import requests
import os
from bs4 import BeautifulSoup
import re
import time
import random
import logging
from database import add_product_if_not_exists, add_price_entry
from proxy_pool_manager import get_proxy_manager
from utils import get_random_user_agent, get_common_headers, create_proxy_dict, ScrapingFailedError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text):
    return re.sub(r'[^\d.]', '', text).strip() if text else ""

def scrape_with_proxy(url: str, max_retries: int = 5) -> str:
    """
    Scrapes a URL using the intelligent proxy management system.
    
    Args:
        url: URL to scrape
        max_retries: Maximum number of retry attempts
        
    Returns:
        HTML content as string
        
    Raises:
        ScrapingFailedError: If all retries fail
    """
    proxy_manager = get_proxy_manager()
    
    for attempt in range(max_retries):
        proxy = None
        try:
            # Get a proxy from the pool
            proxy = proxy_manager.get_proxy()
            if not proxy:
                logger.warning(f"No proxy available for attempt {attempt + 1}/{max_retries}")
                time.sleep(random.uniform(1, 3))
                continue
            
            # Get headers with random user agent
            headers = get_common_headers()
            
            # Configure proxy for requests
            proxy_dict = create_proxy_dict(proxy)
            
            logger.debug(f"Attempt {attempt + 1}/{max_retries}: Using proxy {proxy}")
            
            # Make the request
            response = requests.get(
                url,
                proxies=proxy_dict,
                headers=headers,
                timeout=15,
                verify=False  # Skip SSL verification for proxy requests
            )
            
            # Check if request was successful
            if response.status_code == 200:
                # Return proxy to pool for reuse
                proxy_manager.return_proxy(proxy)
                logger.debug(f"Successfully scraped {url} using proxy {proxy}")
                return response.text
            else:
                # Non-200 status code, report proxy as failed
                logger.warning(f"HTTP {response.status_code} from {url} using proxy {proxy}")
                proxy_manager.report_failed_proxy(proxy)
                
        except requests.exceptions.ProxyError as e:
            logger.warning(f"Proxy error with {proxy}: {e}")
            if proxy:
                proxy_manager.report_failed_proxy(proxy)
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout with proxy {proxy}: {e}")
            if proxy:
                proxy_manager.report_failed_proxy(proxy)
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error with proxy {proxy}: {e}")
            if proxy:
                proxy_manager.report_failed_proxy(proxy)
        except Exception as e:
            logger.error(f"Unexpected error with proxy {proxy}: {e}")
            if proxy:
                proxy_manager.report_failed_proxy(proxy)
        
        # Add delay between retries
        if attempt < max_retries - 1:
            delay = random.uniform(1, 3) * (attempt + 1)  # Exponential backoff
            logger.info(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
    
    # All retries failed
    raise ScrapingFailedError(f"Failed to scrape {url} after {max_retries} attempts")

def process_amazon_search(query: str, max_products=5):
    """Scrapes Amazon search results using the new robust method."""
    print(f"Processing Amazon search for: '{query}'")
    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    html = scrape_with_proxy(search_url)
    if not html: return

    soup = BeautifulSoup(html, 'html.parser')
    results = soup.select('div[data-component-type="s-search-result"]')
    print(f"Found {len(results)} products on Amazon page.")

    for item in results[:max_products]:
        asin = item.get('data-asin')
        if not asin: continue

        title = item.select_one('span.a-text-normal')
        price = item.select_one('.a-price-whole')
        url = item.select_one('a.a-link-normal')
        image = item.select_one('img.s-image')

        if not all([title, price, url, image]): continue

        product_id = add_product_if_not_exists(asin, title.text, f"https://www.amazon.in{url['href']}")
        if product_id:
            add_price_entry(product_id, float(clean_text(price.text)), "In Stock", image['src'])
        print(f"Saved from Amazon: {title.text[:30]}...")

def process_flipkart_search(query: str, max_products=5):
    """Scrapes Flipkart search results using logic inspired by the repository."""
    print(f"Processing Flipkart search for: '{query}'")
    search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    html = scrape_with_proxy(search_url)
    if not html: return

    soup = BeautifulSoup(html, 'html.parser')
    
    # Use a list of potential selectors from the provided repository
    product_selectors = ['div._1xHGtK._373qXS', 'div._4ddWXP', 'div.slAVV4', 'div._1UoZlX']
    results = []
    for selector in product_selectors:
        results = soup.select(selector)
        if results:
            break
    
    print(f"Found {len(results)} products on Flipkart page.")

    for item in results[:max_products]:
        title_element = item.select_one('a.s1Q9rs, ._4rR01T, a.IRpwTa, ._2WkVRV')
        price_element = item.select_one('div._30jeq3')
        url_element = item.select_one('a.s1Q9rs, a._1fQZEK, a.IRpwTa')
        image_element = item.select_one('img._396cs4')

        if not all([title_element, price_element, url_element, image_element]):
            continue

        title = title_element.get_text(strip=True)
        price = float(clean_text(price_element.get_text(strip=True)))
        product_url = f"https://www.flipkart.com{url_element['href']}"
        image_url = image_element['src']
        unique_id = product_url.split('?pid=')[1].split('&')[0] if '?pid=' in product_url else product_url

        product_id = add_product_if_not_exists(unique_id, title, product_url)
        if product_id:
            add_price_entry(product_id, price, "In Stock", image_url)
        print(f"Saved from Flipkart: {title[:30]}...")