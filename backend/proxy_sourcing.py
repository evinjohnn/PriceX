"""
Proxy Sourcing Module - Fetches free proxies from public sources.

This module is responsible for collecting potential proxies from various
free proxy websites. It includes error handling for when sources are
down or change their layout.
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from typing import List, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxySourcer:
    """
    Handles fetching proxies from multiple free proxy sources.
    """
    
    def __init__(self):
        self.sources = [
            {
                'url': 'https://free-proxy-list.net/',
                'parser': self._parse_free_proxy_list
            },
            {
                'url': 'https://www.sslproxies.org/',
                'parser': self._parse_ssl_proxies
            },
            {
                'url': 'https://www.proxy-list.download/api/v1/get?type=http',
                'parser': self._parse_proxy_list_download
            }
        ]
        
        # Headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _parse_free_proxy_list(self, html_content: str) -> Set[str]:
        """
        Parse proxies from free-proxy-list.net format.
        """
        proxies = set()
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table', id='proxylisttable')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        # Only add if it's HTTP/HTTPS (not SOCKS)
                        if len(cols) >= 5 and cols[4].text.strip().lower() in ['no', 'yes']:
                            proxies.add(f"{ip}:{port}")
            
            logger.info(f"Parsed {len(proxies)} proxies from free-proxy-list.net")
            
        except Exception as e:
            logger.error(f"Error parsing free-proxy-list.net: {e}")
        
        return proxies
    
    def _parse_ssl_proxies(self, html_content: str) -> Set[str]:
        """
        Parse proxies from sslproxies.org format.
        """
        proxies = set()
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table', id='proxylisttable')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxies.add(f"{ip}:{port}")
            
            logger.info(f"Parsed {len(proxies)} proxies from sslproxies.org")
            
        except Exception as e:
            logger.error(f"Error parsing sslproxies.org: {e}")
        
        return proxies
    
    def _parse_proxy_list_download(self, content: str) -> Set[str]:
        """
        Parse proxies from proxy-list-download API (simple line format).
        """
        proxies = set()
        try:
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', line):
                    proxies.add(line)
            
            logger.info(f"Parsed {len(proxies)} proxies from proxy-list-download")
            
        except Exception as e:
            logger.error(f"Error parsing proxy-list-download: {e}")
        
        return proxies
    
    def _fetch_from_source(self, source: dict) -> Set[str]:
        """
        Fetch proxies from a single source with error handling.
        """
        try:
            logger.info(f"Fetching proxies from {source['url']}")
            
            # Add random delay to avoid being rate-limited
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(
                source['url'],
                headers=self.headers,
                timeout=30,
                verify=False  # Some proxy sites have SSL issues
            )
            
            if response.status_code == 200:
                return source['parser'](response.text)
            else:
                logger.warning(f"Failed to fetch from {source['url']}: {response.status_code}")
                return set()
                
        except Exception as e:
            logger.error(f"Error fetching from {source['url']}: {e}")
            return set()
    
    def fetch_proxies_from_sources(self) -> List[str]:
        """
        Fetch proxies from all configured sources.
        
        Returns:
            List of proxy strings in format "ip:port"
        """
        logger.info("Starting proxy sourcing from multiple sources...")
        
        all_proxies = set()
        
        for source in self.sources:
            try:
                proxies = self._fetch_from_source(source)
                all_proxies.update(proxies)
                
                # Add delay between sources to be respectful
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"Unexpected error with source {source['url']}: {e}")
                continue
        
        # Remove duplicates and convert to list
        unique_proxies = list(all_proxies)
        logger.info(f"Total unique proxies collected: {len(unique_proxies)}")
        
        return unique_proxies

# Module-level function for easy import
def fetch_proxies_from_sources() -> List[str]:
    """
    Convenience function to fetch proxies from all sources.
    
    Returns:
        List of proxy strings in format "ip:port"
    """
    sourcer = ProxySourcer()
    return sourcer.fetch_proxies_from_sources()

if __name__ == "__main__":
    # Test the module
    proxies = fetch_proxies_from_sources()
    print(f"Found {len(proxies)} proxies")
    print("Sample proxies:")
    for i, proxy in enumerate(proxies[:5]):
        print(f"  {i+1}. {proxy}")