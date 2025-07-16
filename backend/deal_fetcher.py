# backend/deal_fetcher.py

import os
import tweepy
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# The username of the account we want to get tweets from
TARGET_USERNAME = "dealztrendz"

# Initialize the Tweepy client
try:
    bearer_token = os.getenv("X_BEARER_TOKEN")
    if not bearer_token:
        logger.warning("X_BEARER_TOKEN not found. The deals feature will be disabled.")
        client = None
    else:
        client = tweepy.Client(bearer_token)
except Exception as e:
    logger.error(f"Failed to initialize Tweepy client: {e}")
    client = None

def get_deal_posts(limit=10):
    """
    Fetches the latest tweets from the target user.
    """
    if not client:
        return []

    try:
        # First, get the user ID from the username
        user_response = client.get_user(username=TARGET_USERNAME)
        if not user_response.data:
            logger.error(f"Could not find user with username: {TARGET_USERNAME}")
            return []
        
        user_id = user_response.data.id

        # Now, fetch the tweets from that user
        tweets_response = client.get_users_tweets(
            id=user_id,
            max_results=limit,
            tweet_fields=["created_at", "public_metrics"]
        )

        if not tweets_response.data:
            return []

        # Format the tweets into a clean list of dictionaries
        formatted_posts = []
        for tweet in tweets_response.data:
            post = {
                "id": str(tweet.id), # Ensure ID is a string for consistency
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat(),
                "url": f"https://x.com/{TARGET_USERNAME}/status/{tweet.id}",
                "likes": tweet.public_metrics.get('like_count', 0),
                "retweets": tweet.public_metrics.get('retweet_count', 0)
            }
            formatted_posts.append(post)
            
        return formatted_posts

    except Exception as e:
        logger.error(f"An error occurred while fetching tweets: {e}")
        return []

if __name__ == '__main__':
    # For testing this file directly
    posts = get_deal_posts()
    if posts:
        print(f"Successfully fetched {len(posts)} posts.")
        for post in posts:
            print(f"- {post['text'][:50]}...")
    else:
        print("Failed to fetch posts. Check your Bearer Token and the username.")