"""
Utility functions for the enterprise scraping system.

This module provides common utility functions used across the scraping
infrastructure, including enhanced browser profile generation and configuration.
"""
import random
import logging
from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

def get_random_user_agent() -> str:
    """
    Get a random user agent string.
    
    Returns:
        A random user agent string
    """
    return config.get_random_user_agent()

def get_random_viewport() -> dict:
    """
    Get a random viewport configuration.
    
    Returns:
        Dictionary with width and height
    """
    return config.get_random_viewport()

def get_random_locale() -> str:
    """
    Get a random locale.
    
    Returns:
        Locale string
    """
    return config.get_random_locale()

def get_random_timezone() -> str:
    """
    Get a random timezone.
    
    Returns:
        Timezone string
    """
    return config.get_random_timezone()

def get_enhanced_headers() -> dict:
    """
    Get enhanced headers for requests.
    
    Returns:
        Dictionary of HTTP headers
    """
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

def get_mobile_headers() -> dict:
    """
    Get headers that simulate a mobile device.
    
    Returns:
        Dictionary of mobile-specific HTTP headers
    """
    mobile_user_agents = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    ]
    
    return {
        'User-Agent': random.choice(mobile_user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'sec-ch-ua-mobile': '?1'
    }

def get_browser_profile() -> dict:
    """
    Get a complete browser profile for realistic browsing.
    
    Returns:
        Dictionary with complete browser configuration
    """
    return {
        'viewport': get_random_viewport(),
        'user_agent': get_random_user_agent(),
        'locale': get_random_locale(),
        'timezone': get_random_timezone(),
        'headers': get_enhanced_headers()
    }

class EnterpriseScrapingError(Exception):
    """
    Custom exception for enterprise scraping errors.
    """
    pass

if __name__ == "__main__":
    # Test the module
    print("Testing enterprise utility functions:")
    
    print("\n1. User Agent Generation:")
    for i in range(3):
        ua = get_random_user_agent()
        print(f"  {i+1}. {ua}")
    
    print("\n2. Random Viewport:")
    for i in range(3):
        viewport = get_random_viewport()
        print(f"  {i+1}. {viewport['width']}x{viewport['height']}")
    
    print("\n3. Enhanced Headers:")
    headers = get_enhanced_headers()
    for key, value in list(headers.items())[:5]:  # Show first 5
        print(f"  {key}: {value}")
    
    print("\n4. Complete Browser Profile:")
    profile = get_browser_profile()
    print(f"  Viewport: {profile['viewport']}")
    print(f"  Locale: {profile['locale']}")
    print(f"  Timezone: {profile['timezone']}")
    print(f"  User Agent: {profile['user_agent'][:50]}...")