"""
Utility functions for the scraping system.

This module provides common utility functions used across the scraping
infrastructure, including user agent generation and request helpers.
"""
import random
from fake_useragent import UserAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserAgentManager:
    """
    Manages user agent generation for requests.
    """
    
    def __init__(self):
        """
        Initialize the user agent manager.
        """
        try:
            self.ua = UserAgent()
            logger.info("UserAgent initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize UserAgent: {e}")
            self.ua = None
            
            # Fallback user agents
            self.fallback_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
            ]
    
    def get_random_user_agent(self) -> str:
        """
        Generate a random user agent string.
        
        Returns:
            A random user agent string
        """
        try:
            if self.ua:
                # Try different browsers
                browsers = ['chrome', 'firefox', 'safari', 'edge']
                browser = random.choice(browsers)
                
                if browser == 'chrome':
                    return self.ua.chrome
                elif browser == 'firefox':
                    return self.ua.firefox
                elif browser == 'safari':
                    return self.ua.safari
                else:
                    return self.ua.random
            else:
                # Use fallback
                return random.choice(self.fallback_agents)
                
        except Exception as e:
            logger.warning(f"Error generating user agent: {e}")
            return random.choice(self.fallback_agents)

# Global user agent manager instance
_ua_manager = UserAgentManager()

def get_random_user_agent() -> str:
    """
    Get a random user agent string.
    
    Returns:
        A random user agent string
    """
    return _ua_manager.get_random_user_agent()

def get_common_headers() -> dict:
    """
    Get common headers for web requests.
    
    Returns:
        Dictionary of common HTTP headers
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
        'Cache-Control': 'max-age=0'
    }

def get_mobile_headers() -> dict:
    """
    Get headers that simulate a mobile device.
    
    Returns:
        Dictionary of mobile-specific HTTP headers
    """
    mobile_user_agents = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
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
        'Cache-Control': 'max-age=0'
    }

def validate_proxy_format(proxy: str) -> bool:
    """
    Validate if a proxy string is in the correct format.
    
    Args:
        proxy: Proxy string to validate
        
    Returns:
        True if proxy format is valid, False otherwise
    """
    import re
    
    # Check for IP:PORT format
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):\d{1,5}$'
    return re.match(pattern, proxy) is not None

def create_proxy_dict(proxy: str) -> dict:
    """
    Create a proxy dictionary for use with requests.
    
    Args:
        proxy: Proxy string in format "ip:port"
        
    Returns:
        Dictionary formatted for requests library
    """
    return {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}'
    }

class ScrapingFailedError(Exception):
    """
    Custom exception for when scraping fails after all retries.
    """
    pass

if __name__ == "__main__":
    # Test the module
    print("Testing utility functions:")
    
    print("\n1. User Agent Generation:")
    for i in range(3):
        ua = get_random_user_agent()
        print(f"  {i+1}. {ua}")
    
    print("\n2. Common Headers:")
    headers = get_common_headers()
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    print("\n3. Proxy Validation:")
    test_proxies = [
        "192.168.1.1:8080",  # Valid format
        "invalid:proxy",      # Invalid format
        "1.2.3.4:99999",     # Valid format (high port)
        "256.1.1.1:8080"     # Invalid IP
    ]
    
    for proxy in test_proxies:
        valid = validate_proxy_format(proxy)
        print(f"  {proxy}: {'Valid' if valid else 'Invalid'}")