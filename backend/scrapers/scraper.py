import requests
import os
from bs4 import BeautifulSoup
import re
from database import add_product_if_not_exists, add_price_entry

def clean_text(text):
    return re.sub(r'[\s,₹]+', '', text).strip() if text else ""

def scrape_amazon_with_proxy(url: str):
    """Scrapes a URL using the ScrapingBee API."""
    api_key = os.getenv("SCRAPINGBEE_API_KEY")
    params = {
        "api_key": api_key,
        "url": url,
        "render_js": "true", # Tell ScrapingBee to wait for the page to load
        "country_code": "in" # Ensure we get results from Amazon.in
    }
    response = requests.get("https://app.scrapingbee.com/api/v1/", params=params)
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"ScrapingBee failed with status {response.status_code}: {response.text}")
        return None

def process_amazon_search(query: str, max_products=3):
    """Processes the HTML from an Amazon search page."""
    print(f"Processing Amazon search for: {query}")
    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    html = scrape_amazon_with_proxy(search_url)

    if not html:
        return

    soup = BeautifulSoup(html, 'html.parser')
    results = soup.select('div[data-component-type="s-search-result"]')
    print(f"Found {len(results)} potential products on Amazon.")

    for item in results[:max_products]:
        asin = item.get('data-asin')
        if not asin: continue

        title = item.select_one('h2 a.a-link-normal span.a-text-normal')
        price = item.select_one('.a-price-whole')
        url = item.select_one('h2 a.a-link-normal')
        image = item.select_one('img.s-image')

        product_title = title.get_text(strip=True) if title else "N/A"
        product_price = float(clean_text(price.get_text())) if price else 0.0
        product_url = f"https://www.amazon.in{url['href']}" if url else search_url
        image_url = image['src'] if image else ""

        product_id = add_product_if_not_exists(asin, product_title, product_url)
        if product_id:
            add_price_entry(product_id, product_price, "In Stock", image_url)
        
        print(f"Saved product from Amazon: {product_title}")

# TODO: Create a similar process_flipkart_search function