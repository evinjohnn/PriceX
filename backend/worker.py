# backend/worker.py

from celery import Celery
import os
from dotenv import load_dotenv
# CORRECTED: Import the new orchestrator function
from scrapers.scraper import sync_process_scrape_task

load_dotenv()

redis_url = os.getenv("UPSTASH_REDIS_URL")

celery_app = Celery('tasks')
celery_app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_connection_retry_on_startup=True
)

@celery_app.task(name="create_scrape_task")
def create_scrape_task(query: str):
    print(f"WORKER: Received job for query: '{query}'")
    # CORRECTED: Call the single, intelligent task function
    sync_process_scrape_task(query)
    return f"Scraping complete for {query}"

print("Celery worker configured with enterprise scraping system.")