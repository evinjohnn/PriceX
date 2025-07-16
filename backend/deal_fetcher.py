# backend/deal_fetcher.py

import tweepy
import logging
import re
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import json
import requests
from urllib.parse import urlparse

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twitter API configuration
X_BEARER_TOKEN = os.getenv('X_BEARER_TOKEN', 'demo_bearer_token')

class DealFetcher:
    """
    Fetches deals from @dealztrends Twitter account with enhanced data extraction.
    """
    
    def __init__(self):
        self.client = tweepy.Client(bearer_token=X_BEARER_TOKEN)
        self.target_username = 'dealztrendz'
    
    def extract_price_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract price and discount information from tweet text.
        
        Args:
            text: Tweet text
            
        Returns:
            Dictionary containing price, discount, and product info
        """
        price_patterns = [
            r'₹[\d,]+',  # Indian Rupees
            r'\$[\d,]+',  # US Dollars
            r'Rs\.?\s*[\d,]+',  # Rs format
            r'Price:\s*₹[\d,]+',  # Price: ₹xxx
            r'Now:\s*₹[\d,]+',  # Now: ₹xxx
        ]
        
        discount_patterns = [
            r'(\d+)%\s*off',  # XX% off
            r'(\d+)%\s*discount',  # XX% discount
            r'Save\s*₹[\d,]+',  # Save ₹xxx
            r'Was\s*₹[\d,]+',  # Was ₹xxx
        ]
        
        # Extract price
        price = None
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price = match.group(0)
                break
        
        # Extract discount
        discount = None
        for pattern in discount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                discount = match.group(0)
                break
        
        # Extract product name (heuristic approach)
        product_name = self._extract_product_name(text)
        
        return {
            'price': price,
            'discount': discount,
            'product_name': product_name
        }
    
    def _extract_product_name(self, text: str) -> Optional[str]:
        """
        Extract product name from tweet text using heuristics.
        
        Args:
            text: Tweet text
            
        Returns:
            Extracted product name or None
        """
        # Remove URLs, mentions, hashtags
        clean_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        clean_text = re.sub(r'@\w+', '', clean_text)
        clean_text = re.sub(r'#\w+', '', clean_text)
        
        # Split into lines and find the first meaningful line
        lines = clean_text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not line.startswith('₹') and not line.startswith('Price'):
                # Remove common deal-related words
                deal_words = ['deal', 'offer', 'discount', 'off', 'save', 'flash', 'sale']
                words = line.split()
                filtered_words = [word for word in words if word.lower() not in deal_words]
                if len(filtered_words) >= 2:
                    return ' '.join(filtered_words[:8])  # Take first 8 words
        
        return None
    
    def extract_deal_url(self, text: str) -> Optional[str]:
        """
        Extract deal URL from tweet text.
        
        Args:
            text: Tweet text
            
        Returns:
            Deal URL or None
        """
        # Look for URLs in the text
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        # Filter for shopping URLs
        shopping_domains = ['amazon', 'flipkart', 'myntra', 'snapdeal', 'paytm', 'shopclues']
        for url in urls:
            if any(domain in url.lower() for domain in shopping_domains):
                return url
        
        # Return first URL if no shopping URL found
        return urls[0] if urls else None
    
    def get_image_url_from_media(self, media_list: List) -> Optional[str]:
        """
        Extract image URL from tweet media.
        
        Args:
            media_list: List of media objects from tweet
            
        Returns:
            Image URL or None
        """
        if not media_list:
            return None
        
        for media in media_list:
            if media.type == 'photo':
                return media.url
        
        return None
    
    def fetch_deals(self, count: int = 20) -> List[Dict]:
        """
        Fetch recent deals from @dealztrends account.
        
        Args:
            count: Number of deals to fetch
            
        Returns:
            List of deal dictionaries
        """
        try:
            logger.info(f"Fetching {count} deals from @{self.target_username}")
            
            # Get user ID
            user = self.client.get_user(username=self.target_username)
            if not user.data:
                logger.error(f"User @{self.target_username} not found")
                return []
            
            user_id = user.data.id
            
            # Fetch tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=count,
                tweet_fields=['created_at', 'public_metrics', 'attachments'],
                media_fields=['url', 'type'],
                expansions=['attachments.media_keys']
            )
            
            if not tweets.data:
                logger.warning("No tweets found")
                return []
            
            # Process tweets
            deals = []
            media_dict = {}
            
            # Create media dictionary if includes exist
            if tweets.includes and 'media' in tweets.includes:
                for media in tweets.includes['media']:
                    media_dict[media.media_key] = media
            
            for tweet in tweets.data:
                try:
                    # Extract deal information
                    price_info = self.extract_price_info(tweet.text)
                    deal_url = self.extract_deal_url(tweet.text)
                    
                    # Get image URL
                    image_url = None
                    if tweet.attachments and 'media_keys' in tweet.attachments:
                        for media_key in tweet.attachments['media_keys']:
                            if media_key in media_dict:
                                media_obj = media_dict[media_key]
                                if media_obj.type == 'photo':
                                    image_url = media_obj.url
                                    break
                    
                    # Create deal object
                    deal = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'url': deal_url,
                        'likes': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                        'retweets': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                        'price': price_info['price'],
                        'discount': price_info['discount'],
                        'product_name': price_info['product_name'],
                        'image_url': image_url
                    }
                    
                    deals.append(deal)
                    
                except Exception as e:
                    logger.error(f"Error processing tweet {tweet.id}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(deals)} deals")
            return deals
            
        except Exception as e:
            logger.error(f"Error fetching deals: {e}")
            return []

# Global deal fetcher instance
deal_fetcher = DealFetcher()

def get_latest_deals(count: int = 20) -> List[Dict]:
    """
    Get latest deals from @dealztrends.
    
    Args:
        count: Number of deals to fetch
        
    Returns:
        List of deal dictionaries
    """
    return deal_fetcher.fetch_deals(count)