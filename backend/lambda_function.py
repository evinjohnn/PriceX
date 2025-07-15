"""
AWS Lambda Function for Serverless Web Scraping

This Lambda function provides IP rotation and clean datacenter IPs for web scraping.
It uses Playwright in a serverless environment to perform scraping tasks with
enterprise-grade reliability and anti-detection capabilities.
"""
import json
import asyncio
import base64
import logging
import os
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LambdaScrapingError(Exception):
    """Custom exception for Lambda scraping errors."""
    pass

class LambdaScraper:
    """
    Serverless web scraper using Playwright in AWS Lambda.
    """
    
    def __init__(self):
        """Initialize the Lambda scraper."""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
        # Configuration
        self.timeout = 30000  # 30 seconds
        self.viewport_sizes = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1280, "height": 720},
        ]
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
    
    def get_random_config(self) -> Dict[str, Any]:
        """Get random browser configuration."""
        import random
        
        return {
            "viewport": random.choice(self.viewport_sizes),
            "user_agent": random.choice(self.user_agents),
            "locale": random.choice(["en-US", "en-GB", "en-CA"]),
            "timezone": random.choice(["America/New_York", "America/Chicago", "America/Los_Angeles"])
        }
    
    async def initialize_browser(self) -> None:
        """Initialize the browser with stealth settings."""
        try:
            logger.info("Initializing Playwright browser...")
            
            playwright = await async_playwright().start()
            
            # Get random configuration
            config = self.get_random_config()
            
            # Launch browser with stealth settings
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--single-process',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                viewport=config["viewport"],
                user_agent=config["user_agent"],
                locale=config["locale"],
                timezone_id=config["timezone"],
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
                    "Cache-Control": "max-age=0"
                }
            )
            
            logger.info("Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise LambdaScrapingError(f"Browser initialization failed: {e}")
    
    async def scrape_url(self, url: str, wait_for_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape a single URL and return the content.
        
        Args:
            url: URL to scrape
            wait_for_selector: Optional CSS selector to wait for
            
        Returns:
            Dictionary with scraping results
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            if not self.context:
                await self.initialize_browser()
            
            # Create new page
            page = await self.context.new_page()
            
            # Set additional page settings
            await page.set_extra_http_headers({
                "DNT": "1",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"'
            })
            
            # Navigate to URL
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout
            )
            
            if not response:
                raise LambdaScrapingError("Failed to load page")
            
            # Wait for specific selector if provided
            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)
                except Exception as e:
                    logger.warning(f"Selector '{wait_for_selector}' not found: {e}")
            
            # Wait for page to fully load
            await page.wait_for_load_state("networkidle", timeout=self.timeout)
            
            # Get page content
            html_content = await page.content()
            
            # Get current URL (in case of redirects)
            current_url = page.url
            
            # Get page title
            title = await page.title()
            
            # Check for common blocking indicators
            blocking_indicators = [
                "captcha",
                "robot",
                "blocked",
                "access denied",
                "forbidden",
                "rate limit",
                "security check"
            ]
            
            content_lower = html_content.lower()
            is_blocked = any(indicator in content_lower for indicator in blocking_indicators)
            
            # Take screenshot for debugging (optional)
            screenshot = None
            if is_blocked:
                screenshot_bytes = await page.screenshot(full_page=False)
                screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            await page.close()
            
            result = {
                "success": True,
                "url": url,
                "current_url": current_url,
                "title": title,
                "html_content": html_content,
                "content_length": len(html_content),
                "is_blocked": is_blocked,
                "status_code": response.status,
                "screenshot": screenshot
            }
            
            logger.info(f"Successfully scraped {url} - Content length: {len(html_content)}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
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
scraper = LambdaScraper()

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        HTTP response with scraping results
    """
    try:
        logger.info("Lambda function invoked")
        logger.info(f"Event: {json.dumps(event, indent=2)}")
        
        # Parse request
        if "body" in event:
            # API Gateway event
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            # Direct invocation
            body = event
        
        # Extract parameters
        url = body.get("url")
        if not url:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing 'url' parameter"
                })
            }
        
        wait_for_selector = body.get("wait_for_selector")
        
        # Validate URL
        if not url.startswith(("http://", "https://")):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Invalid URL format"
                })
            }
        
        # Perform scraping
        result = asyncio.run(scraper.scrape_url(url, wait_for_selector))
        
        # Clean up
        asyncio.run(scraper.close())
        
        # Return response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda execution error: {e}")
        
        # Clean up on error
        try:
            asyncio.run(scraper.close())
        except:
            pass
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "error_type": type(e).__name__
            })
        }

# For local testing
if __name__ == "__main__":
    # Test the Lambda function locally
    test_event = {
        "url": "https://httpbin.org/ip",
        "wait_for_selector": None
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))