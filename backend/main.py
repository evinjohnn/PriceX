from flask import Flask, request, jsonify
from flask_cors import CORS
from scrapers.scraper import process_amazon_search
from database import get_results_by_query
import threading

app = Flask(__name__)
CORS(app)
active_jobs = set()

def orchestrator(query: str):
    job_id = query.lower().strip()
    if job_id in active_jobs:
        print(f"Job for query '{query}' is already running.")
        return
    try:
        active_jobs.add(job_id)
        print(f"Orchestrator started for: '{query}'")
        process_amazon_search(query)
        # TODO: process_flipkart_search(query)
    finally:
        print(f"Orchestrator finished for: '{query}'")
        active_jobs.remove(job_id)

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    thread = threading.Thread(target=orchestrator, args=(query,))
    thread.start()
    return jsonify({"message": f"Search initiated for '{query}'. Results will appear shortly."})

@app.route('/results', methods=['GET'])
def get_results():
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
    print("Starting Flask server with Waitress...")
    serve(app, host='0.0.0.0', port=8000)