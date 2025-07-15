"""
Enterprise-Grade Web Scraping System with Multi-Tiered Anti-Blocking Architecture

This module implements a sophisticated, resilient web scraping system with:
- Tier 1: Stealth Playwright browser automation (primary)
- Tier 2: AWS Lambda serverless IP rotation (fallback)
- Tier 3: Automated CAPTCHA solving (final escalation)

The system provides enterprise-grade reliability for scraping e-commerce sites
like Amazon and Flipkart with advanced anti-detection capabilities.
"""
import asyncio
import json
import logging
import random
import time
import requests
from typing import Optional, Dict, Any, List
import boto3
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
import re
class ScrapingError(Exception):
    """Base exception for scraping errors."""
    pass

class BlockedError(ScrapingError):
    """Raised when scraping is blocked."""
    pass

class CaptchaError(ScrapingError):
    """Raised when CAPTCHA is encountered."""
    pass

class EnterpriseScrapingSystem:
    """
    Enterprise-grade scraping system with multi-tiered anti-blocking architecture.
    """
    
    def __init__(self):
        """Initialize the scraping system."""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.aws_client = None
        
        # Initialize AWS client if configured
        if config.is_aws_configured():
            self.aws_client = boto3.client(
                'lambda',
                region_name=config.AWS_REGION,
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
            )
            logger.info("AWS Lambda client initialized")
        else:
            logger.warning("AWS not configured. Tier 2 fallback will be disabled.")
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing non-numeric characters."""
        return re.sub(r'[^\d.]', '', text).strip() if text else ""

    async def initialize_browser(self) -> None:
        """Initialize Playwright browser with stealth settings."""
        try:
            logger.info("Initializing stealth browser...")
            
            playwright = await async_playwright().start()
            
            # Get random configuration
            viewport = config.get_random_viewport()
            user_agent = config.get_random_user_agent()
            locale = config.get_random_locale()
            timezone = config.get_random_timezone()
            
            # Launch browser with stealth settings
            self.browser = await playwright.chromium.launch(
                headless=config.BROWSER_HEADLESS,
                slow_mo=config.BROWSER_SLOW_MO,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-translate',
                    '--disable-logging',
                    '--disable-permissions-api',
                    '--disable-notifications',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-background-networking',
                    '--disable-component-update',
                    '--disable-client-side-phishing-detection',
                    '--disable-hang-monitor',
                    '--disable-popup-blocking',
                    '--disable-prompt-on-repost',
                    '--disable-domain-reliability',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-ipc-flooding-protection',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-features=TranslateUI',
                    '--disable-features=BlinkGenPropertyTrees',
                    '--disable-field-trial-config',
                    '--disable-back-forward-cache',
                    '--disable-features=AutomationControlled',
                    '--exclude-switches=enable-automation',
                    '--use-mock-keychain',
                    '--disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate',
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                viewport=viewport,
                user_agent=user_agent,
                locale=locale,
                timezone_id=timezone,
                permissions=["geolocation"],
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Cache-Control": "max-age=0",
                    "DNT": "1",
                    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"'
                }
            )
            
            logger.info(f"Browser initialized with viewport {viewport['width']}x{viewport['height']}, locale {locale}")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise ScrapingError(f"Browser initialization failed: {e}")

    async def get_page_content_tier1(self, url: str) -> Optional[str]:
        """
        Tier 1: Get page content using stealth Playwright (primary method).
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Tier 1: Scraping {url} with stealth browser")
            
            if not self.context:
                await self.initialize_browser()
            
            # Create new page
            page = await self.context.new_page()
            
            # Apply stealth settings
            await stealth_async(page)
            
            # Add random delay before request
            await asyncio.sleep(random.uniform(config.MIN_REQUEST_DELAY, config.MAX_REQUEST_DELAY))
            
            # Navigate to URL
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=config.PAGE_LOAD_TIMEOUT * 1000
            )
            
            if not response:
                raise ScrapingError("Failed to load page")
            
            # Wait for page to fully load
            await page.wait_for_load_state("networkidle", timeout=config.NAVIGATION_TIMEOUT * 1000)
            
            # Check for blocking indicators
            html_content = await page.content()
            if self._is_blocked(html_content):
                logger.warning("Tier 1: Page appears to be blocked")
                await page.close()
                raise BlockedError("Page blocked by anti-bot measures")
            
            # Check for CAPTCHA
            if captcha_solver.is_configured():
                captcha_detected = await captcha_solver.detect_captcha(page)
                if captcha_detected:
                    logger.info("Tier 1: CAPTCHA detected, attempting to solve...")
                    if await captcha_solver.solve_captcha_on_page(page):
                        logger.info("Tier 1: CAPTCHA solved successfully")
                        # Get updated content after CAPTCHA solving
                        html_content = await page.content()
                    else:
                        logger.error("Tier 1: Failed to solve CAPTCHA")
                        await page.close()
                        raise CaptchaError("CAPTCHA solving failed")
            
            await page.close()
            
            logger.info(f"Tier 1: Successfully scraped {url} ({len(html_content)} chars)")
            return html_content
            
        except (BlockedError, CaptchaError):
            raise  # Re-raise these specific errors
        except Exception as e:
            logger.error(f"Tier 1: Error scraping {url}: {e}")
            return None

    async def get_page_content_tier2(self, url: str) -> Optional[str]:
        """
        Tier 2: Get page content using AWS Lambda (fallback method).
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Tier 2: Scraping {url} with AWS Lambda")
            
            if not self.aws_client:
                logger.error("Tier 2: AWS client not configured")
                return None
            
            # Prepare Lambda payload
            payload = {
                "url": url,
                "wait_for_selector": None
            }
            
            # Invoke Lambda function
            response = self.aws_client.invoke(
                FunctionName=config.AWS_LAMBDA_FUNCTION_NAME,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Parse response
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                result = json.loads(response_payload['body'])
                
                if result.get('success'):
                    html_content = result.get('html_content')
                    
                    if self._is_blocked(html_content):
                        logger.warning("Tier 2: Page appears to be blocked")
                        raise BlockedError("Page blocked by anti-bot measures")
                    
                    logger.info(f"Tier 2: Successfully scraped {url} ({len(html_content)} chars)")
                    return html_content
                else:
                    logger.error(f"Tier 2: Lambda scraping failed: {result.get('error')}")
                    return None
            else:
                logger.error(f"Tier 2: Lambda invocation failed: {response_payload}")
                return None
                
        except Exception as e:
            logger.error(f"Tier 2: Error scraping {url}: {e}")
            return None

    def _is_blocked(self, html_content: str) -> bool:
        """Check if page content indicates blocking."""
        if not html_content:
            return True
        
        blocking_indicators = [
            "captcha",
            "blocked",
            "access denied",
            "forbidden",
            "rate limit",
            "security check",
            "unusual traffic",
            "automated queries",
            "robot",
            "bot detection",
            "please verify",
            "temporarily blocked",
            "suspicious activity"
        ]
        
        content_lower = html_content.lower()
        return any(indicator in content_lower for indicator in blocking_indicators)

    async def get_page_content_resiliently(self, url: str) -> str:
        """
        Get page content using multi-tiered resilient approach.
        
        Args:
            url: URL to scrape
            
        Returns:
            HTML content
            
        Raises:
            ScrapingError: If all tiers fail
        """
        last_error = None
        
        for attempt in range(config.MAX_RETRY_ATTEMPTS):
            try:
                logger.info(f"Resilient scraping attempt {attempt + 1}/{config.MAX_RETRY_ATTEMPTS} for {url}")
                
                # Tier 1: Stealth Browser (Primary)
                try:
                    html_content = await self.get_page_content_tier1(url)
                    if html_content:
                        return html_content
                except (BlockedError, CaptchaError) as e:
                    logger.warning(f"Tier 1 failed: {e}")
                    last_error = e
                
                # Tier 2: AWS Lambda (Fallback)
                if self.aws_client:
                    try:
                        html_content = await self.get_page_content_tier2(url)
                        if html_content:
                            return html_content
                    except Exception as e:
                        logger.warning(f"Tier 2 failed: {e}")
                        last_error = e
                
                # If we get here, both tiers failed
                if attempt < config.MAX_RETRY_ATTEMPTS - 1:
                    delay = min(config.RETRY_DELAY_BASE ** (attempt + 1), config.RETRY_DELAY_MAX)
                    logger.info(f"All tiers failed, retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Unexpected error in resilient scraping: {e}")
                last_error = e
                
                if attempt < config.MAX_RETRY_ATTEMPTS - 1:
                    delay = min(config.RETRY_DELAY_BASE ** (attempt + 1), config.RETRY_DELAY_MAX)
                    await asyncio.sleep(delay)
        
        # All attempts failed
        error_msg = f"Failed to scrape {url} after {config.MAX_RETRY_ATTEMPTS} attempts"
        if last_error:
            error_msg += f". Last error: {last_error}"
        
        raise ScrapingError(error_msg)

    async def close(self) -> None:
        """Clean up browser resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

# Global scraper instance
enterprise_scraper = EnterpriseScrapingSystem()

from database import add_product_if_not_exists, add_price_entry
from config import config
from captcha_solver import captcha_solver
from proxy_pool_manager import get_proxy_manager
from utils import get_random_user_agent, get_common_headers, create_proxy_dict, ScrapingFailedError

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
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