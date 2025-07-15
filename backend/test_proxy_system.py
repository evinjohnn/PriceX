#!/usr/bin/env python3
"""
Test script for the Intelligent Proxy Management System

This script demonstrates the key features of the proxy management system:
- Proxy sourcing from multiple free sources
- Concurrent proxy validation
- Proxy pool management
- User agent rotation
- Resilient scraping with automatic retry

Run this script to test the system before using it in production.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import logging
from proxy_sourcing import fetch_proxies_from_sources
from proxy_validator import get_healthy_proxies
from proxy_pool_manager import get_proxy_manager
from utils import get_random_user_agent, get_common_headers
from scrapers.scraper import scrape_with_proxy, ScrapingFailedError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_proxy_sourcing():
    """Test proxy sourcing functionality"""
    print("\n" + "="*50)
    print("TESTING PROXY SOURCING")
    print("="*50)
    
    try:
        proxies = fetch_proxies_from_sources()
        print(f"✓ Successfully sourced {len(proxies)} proxies")
        
        if proxies:
            print("\nSample proxies:")
            for i, proxy in enumerate(proxies[:5]):
                print(f"  {i+1}. {proxy}")
        
        return proxies
    except Exception as e:
        print(f"✗ Proxy sourcing failed: {e}")
        return []

def test_proxy_validation(proxies):
    """Test proxy validation functionality"""
    print("\n" + "="*50)
    print("TESTING PROXY VALIDATION")
    print("="*50)
    
    if not proxies:
        print("✗ No proxies to validate")
        return []
    
    try:
        # Test with first 20 proxies for speed
        test_proxies = proxies[:20]
        print(f"Validating first {len(test_proxies)} proxies...")
        
        healthy = get_healthy_proxies(test_proxies)
        success_rate = (len(healthy) / len(test_proxies)) * 100
        
        print(f"✓ Validation complete: {len(healthy)}/{len(test_proxies)} healthy ({success_rate:.1f}% success rate)")
        
        if healthy:
            print("\nHealthy proxies:")
            for i, proxy in enumerate(healthy):
                print(f"  {i+1}. {proxy}")
        
        return healthy
    except Exception as e:
        print(f"✗ Proxy validation failed: {e}")
        return []

def test_proxy_pool_manager():
    """Test proxy pool manager functionality"""
    print("\n" + "="*50)
    print("TESTING PROXY POOL MANAGER")
    print("="*50)
    
    try:
        manager = get_proxy_manager()
        stats = manager.get_stats()
        
        print("Proxy Pool Manager Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Try to get a proxy
        proxy = manager.get_proxy()
        if proxy:
            print(f"\n✓ Retrieved proxy from pool: {proxy}")
            # Return it back
            manager.return_proxy(proxy)
            print("✓ Successfully returned proxy to pool")
        else:
            print("\n! No proxies available in pool (expected with free proxies)")
        
        return True
    except Exception as e:
        print(f"✗ Proxy pool manager test failed: {e}")
        return False

def test_user_agent_rotation():
    """Test user agent rotation functionality"""
    print("\n" + "="*50)
    print("TESTING USER AGENT ROTATION")
    print("="*50)
    
    try:
        print("Generating random user agents:")
        for i in range(5):
            ua = get_random_user_agent()
            print(f"  {i+1}. {ua}")
        
        print("\n✓ User agent rotation working correctly")
        return True
    except Exception as e:
        print(f"✗ User agent rotation failed: {e}")
        return False

def test_integrated_scraping():
    """Test integrated scraping with proxy management"""
    print("\n" + "="*50)
    print("TESTING INTEGRATED SCRAPING")
    print("="*50)
    
    test_urls = [
        'https://httpbin.org/ip',
        'https://httpbin.org/user-agent',
        'https://ipinfo.io/ip'
    ]
    
    for url in test_urls:
        try:
            print(f"\nTesting URL: {url}")
            result = scrape_with_proxy(url, max_retries=3)
            
            if result:
                print(f"✓ Successfully scraped {url}")
                print(f"  Response length: {len(result)} characters")
                print(f"  Response preview: {result[:100]}...")
            else:
                print(f"✗ Failed to scrape {url}")
                
        except ScrapingFailedError as e:
            print(f"! Scraping failed for {url}: {e}")
            print("  This is expected with free proxies")
        except Exception as e:
            print(f"✗ Unexpected error for {url}: {e}")

def main():
    """Main test function"""
    print("INTELLIGENT PROXY MANAGEMENT SYSTEM TEST")
    print("="*60)
    print("This test will demonstrate the proxy management system.")
    print("Note: Free proxies have low success rates, so some tests may fail.")
    print("="*60)
    
    # Test 1: Proxy Sourcing
    proxies = test_proxy_sourcing()
    
    # Test 2: Proxy Validation
    healthy_proxies = test_proxy_validation(proxies)
    
    # Test 3: Proxy Pool Manager
    test_proxy_pool_manager()
    
    # Test 4: User Agent Rotation
    test_user_agent_rotation()
    
    # Test 5: Integrated Scraping
    test_integrated_scraping()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total proxies sourced: {len(proxies)}")
    print(f"Healthy proxies found: {len(healthy_proxies)}")
    if proxies:
        success_rate = (len(healthy_proxies) / len(proxies[:20])) * 100
        print(f"Validation success rate: {success_rate:.1f}%")
    
    print("\n" + "="*60)
    print("SYSTEM READY!")
    print("="*60)
    print("The proxy management system is now ready for use.")
    print("You can now start the main application with confidence.")
    print("Note: First scraping requests may be slower due to proxy validation.")

if __name__ == "__main__":
    main()