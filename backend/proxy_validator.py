"""
Concurrent Proxy Validator - Tests proxies to filter out dead/slow ones.

This module provides concurrent validation of proxy lists to identify
healthy proxies that can be used for scraping. It's designed to handle
the high failure rate of free proxies efficiently.
"""
import requests
import concurrent.futures
import time
import logging
from typing import List, Optional
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyValidator:
    """
    Validates proxies concurrently to filter out dead or slow ones.
    """
    
    def __init__(self, max_workers: int = 50, timeout: int = 8):
        """
        Initialize the proxy validator.
        
        Args:
            max_workers: Maximum number of concurrent validation threads
            timeout: Request timeout in seconds
        """
        self.max_workers = max_workers
        self.timeout = timeout
        
        # Test URLs to validate proxies against
        self.test_urls = [
            'https://httpbin.org/ip',
            'https://ipinfo.io/ip',
            'https://api.ipify.org',
            'https://checkip.amazonaws.com/',
        ]
        
        # Headers to use during validation
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _validate_proxy(self, proxy: str) -> Optional[str]:
        """
        Validate a single proxy by making a test request.
        
        Args:
            proxy: Proxy string in format "ip:port"
            
        Returns:
            The proxy string if valid, None if invalid
        """
        try:
            # Choose a random test URL to avoid overloading any single service
            test_url = random.choice(self.test_urls)
            
            # Configure proxy for requests
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'https://{proxy}'
            }
            
            # Make test request
            start_time = time.time()
            response = requests.get(
                test_url,
                proxies=proxy_dict,
                headers=self.headers,
                timeout=self.timeout,
                verify=False  # Don't verify SSL for test requests
            )
            
            response_time = time.time() - start_time
            
            # Check if request was successful and reasonably fast
            if response.status_code == 200 and response_time < self.timeout:
                # Additional check: make sure we got a response that looks like an IP
                response_text = response.text.strip()
                if len(response_text) > 0 and len(response_text) < 100:
                    logger.debug(f"✓ Proxy {proxy} is healthy (response time: {response_time:.2f}s)")
                    return proxy
            
            logger.debug(f"✗ Proxy {proxy} failed: Status {response.status_code}, Time {response_time:.2f}s")
            return None
            
        except requests.exceptions.ProxyError:
            logger.debug(f"✗ Proxy {proxy} failed: Proxy error")
            return None
        except requests.exceptions.Timeout:
            logger.debug(f"✗ Proxy {proxy} failed: Timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.debug(f"✗ Proxy {proxy} failed: Connection error")
            return None
        except Exception as e:
            logger.debug(f"✗ Proxy {proxy} failed: {e}")
            return None
    
    def get_healthy_proxies(self, proxies: List[str]) -> List[str]:
        """
        Validate a list of proxies concurrently and return only healthy ones.
        
        Args:
            proxies: List of proxy strings in format "ip:port"
            
        Returns:
            List of validated, healthy proxy strings
        """
        if not proxies:
            logger.warning("No proxies provided for validation")
            return []
        
        logger.info(f"Starting concurrent validation of {len(proxies)} proxies...")
        logger.info(f"Using {self.max_workers} concurrent workers with {self.timeout}s timeout")
        
        healthy_proxies = []
        completed = 0
        
        # Use ThreadPoolExecutor for concurrent validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all validation tasks
            future_to_proxy = {
                executor.submit(self._validate_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_proxy):
                completed += 1
                proxy = future_to_proxy[future]
                
                try:
                    result = future.result()
                    if result is not None:
                        healthy_proxies.append(result)
                    
                    # Log progress every 10% or every 100 proxies
                    if completed % max(len(proxies) // 10, 100) == 0:
                        success_rate = (len(healthy_proxies) / completed) * 100
                        logger.info(f"Progress: {completed}/{len(proxies)} ({success_rate:.1f}% success rate)")
                        
                except Exception as e:
                    logger.error(f"Unexpected error validating proxy {proxy}: {e}")
        
        success_rate = (len(healthy_proxies) / len(proxies)) * 100
        logger.info(f"Validation complete: {len(healthy_proxies)}/{len(proxies)} proxies are healthy ({success_rate:.1f}% success rate)")
        
        return healthy_proxies
    
    def validate_proxy_batch(self, proxies: List[str], batch_size: int = 100) -> List[str]:
        """
        Validate proxies in batches to manage memory usage for large lists.
        
        Args:
            proxies: List of proxy strings to validate
            batch_size: Number of proxies to validate in each batch
            
        Returns:
            List of validated, healthy proxy strings
        """
        if not proxies:
            return []
        
        logger.info(f"Validating {len(proxies)} proxies in batches of {batch_size}")
        
        all_healthy = []
        
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(proxies) + batch_size - 1)//batch_size}")
            
            healthy_batch = self.get_healthy_proxies(batch)
            all_healthy.extend(healthy_batch)
            
            # Small delay between batches to be respectful
            if i + batch_size < len(proxies):
                time.sleep(1)
        
        return all_healthy

# Module-level function for easy import
def get_healthy_proxies(proxies: List[str]) -> List[str]:
    """
    Convenience function to validate a list of proxies.
    
    Args:
        proxies: List of proxy strings in format "ip:port"
        
    Returns:
        List of validated, healthy proxy strings
    """
    validator = ProxyValidator()
    return validator.get_healthy_proxies(proxies)

if __name__ == "__main__":
    # Test the module
    test_proxies = [
        "8.8.8.8:8080",  # This will likely fail
        "1.1.1.1:80",    # This will likely fail
        "127.0.0.1:8080" # This will likely fail
    ]
    
    healthy = get_healthy_proxies(test_proxies)
    print(f"Healthy proxies: {healthy}")