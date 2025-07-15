"""
Configuration settings for the enterprise-grade scraping system.

This module contains all configuration settings for the multi-tiered
scraping architecture including timeouts, retry counts, and service settings.
"""
import os
from typing import Dict, Any

class ScrapingConfig:
    """
    Configuration class for the scraping system.
    """
    
    # =============================================================================
    # GENERAL SETTINGS
    # =============================================================================
    
    # Request timeouts (in seconds)
    PAGE_LOAD_TIMEOUT = 30
    ELEMENT_WAIT_TIMEOUT = 10
    NAVIGATION_TIMEOUT = 30
    
    # Retry settings
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_BASE = 2  # Base delay in seconds (exponential backoff)
    RETRY_DELAY_MAX = 30  # Maximum delay in seconds
    
    # =============================================================================
    # PLAYWRIGHT SETTINGS (TIER 1)
    # =============================================================================
    
    # Browser settings
    BROWSER_HEADLESS = True
    BROWSER_SLOW_MO = 0  # Milliseconds to slow down operations
    
    # Viewport settings for realistic browsing
    VIEWPORT_SIZES = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 720},
    ]
    
    # Locale and timezone settings
    LOCALES = [
        "en-US",
        "en-GB",
        "en-IN",
        "en-CA",
        "en-AU"
    ]
    
    TIMEZONES = [
        "America/New_York",
        "America/Chicago",
        "America/Denver",
        "America/Los_Angeles",
        "Europe/London",
        "Asia/Kolkata"
    ]
    
    # User agent settings
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    ]
    
    # =============================================================================
    # AWS LAMBDA SETTINGS (TIER 2)
    # =============================================================================
    
    # AWS Lambda configuration
    AWS_LAMBDA_FUNCTION_NAME = os.getenv("AWS_LAMBDA_FUNCTION_NAME", "web-scraper-function")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Lambda timeout settings
    LAMBDA_TIMEOUT = 60  # seconds
    LAMBDA_MEMORY_SIZE = 1024  # MB
    
    # =============================================================================
    # CAPTCHA SOLVER SETTINGS (TIER 3)
    # =============================================================================
    
    # 2Captcha service configuration
    CAPTCHA_API_KEY = os.getenv("2CAPTCHA_API_KEY")
    CAPTCHA_SERVICE_URL = "http://2captcha.com"
    CAPTCHA_SOLVE_TIMEOUT = 120  # seconds
    CAPTCHA_POLL_INTERVAL = 5  # seconds
    
    # CAPTCHA detection patterns
    CAPTCHA_INDICATORS = [
        "captcha",
        "captchacharacters",
        "auth-captcha",
        "cvf-captcha",
        "captcha-image",
        "robot-check",
        "verification",
        "security-check",
        "Enter the characters you see below",
        "Type the characters you see in this image",
        "To continue, please type the characters below",
        "Please verify you're not a robot"
    ]
    
    # =============================================================================
    # SITE-SPECIFIC SETTINGS
    # =============================================================================
    
    # Amazon-specific settings
    AMAZON_DOMAINS = [
        "amazon.in",
        "amazon.com",
        "amazon.co.uk",
        "amazon.de",
        "amazon.fr"
    ]
    
    # Flipkart-specific settings
    FLIPKART_DOMAINS = [
        "flipkart.com"
    ]
    
    # Common selectors for products
    PRODUCT_SELECTORS = {
        "amazon": {
            "search_results": 'div[data-component-type="s-search-result"]',
            "title": "span.a-text-normal",
            "price": ".a-price-whole",
            "image": "img.s-image",
            "url": "a.a-link-normal"
        },
        "flipkart": {
            "search_results": ['div._1xHGtK._373qXS', 'div._4ddWXP', 'div.slAVV4', 'div._1UoZlX'],
            "title": ['a.s1Q9rs', 'a._1fQZEK', 'a.IRpwTa', 'a._2WkVRV'],
            "price": ['div._30jeq3', 'div._1_WHN1', 'div._3tbHP2'],
            "image": ['img._396cs4', 'img._2r_T1I', 'img._3exPp9'],
            "url": ['a.s1Q9rs', 'a._1fQZEK', 'a.IRpwTa']
        }
    }
    
    # =============================================================================
    # RATE LIMITING SETTINGS
    # =============================================================================
    
    # Delays between requests (in seconds)
    MIN_REQUEST_DELAY = 2
    MAX_REQUEST_DELAY = 8
    
    # Delays between page interactions
    MIN_INTERACTION_DELAY = 0.5
    MAX_INTERACTION_DELAY = 2.0
    
    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    @classmethod
    def get_random_viewport(cls) -> Dict[str, int]:
        """Get a random viewport size."""
        import random
        return random.choice(cls.VIEWPORT_SIZES)
    
    @classmethod
    def get_random_locale(cls) -> str:
        """Get a random locale."""
        import random
        return random.choice(cls.LOCALES)
    
    @classmethod
    def get_random_timezone(cls) -> str:
        """Get a random timezone."""
        import random
        return random.choice(cls.TIMEZONES)
    
    @classmethod
    def get_random_user_agent(cls) -> str:
        """Get a random user agent."""
        import random
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def is_aws_configured(cls) -> bool:
        """Check if AWS credentials are configured."""
        return bool(cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY)
    
    @classmethod
    def is_captcha_configured(cls) -> bool:
        """Check if CAPTCHA solving is configured."""
        return bool(cls.CAPTCHA_API_KEY)
    
    @classmethod
    def get_site_selectors(cls, site: str) -> Dict[str, Any]:
        """Get selectors for a specific site."""
        return cls.PRODUCT_SELECTORS.get(site, {})

# Global configuration instance
config = ScrapingConfig()