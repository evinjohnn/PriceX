# backend/scrapers/scraper.py

import requests
import logging
import re
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os
from dotenv import load_dotenv

from database import add_product_if_not_exists, add_price_entry

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ScraperAPI configuration
SCRAPER_API_KEY = os.getenv('SCRAPER_API_KEY', 'demo_key')
SCRAPER_API_URL = 'http://api.scraperapi.com'

class SimplifiedScraper:
    """
    Simplified scraping system using ScraperAPI for reliability.
    """
    
    def __init__(self):
        self.api_key = SCRAPER_API_KEY
        self.base_url = SCRAPER_API_URL
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing non-numeric characters."""
        return re.sub(r'[^\d.]', '', text).strip() if text else ""
    
    def get_page_content(self, url: str) -> Optional[str]:
        """
        Get page content using ScraperAPI.
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Scraping {url} with ScraperAPI")
            
            params = {
                'api_key': self.api_key,
                'url': url,
                'render': 'true',  # Enable JavaScript rendering
                'country_code': 'in',  # Use Indian IP for better results
                'device_type': 'desktop'
            }
            
            response = requests.get(self.base_url, params=params, timeout=60)
            response.raise_for_status()
            
            logger.info(f"Successfully scraped {url} ({len(response.text)} chars)")
            return response.text
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def is_url(self, string: str) -> bool:
        """Checks if a string is a valid URL."""
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    
    def get_platform_from_url(self, url: str) -> Optional[str]:
        """Determines the platform (amazon or flipkart) from a URL."""
        if 'amazon' in url.lower():
            return 'amazon'
        if 'flipkart' in url.lower():
            return 'flipkart'
        return None

# Global scraper instance
scraper = SimplifiedScraper()

def process_amazon_search(query: str, max_products: int = 5):
    """Process Amazon search results."""
    logger.info(f"Processing Amazon search for: '{query}'")
    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    
    try:
        html = scraper.get_page_content(search_url)
        if not html:
            logger.warning(f"Failed to get HTML content for Amazon search: {query}")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Amazon product selectors
        results = soup.select('[data-component-type="s-search-result"]')
        
        if not results:
            logger.warning(f"No search results found on Amazon for '{query}'")
            return
        
        logger.info(f"Found {len(results)} potential products on Amazon")
        
        products_processed = 0
        for item in results:
            if products_processed >= max_products:
                break
                
            try:
                # Extract ASIN
                asin = item.get('data-asin')
                if not asin:
                    continue
                
                # Extract title
                title_el = item.select_one('h2 a span')
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                
                # Extract price
                price_el = item.select_one('.a-price-whole')
                if not price_el:
                    continue
                price_text = scraper.clean_text(price_el.get_text(strip=True))
                if not price_text:
                    continue
                
                # Extract product URL
                url_el = item.select_one('h2 a')
                if not url_el:
                    continue
                product_url = urljoin('https://www.amazon.in', url_el.get('href', ''))
                
                # Extract image
                image_el = item.select_one('img')
                image_url = image_el.get('src', '') if image_el else ''
                
                # Save to database
                try:
                    price_float = float(price_text)
                    product_id = add_product_if_not_exists(asin, title, product_url)
                    if product_id:
                        add_price_entry(product_id, price_float, "In Stock", image_url)
                        products_processed += 1
                        logger.info(f"Saved Amazon product: {title[:50]}...")
                except ValueError:
                    logger.warning(f"Invalid price format: {price_text}")
                    continue
                    
            except Exception as e:
                logger.error(f"Error processing Amazon product: {e}")
                continue
        
        logger.info(f"Successfully processed {products_processed} Amazon products")
        
    except Exception as e:
        logger.error(f"Amazon scraping failed for query '{query}': {e}")

def process_flipkart_search(query: str, max_products: int = 5):
    """Process Flipkart search results."""
    logger.info(f"Processing Flipkart search for: '{query}'")
    search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    
    try:
        html = scraper.get_page_content(search_url)
        if not html:
            logger.warning(f"Failed to get HTML content for Flipkart search: {query}")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Flipkart product selectors
        results = soup.select('[data-id]')
        
        if not results:
            logger.warning(f"No search results found on Flipkart for '{query}'")
            return
        
        logger.info(f"Found {len(results)} potential products on Flipkart")
        
        products_processed = 0
        for item in results:
            if products_processed >= max_products:
                break
                
            try:
                # Extract product ID
                product_id = item.get('data-id')
                if not product_id:
                    continue
                
                # Extract title
                title_el = item.select_one('a[title]')
                if not title_el:
                    continue
                title = title_el.get('title', '').strip()
                
                # Extract price
                price_el = item.select_one('div[class*="price"]')
                if not price_el:
                    continue
                price_text = scraper.clean_text(price_el.get_text(strip=True))
                if not price_text:
                    continue
                
                # Extract product URL
                url_el = item.select_one('a[href]')
                if not url_el:
                    continue
                product_url = urljoin('https://www.flipkart.com', url_el.get('href', ''))
                
                # Extract image
                image_el = item.select_one('img')
                image_url = image_el.get('src', '') if image_el else ''
                
                # Save to database
                try:
                    price_float = float(price_text)
                    db_product_id = add_product_if_not_exists(product_id, title, product_url)
                    if db_product_id:
                        add_price_entry(db_product_id, price_float, "In Stock", image_url)
                        products_processed += 1
                        logger.info(f"Saved Flipkart product: {title[:50]}...")
                except ValueError:
                    logger.warning(f"Invalid price format: {price_text}")
                    continue
                    
            except Exception as e:
                logger.error(f"Error processing Flipkart product: {e}")
                continue
        
        logger.info(f"Successfully processed {products_processed} Flipkart products")
        
    except Exception as e:
        logger.error(f"Flipkart scraping failed for query '{query}': {e}")

def process_single_product_page(url: str, platform: str):
    """Process a single product page."""
    logger.info(f"Processing single product page for platform '{platform}': {url}")
    
    try:
        html = scraper.get_page_content(url)
        if not html:
            logger.warning(f"Failed to get HTML content for URL: {url}")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        if platform == 'amazon':
            # Amazon product page selectors
            title_el = soup.select_one('#productTitle')
            price_el = soup.select_one('.a-price-whole')
            image_el = soup.select_one('#landingImage')
            
            # Extract ASIN from URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            asin = asin_match.group(1) if asin_match else None
            
            if not all([title_el, price_el, image_el, asin]):
                logger.error("Could not extract all required fields from Amazon product page")
                return
            
            title = title_el.get_text(strip=True)
            price_text = scraper.clean_text(price_el.get_text(strip=True))
            image_url = image_el.get('src', '')
            unique_id = asin
            
        elif platform == 'flipkart':
            # Flipkart product page selectors
            title_el = soup.select_one('span.B_NuCI')
            price_el = soup.select_one('div._30jeq3._16Jk6d')
            image_el = soup.select_one('img._396cs4._2amPTt._3qGmMb')
            
            # Extract product ID from URL
            pid_match = re.search(r'pid=([A-Z0-9]+)', url)
            unique_id = pid_match.group(1) if pid_match else url
            
            if not all([title_el, price_el, image_el]):
                logger.error("Could not extract all required fields from Flipkart product page")
                return
            
            title = title_el.get_text(strip=True)
            price_text = scraper.clean_text(price_el.get_text(strip=True))
            image_url = image_el.get('src', '')
            
        else:
            logger.warning(f"Unsupported platform: {platform}")
            return
        
        # Save to database
        try:
            price_float = float(price_text)
            product_id = add_product_if_not_exists(unique_id, title, url)
            if product_id:
                add_price_entry(product_id, price_float, "In Stock", image_url)
                logger.info(f"Saved single product: {title[:50]}...")
        except ValueError:
            logger.warning(f"Invalid price format: {price_text}")
            
    except Exception as e:
        logger.error(f"Error processing single product page {url}: {e}")

def process_scrape_task(query: str):
    """Main task orchestrator."""
    logger.info(f"Processing scrape task for: '{query}'")
    
    if scraper.is_url(query):
        # Handle single product URL
        platform = scraper.get_platform_from_url(query)
        if platform:
            process_single_product_page(query, platform)
        else:
            logger.warning(f"Unsupported platform URL: {query}")
    else:
        # Handle search query - process both platforms
        try:
            process_amazon_search(query)
            process_flipkart_search(query)
        except Exception as e:
            logger.error(f"Error in search processing: {e}")

def sync_process_scrape_task(query: str):
    """Synchronous wrapper for the main scrape task orchestrator."""
    try:
        process_scrape_task(query)
    except Exception as e:
        logger.error(f"Error in sync wrapper for query '{query}': {e}")