"""
Proxy Pool Manager - Thread-safe singleton for managing proxy state.

This module provides a centralized, thread-safe proxy pool that can be
used across the application. It handles proxy lifecycle, caching, and
automatic pool replenishment.
"""
import json
import os
import time
import threading
import queue
from typing import Optional, List
import logging
from datetime import datetime, timedelta

from proxy_sourcing import fetch_proxies_from_sources
from proxy_validator import get_healthy_proxies

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyPoolManager:
    """
    Thread-safe singleton class for managing a pool of healthy proxies.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Prevent multiple initialization
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # Configuration
        self.cache_file = os.path.join(os.path.dirname(__file__), 'healthy_proxies.json')
        self.cache_max_age = 30 * 60  # 30 minutes in seconds
        self.min_pool_size = 10  # Minimum proxies to maintain in pool
        self.max_pool_size = 100  # Maximum proxies in pool
        
        # Thread-safe proxy pool
        self.proxy_pool = queue.Queue()
        self.failed_proxies = set()  # Track failed proxies
        self.pool_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_sourced': 0,
            'total_validated': 0,
            'currently_healthy': 0,
            'total_failed': 0,
            'last_refresh': None
        }
        
        # Initialize the pool
        self._populate_pool()
    
    def _load_cache(self) -> Optional[List[str]]:
        """
        Load proxies from cache if it exists and is fresh.
        
        Returns:
            List of cached proxies or None if cache is invalid/stale
        """
        try:
            if not os.path.exists(self.cache_file):
                logger.info("No proxy cache file found")
                return None
            
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check cache age
            cache_timestamp = cache_data.get('timestamp', 0)
            cache_age = time.time() - cache_timestamp
            
            if cache_age > self.cache_max_age:
                logger.info(f"Proxy cache is stale ({cache_age:.0f}s old), will refresh")
                return None
            
            proxies = cache_data.get('proxies', [])
            logger.info(f"Loaded {len(proxies)} proxies from cache (age: {cache_age:.0f}s)")
            return proxies
            
        except Exception as e:
            logger.error(f"Error loading proxy cache: {e}")
            return None
    
    def _save_cache(self, proxies: List[str]) -> None:
        """
        Save proxies to cache file.
        
        Args:
            proxies: List of proxy strings to cache
        """
        try:
            cache_data = {
                'timestamp': time.time(),
                'proxies': proxies
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Saved {len(proxies)} proxies to cache")
            
        except Exception as e:
            logger.error(f"Error saving proxy cache: {e}")
    
    def _populate_pool(self) -> None:
        """
        Populate the proxy pool with healthy proxies.
        This method handles both cache loading and fresh proxy sourcing.
        """
        with self.pool_lock:
            logger.info("Populating proxy pool...")
            
            # First, try to load from cache
            cached_proxies = self._load_cache()
            
            if cached_proxies:
                # Use cached proxies
                for proxy in cached_proxies:
                    if proxy not in self.failed_proxies:
                        self.proxy_pool.put(proxy)
                
                self.stats['currently_healthy'] = self.proxy_pool.qsize()
                logger.info(f"Proxy pool populated with {self.proxy_pool.qsize()} cached proxies")
                return
            
            # Cache is stale or empty, fetch fresh proxies
            logger.info("Fetching fresh proxies from sources...")
            
            try:
                # Source proxies
                raw_proxies = fetch_proxies_from_sources()
                self.stats['total_sourced'] = len(raw_proxies)
                
                if not raw_proxies:
                    logger.error("No proxies could be sourced!")
                    return
                
                # Validate proxies
                logger.info(f"Validating {len(raw_proxies)} sourced proxies...")
                healthy_proxies = get_healthy_proxies(raw_proxies)
                self.stats['total_validated'] = len(healthy_proxies)
                
                if not healthy_proxies:
                    logger.error("No healthy proxies found after validation!")
                    return
                
                # Limit pool size
                if len(healthy_proxies) > self.max_pool_size:
                    healthy_proxies = healthy_proxies[:self.max_pool_size]
                
                # Save to cache
                self._save_cache(healthy_proxies)
                
                # Add to pool
                for proxy in healthy_proxies:
                    self.proxy_pool.put(proxy)
                
                self.stats['currently_healthy'] = self.proxy_pool.qsize()
                self.stats['last_refresh'] = datetime.now()
                
                logger.info(f"Proxy pool populated with {self.proxy_pool.qsize()} fresh proxies")
                
            except Exception as e:
                logger.error(f"Error populating proxy pool: {e}")
    
    def get_proxy(self) -> Optional[str]:
        """
        Get a proxy from the pool.
        
        Returns:
            A proxy string or None if no proxies are available
        """
        try:
            # Check if pool needs replenishment
            if self.proxy_pool.qsize() < self.min_pool_size:
                logger.info(f"Proxy pool is low ({self.proxy_pool.qsize()} proxies), replenishing...")
                self._populate_pool()
            
            # Get proxy from pool (non-blocking)
            proxy = self.proxy_pool.get_nowait()
            logger.debug(f"Dispensed proxy: {proxy}")
            return proxy
            
        except queue.Empty:
            logger.warning("Proxy pool is empty, attempting to replenish...")
            self._populate_pool()
            
            # Try one more time after replenishment
            try:
                proxy = self.proxy_pool.get_nowait()
                logger.debug(f"Dispensed proxy after replenishment: {proxy}")
                return proxy
            except queue.Empty:
                logger.error("No proxies available even after replenishment!")
                return None
    
    def return_proxy(self, proxy: str) -> None:
        """
        Return a successfully used proxy back to the pool.
        
        Args:
            proxy: The proxy string to return
        """
        try:
            if proxy not in self.failed_proxies:
                self.proxy_pool.put(proxy)
                logger.debug(f"Returned proxy to pool: {proxy}")
            else:
                logger.debug(f"Not returning failed proxy: {proxy}")
        except Exception as e:
            logger.error(f"Error returning proxy to pool: {e}")
    
    def report_failed_proxy(self, proxy: str) -> None:
        """
        Report a proxy as failed and remove it from circulation.
        
        Args:
            proxy: The proxy string that failed
        """
        self.failed_proxies.add(proxy)
        self.stats['total_failed'] += 1
        logger.debug(f"Marked proxy as failed: {proxy}")
    
    def get_stats(self) -> dict:
        """
        Get current proxy pool statistics.
        
        Returns:
            Dictionary containing pool statistics
        """
        return {
            **self.stats,
            'pool_size': self.proxy_pool.qsize(),
            'failed_count': len(self.failed_proxies)
        }
    
    def force_refresh(self) -> None:
        """
        Force a fresh proxy pool refresh, bypassing cache.
        """
        logger.info("Forcing proxy pool refresh...")
        
        # Clear existing pool
        with self.pool_lock:
            while not self.proxy_pool.empty():
                try:
                    self.proxy_pool.get_nowait()
                except queue.Empty:
                    break
        
        # Clear failed proxies set
        self.failed_proxies.clear()
        
        # Remove cache file to force fresh sourcing
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        
        # Repopulate
        self._populate_pool()

# Module-level functions for easy import
def get_proxy_manager() -> ProxyPoolManager:
    """
    Get the singleton proxy pool manager instance.
    
    Returns:
        ProxyPoolManager instance
    """
    return ProxyPoolManager()

if __name__ == "__main__":
    # Test the module
    manager = get_proxy_manager()
    
    print("Proxy Pool Manager Statistics:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nTesting proxy retrieval:")
    for i in range(3):
        proxy = manager.get_proxy()
        if proxy:
            print(f"  Got proxy: {proxy}")
            # Simulate successful use
            manager.return_proxy(proxy)
        else:
            print("  No proxy available")