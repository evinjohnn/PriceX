# backend/main.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
import os
from dotenv import load_dotenv
import threading
from deal_fetcher import get_latest_deals
from functools import lru_cache
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
CORS(app)

# This configuration is for your local Redis instance.
redis_url = os.getenv("UPSTASH_REDIS_URL")
celery_app = Celery('tasks')
celery_app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_connection_retry_on_startup=True
)

active_jobs = set()

def orchestrator(query: str):
    job_id = query.lower().strip()
    if job_id in active_jobs:
        return
    try:
        active_jobs.add(job_id)
        print(f"API: Sending task for '{query}' to the queue.")
        # This sends the task to the worker, which handles the scraping logic.
        celery_app.send_task('create_scrape_task', args=[query])
    finally:
        threading.Timer(600, lambda: active_jobs.remove(job_id) if job_id in active_jobs else None).start()

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    orchestrator(query)
    return jsonify({"message": f"Search initiated for '{query}'. Results will appear shortly."})

@app.route('/results', methods=['GET'])
def get_results():
    from database import get_results_by_query
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    scraped_data = get_results_by_query(query)
    if scraped_data.get("amazon") or scraped_data.get("flipkart"):
        return jsonify(scraped_data)
    else:
        return jsonify({"status": "pending"}), 202

# Cache for deals to avoid hitting Twitter API too frequently
deals_cache = {
    'data': None,
    'timestamp': None,
    'ttl': 300  # 5 minutes cache
}

@lru_cache(maxsize=1)
def get_cached_deals():
    """Get cached deals with LRU cache."""
    return get_latest_deals(30)

@app.route('/api/deals', methods=['GET'])
def get_deals():
    """Get latest deals from @dealztrends with caching."""
    try:
        current_time = datetime.now()
        
        # Check if cache is valid
        if (deals_cache['data'] is not None and 
            deals_cache['timestamp'] is not None and 
            current_time - deals_cache['timestamp'] < timedelta(seconds=deals_cache['ttl'])):
            return jsonify(deals_cache['data'])
        
        # Fetch fresh data
        fresh_deals = get_latest_deals(30)
        
        # Update cache
        deals_cache['data'] = fresh_deals
        deals_cache['timestamp'] = current_time
        
        return jsonify(fresh_deals)
        
    except Exception as e:
        print(f"Error fetching deals: {e}")
        # Return cached data if available, otherwise empty array
        if deals_cache['data'] is not None:
            return jsonify(deals_cache['data'])
        return jsonify([])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    from waitress import serve
    print("Starting Flask API server with Waitress...")
    serve(app, host='0.0.0.0', port=8001)