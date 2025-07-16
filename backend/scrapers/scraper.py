# backend/scrapers/scraper.py

import asyncio
import json
import logging
import random
import time
import requests
from typing import Optional, Dict, Any, List
import boto3
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
# CORRECTED: Importing the 'stealth' function directly.
from playwright_stealth import stealth
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

from config import config
from captcha_solver import captcha_solver
from database import add_product_if_not_exists, add_price_entry

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class ScrapingError(Exception):
    pass

class BlockedError(ScrapingError):
    pass

class CaptchaError(ScrapingError):
    pass

# --- Helper function to identify input type ---
def is_url(string: str) -> bool:
    """Checks if a string is a valid URL."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_platform_from_url(url: str) -> Optional[str]:
    """Determines the platform (amazon or flipkart) from a URL."""
    if 'amazon' in url:
        return 'amazon'
    if 'flipkart' in url:
        return 'flipkart'
    return None

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
            
            # CORRECTED FUNCTION CALL
            await stealth(page)
            
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

enterprise_scraper = EnterpriseScrapingSystem()

# --- NEW: Logic to handle a single product page ---
async def process_single_product_page(url: str, platform: str):
    logger.info(f"Processing single product page for platform '{platform}': {url}")
    try:
        html = await enterprise_scraper.get_page_content_resiliently(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # This is a simplified example; selectors for single product pages are often different
        # from search result pages. For now, we'll assume they are similar or reuse some.
        # A robust solution would have dedicated selectors in config.py for product pages.
        
        if platform == 'amazon':
            # Example selectors for an Amazon product page
            title_el = soup.select_one('#productTitle')
            price_el = soup.select_one('.a-price-whole')
            image_el = soup.select_one('#landingImage')
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            asin = asin_match.group(1) if asin_match else None
            
            if not all([title_el, price_el, image_el, asin]):
                logger.error("Could not extract all required fields from Amazon product page.")
                return

            title = title_el.text.strip()
            price = enterprise_scraper.clean_text(price_el.text)
            image_url = image_el.get('src')
            
        elif platform == 'flipkart':
            # Example selectors for a Flipkart product page
            title_el = soup.select_one('span.B_NuCI')
            price_el = soup.select_one('div._30jeq3._16Jk6d')
            image_el = soup.select_one('img._396cs4._2amPTt._3qGmMb')
            pid_match = re.search(r'pid=([A-Z0-9]+)', url)
            unique_id = pid_match.group(1) if pid_match else url
            
            if not all([title_el, price_el, image_el]):
                logger.error("Could not extract all required fields from Flipkart product page.")
                return

            title = title_el.text.strip()
            price = enterprise_scraper.clean_text(price_el.text)
            image_url = image_el.get('src')
            
        else:
            return

        price_float = float(price)
        product_id = add_product_if_not_exists(asin or unique_id, title, url)
        if product_id:
            add_price_entry(product_id, price_float, "In Stock", image_url)
            logger.info(f"Saved single product: {title[:50]}...")

    except Exception as e:
        logger.error(f"Error processing single product page {url}: {e}", exc_info=True)
    finally:
        await enterprise_scraper.close()

# --- MODIFIED: Search processing functions ---
async def process_amazon_search(query: str, max_products: int = 5):
    logger.info(f"Processing Amazon search for: '{query}'")
    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    try:
        html = await enterprise_scraper.get_page_content_resiliently(search_url)
        soup = BeautifulSoup(html, 'html.parser')
        selectors = config.get_site_selectors('amazon')
        results = soup.select(selectors['search_results'])
        
        if not results:
            logger.warning(f"No search results found on Amazon for '{query}'. The page might be blocked or selectors are outdated.")
            return

        logger.info(f"Found {len(results)} potential products on Amazon page.")
        
        products_processed = 0
        for item in results:
            if products_processed >= max_products: break
            try:
                asin = item.get('data-asin')
                if not asin: continue
                
                title_el = item.select_one(selectors['title'])
                price_el = item.select_one(selectors['price'])
                url_el = item.select_one(selectors['url'])
                image_el = item.select_one(selectors['image'])
                
                if not all([title_el, price_el, url_el, image_el]): continue
                
                title_text = title_el.text.strip()
                price_text = enterprise_scraper.clean_text(price_el.text)
                if not title_text or not price_text: continue
                
                price_float = float(price_text)
                product_url = f"https://www.amazon.in{url_el['href']}"
                image_url = image_el.get('src', '')
                
                product_id = add_product_if_not_exists(asin, title_text, product_url)
                if product_id:
                    add_price_entry(product_id, price_float, "In Stock", image_url)
                    products_processed += 1
                    logger.info(f"Saved Amazon product: {title_text[:50]}...")
            except Exception as e:
                logger.error(f"Error processing an Amazon product item: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully processed {products_processed} Amazon products.")
    except Exception as e:
        logger.error(f"Amazon scraping failed for query '{query}': {e}", exc_info=True)
    finally:
        await enterprise_scraper.close()

async def process_flipkart_search(query: str, max_products: int = 5):
    logger.info(f"Processing Flipkart search for: '{query}'")
    search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    try:
        html = await enterprise_scraper.get_page_content_resiliently(search_url)
        soup = BeautifulSoup(html, 'html.parser')
        selectors = config.get_site_selectors('flipkart')
        
        results = []
        for selector in selectors['search_results']:
            results = soup.select(selector)
            if results: break
        
        if not results:
            logger.warning(f"No search results found on Flipkart for '{query}'. The page might be blocked or selectors are outdated.")
            return

        logger.info(f"Found {len(results)} potential products on Flipkart page.")
        
        products_processed = 0
        for item in results:
            if products_processed >= max_products: break
            try:
                title_el, price_el, url_el, image_el = None, None, None, None
                for s in selectors['title']:
                    title_el = item.select_one(s)
                    if title_el: break
                for s in selectors['price']:
                    price_el = item.select_one(s)
                    if price_el: break
                for s in selectors['url']:
                    url_el = item.select_one(s)
                    if url_el: break
                for s in selectors['image']:
                    image_el = item.select_one(s)
                    if image_el: break
                
                if not all([title_el, price_el, url_el, image_el]): continue
                
                title = title_el.get_text(strip=True)
                price_text = enterprise_scraper.clean_text(price_el.get_text(strip=True))
                if not title or not price_text: continue
                
                price_float = float(price_text)
                product_url = f"https://www.flipkart.com{url_el['href']}"
                image_url = image_el.get('src', '')
                
                unique_id_match = re.search(r'pid=([A-Z0-9]+)', product_url)
                unique_id = unique_id_match.group(1) if unique_id_match else product_url
                
                product_id = add_product_if_not_exists(unique_id, title, product_url)
                if product_id:
                    add_price_entry(product_id, price_float, "In Stock", image_url)
                    products_processed += 1
                    logger.info(f"Saved Flipkart product: {title[:50]}...")
            except Exception as e:
                logger.error(f"Error processing a Flipkart product item: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully processed {products_processed} Flipkart products.")
    except Exception as e:
        logger.error(f"Flipkart scraping failed for query '{query}': {e}", exc_info=True)
    finally:
        await enterprise_scraper.close()

# --- NEW: Main task orchestrator ---
async def process_scrape_task(query: str):
    """Determines if the query is a URL or a search term and calls the appropriate function."""
    if is_url(query):
        platform = get_platform_from_url(query)
        if platform:
            await process_single_product_page(query, platform)
        else:
            logger.warning(f"Received a URL from an unsupported platform: {query}")
    else:
        # It's a search term, so search both platforms
        # We run them concurrently for speed
        await asyncio.gather(
            process_amazon_search(query),
            process_flipkart_search(query)
        )

# --- MODIFIED: Synchronous wrapper for Celery ---
def sync_process_scrape_task(query: str):
    """Synchronous wrapper for the main scrape task orchestrator."""
    # Using asyncio.run() is simpler and safer for top-level async calls
    try:
        asyncio.run(process_scrape_task(query))
    except Exception as e:
        logger.error(f"An error occurred in the sync wrapper for query '{query}': {e}", exc_info=True)