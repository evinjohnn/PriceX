from celery import Celery
import os
from dotenv import load_dotenv
from scrapers.scraper import process_amazon_search, process_flipkart_search

load_dotenv()

# The rediss:// scheme in the URL is enough to handle SSL automatically
redis_url = os.getenv("UPSTASH_REDIS_URL")

celery_app = Celery(
    'tasks',
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(broker_connection_retry_on_startup=True)

@celery_app.task(name="create_scrape_task")
def create_scrape_task(query: str):
    print(f"WORKER: Received job for query: '{query}'")
    process_amazon_search(query)
    process_flipkart_search(query)
    return f"Scraping complete for {query}"

print("Celery worker configured.")