from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Celery with the same settings as the worker
redis_url = os.getenv("UPSTASH_REDIS_URL")
celery_app = Celery('tasks')
celery_app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_use_ssl={'ssl_cert_reqs': 'CERT_NONE'},
    redis_backend_use_ssl={'ssl_cert_reqs': 'CERT_NONE'}
)

active_jobs = set()

def orchestrator(query: str):
    job_id = query.lower().strip()
    if job_id in active_jobs:
        return
    try:
        active_jobs.add(job_id)
        print(f"API: Sending task for '{query}' to the queue.")
        celery_app.send_task('create_scrape_task', args=[query])
    finally:
        # We will remove the job lock after a timeout to prevent it getting stuck
        # A more robust system would use Celery's task state
        threading.Timer(300, lambda: active_jobs.remove(job_id) if job_id in active_jobs else None).start()

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    orchestrator(query)
    return jsonify({"message": f"Search initiated for '{query}'. Please check back for results."})

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

if __name__ == '__main__':
    from waitress import serve
    print("Starting Flask API server with Waitress...")
    serve(app, host='0.0.0.0', port=8000)