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
    """Scrapes Amazon search results using the intelligent proxy system."""
    logger.info(f"Processing Amazon search for: '{query}'")
    
    try:
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        html = scrape_with_proxy(search_url)
        
        if not html:
            logger.error(f"Failed to scrape Amazon search for: {query}")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.select('div[data-component-type="s-search-result"]')
        logger.info(f"Found {len(results)} products on Amazon page.")
        
        products_processed = 0
        for item in results:
            if products_processed >= max_products:
                break
                
            try:
                asin = item.get('data-asin')
                if not asin:
                    continue
                
                title = item.select_one('span.a-text-normal')
                price = item.select_one('.a-price-whole')
                url = item.select_one('a.a-link-normal')
                image = item.select_one('img.s-image')
                
                if not all([title, price, url, image]):
                    continue
                
                # Clean and validate data
                title_text = title.text.strip()
                price_text = clean_text(price.text)
                
                if not title_text or not price_text:
                    continue
                
                try:
                    price_float = float(price_text)
                except ValueError:
                    continue
                
                product_url = f"https://www.amazon.in{url['href']}"
                image_url = image.get('src', '')
                
                # Save to database
                product_id = add_product_if_not_exists(asin, title_text, product_url)
                if product_id:
                    add_price_entry(product_id, price_float, "In Stock", image_url)
                    products_processed += 1
                    logger.info(f"Saved Amazon product: {title_text[:50]}...")
                
            except Exception as e:
                logger.error(f"Error processing Amazon product: {e}")
                continue
        
        logger.info(f"Successfully processed {products_processed} Amazon products")
        
    except ScrapingFailedError as e:
        logger.error(f"Amazon scraping failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in Amazon search: {e}")

def process_flipkart_search(query: str, max_products=5):
    """Scrapes Flipkart search results using the intelligent proxy system."""
    logger.info(f"Processing Flipkart search for: '{query}'")
    
    try:
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        html = scrape_with_proxy(search_url)
        
        if not html:
            logger.error(f"Failed to scrape Flipkart search for: {query}")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Use multiple selectors to handle different page layouts
        product_selectors = [
            'div._1xHGtK._373qXS', 
            'div._4ddWXP', 
            'div.slAVV4', 
            'div._1UoZlX',
            'div._13oc-S',
            'div._3pLy-c'
        ]
        
        results = []
        for selector in product_selectors:
            results = soup.select(selector)
            if results:
                break
        
        logger.info(f"Found {len(results)} products on Flipkart page.")
        
        products_processed = 0
        for item in results:
            if products_processed >= max_products:
                break
                
            try:
                # Try multiple selectors for different elements
                title_selectors = ['a.s1Q9rs', 'a._1fQZEK', 'a.IRpwTa', 'a._2WkVRV', 'div._4rR01T']
                title_element = None
                for selector in title_selectors:
                    title_element = item.select_one(selector)
                    if title_element:
                        break
                
                price_selectors = ['div._30jeq3', 'div._1_WHN1', 'div._3tbHP2']
                price_element = None
                for selector in price_selectors:
                    price_element = item.select_one(selector)
                    if price_element:
                        break
                
                url_selectors = ['a.s1Q9rs', 'a._1fQZEK', 'a.IRpwTa']
                url_element = None
                for selector in url_selectors:
                    url_element = item.select_one(selector)
                    if url_element:
                        break
                
                image_selectors = ['img._396cs4', 'img._2r_T1I', 'img._3exPp9']
                image_element = None
                for selector in image_selectors:
                    image_element = item.select_one(selector)
                    if image_element:
                        break
                
                if not all([title_element, price_element, url_element, image_element]):
                    continue
                
                # Extract and clean data
                title = title_element.get_text(strip=True)
                price_text = clean_text(price_element.get_text(strip=True))
                
                if not title or not price_text:
                    continue
                
                try:
                    price_float = float(price_text)
                except ValueError:
                    continue
                
                product_url = f"https://www.flipkart.com{url_element['href']}"
                image_url = image_element.get('src', '')
                
                # Extract unique ID from URL
                unique_id = product_url.split('?pid=')[1].split('&')[0] if '?pid=' in product_url else product_url
                
                # Save to database
                product_id = add_product_if_not_exists(unique_id, title, product_url)
                if product_id:
                    add_price_entry(product_id, price_float, "In Stock", image_url)
                    products_processed += 1
                    logger.info(f"Saved Flipkart product: {title[:50]}...")
                
            except Exception as e:
                logger.error(f"Error processing Flipkart product: {e}")
                continue
        
        logger.info(f"Successfully processed {products_processed} Flipkart products")
        
    except ScrapingFailedError as e:
        logger.error(f"Flipkart scraping failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in Flipkart search: {e}")