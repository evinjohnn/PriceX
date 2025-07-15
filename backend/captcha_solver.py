"""
CAPTCHA Solver Module - Automated CAPTCHA solving using third-party services.

This module provides enterprise-grade CAPTCHA solving capabilities using
services like 2Captcha or Anti-CAPTCHA. It integrates seamlessly with
Playwright for automated form submission.
"""
import asyncio
import base64
import io
import time
import logging
from typing import Optional, Dict, Any
import requests
from playwright.async_api import Page
from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class CaptchaDetectionError(Exception):
    """Raised when CAPTCHA detection fails."""
    pass

class CaptchaSolvingError(Exception):
    """Raised when CAPTCHA solving fails."""
    pass

class CaptchaSolver:
    """
    Enterprise-grade CAPTCHA solver using 2Captcha service.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the CAPTCHA solver.
        
        Args:
            api_key: 2Captcha API key (defaults to config)
        """
        self.api_key = api_key or config.CAPTCHA_API_KEY
        self.service_url = config.CAPTCHA_SERVICE_URL
        self.solve_timeout = config.CAPTCHA_SOLVE_TIMEOUT
        self.poll_interval = config.CAPTCHA_POLL_INTERVAL
        
        if not self.api_key:
            logger.warning("CAPTCHA API key not configured. CAPTCHA solving will be disabled.")
    
    def is_configured(self) -> bool:
        """Check if CAPTCHA solver is properly configured."""
        return bool(self.api_key)
    
    async def detect_captcha(self, page: Page) -> Optional[Dict[str, Any]]:
        """
        Detect CAPTCHA presence on the page.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary with CAPTCHA information if detected, None otherwise
        """
        try:
            logger.debug("Scanning page for CAPTCHA indicators...")
            
            # Check for common CAPTCHA indicators
            captcha_info = None
            
            # Method 1: Check for CAPTCHA by ID
            for indicator in config.CAPTCHA_INDICATORS:
                if indicator.startswith("#") or indicator.startswith("."):
                    # CSS selector
                    element = await page.query_selector(indicator)
                    if element:
                        captcha_info = {
                            "type": "image",
                            "element": element,
                            "selector": indicator,
                            "method": "css_selector"
                        }
                        break
                else:
                    # Text content check
                    if await page.query_selector(f"text={indicator}"):
                        captcha_info = {
                            "type": "text",
                            "text": indicator,
                            "method": "text_content"
                        }
                        break
            
            # Method 2: Common CAPTCHA image selectors
            if not captcha_info:
                captcha_selectors = [
                    "#captchacharacters",
                    "#auth-captcha-image",
                    "img[alt*='captcha']",
                    "img[src*='captcha']",
                    ".captcha-image",
                    "#cvf-captcha-image"
                ]
                
                for selector in captcha_selectors:
                    element = await page.query_selector(selector)
                    if element:
                        captcha_info = {
                            "type": "image",
                            "element": element,
                            "selector": selector,
                            "method": "image_selector"
                        }
                        break
            
            # Method 3: Check for input fields that might be CAPTCHA
            if not captcha_info:
                input_selectors = [
                    "input[name*='captcha']",
                    "input[id*='captcha']",
                    "input[placeholder*='captcha']"
                ]
                
                for selector in input_selectors:
                    element = await page.query_selector(selector)
                    if element:
                        captcha_info = {
                            "type": "input",
                            "element": element,
                            "selector": selector,
                            "method": "input_selector"
                        }
                        break
            
            if captcha_info:
                logger.info(f"CAPTCHA detected: {captcha_info['method']} - {captcha_info.get('selector', captcha_info.get('text'))}")
                return captcha_info
            
            logger.debug("No CAPTCHA detected on page")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return None
    
    async def capture_captcha_image(self, page: Page, element) -> Optional[str]:
        """
        Capture CAPTCHA image as base64 string.
        
        Args:
            page: Playwright page object
            element: CAPTCHA image element
            
        Returns:
            Base64 encoded image string or None if failed
        """
        try:
            logger.debug("Capturing CAPTCHA image...")
            
            # Take screenshot of the CAPTCHA element
            screenshot_bytes = await element.screenshot()
            
            # Convert to base64
            image_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            logger.debug(f"CAPTCHA image captured successfully ({len(image_base64)} characters)")
            return image_base64
            
        except Exception as e:
            logger.error(f"Error capturing CAPTCHA image: {e}")
            return None
    
    def submit_captcha_to_service(self, image_base64: str) -> Optional[str]:
        """
        Submit CAPTCHA to solving service.
        
        Args:
            image_base64: Base64 encoded CAPTCHA image
            
        Returns:
            Task ID from the service or None if failed
        """
        try:
            logger.debug("Submitting CAPTCHA to solving service...")
            
            # Prepare request data
            data = {
                'key': self.api_key,
                'method': 'base64',
                'body': image_base64,
                'json': 1
            }
            
            # Submit to 2Captcha
            response = requests.post(f"{self.service_url}/in.php", data=data, timeout=30)
            result = response.json()
            
            if result.get('status') == 1:
                task_id = result.get('request')
                logger.info(f"CAPTCHA submitted successfully. Task ID: {task_id}")
                return task_id
            else:
                logger.error(f"Failed to submit CAPTCHA: {result.get('error_text', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error submitting CAPTCHA: {e}")
            return None
    
    def get_captcha_solution(self, task_id: str) -> Optional[str]:
        """
        Get CAPTCHA solution from service.
        
        Args:
            task_id: Task ID from submission
            
        Returns:
            CAPTCHA solution text or None if failed
        """
        try:
            logger.debug(f"Polling for CAPTCHA solution (Task ID: {task_id})")
            
            start_time = time.time()
            
            while time.time() - start_time < self.solve_timeout:
                # Check solution status
                params = {
                    'key': self.api_key,
                    'action': 'get',
                    'id': task_id,
                    'json': 1
                }
                
                response = requests.get(f"{self.service_url}/res.php", params=params, timeout=30)
                result = response.json()
                
                if result.get('status') == 1:
                    solution = result.get('request')
                    logger.info(f"CAPTCHA solved successfully: {solution}")
                    return solution
                elif result.get('error_text') == 'CAPCHA_NOT_READY':
                    logger.debug("CAPTCHA not ready yet, continuing to poll...")
                    time.sleep(self.poll_interval)
                else:
                    logger.error(f"CAPTCHA solving failed: {result.get('error_text', 'Unknown error')}")
                    return None
            
            logger.error("CAPTCHA solving timed out")
            return None
            
        except Exception as e:
            logger.error(f"Error getting CAPTCHA solution: {e}")
            return None
    
    async def solve_captcha_on_page(self, page: Page) -> bool:
        """
        Detect and solve CAPTCHA on the current page.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if CAPTCHA was solved successfully, False otherwise
        """
        try:
            if not self.is_configured():
                logger.warning("CAPTCHA solver not configured. Skipping CAPTCHA solving.")
                return False
            
            logger.info("Starting CAPTCHA solving process...")
            
            # Step 1: Detect CAPTCHA
            captcha_info = await self.detect_captcha(page)
            if not captcha_info:
                logger.debug("No CAPTCHA detected on page")
                return True  # No CAPTCHA means success
            
            # Step 2: Handle different CAPTCHA types
            if captcha_info["type"] == "image":
                return await self._solve_image_captcha(page, captcha_info)
            elif captcha_info["type"] == "text":
                logger.warning("Text-based CAPTCHA detection not implemented yet")
                return False
            elif captcha_info["type"] == "input":
                return await self._solve_input_captcha(page, captcha_info)
            else:
                logger.error(f"Unknown CAPTCHA type: {captcha_info['type']}")
                return False
                
        except Exception as e:
            logger.error(f"Error in CAPTCHA solving process: {e}")
            return False
    
    async def _solve_image_captcha(self, page: Page, captcha_info: Dict[str, Any]) -> bool:
        """
        Solve image-based CAPTCHA.
        
        Args:
            page: Playwright page object
            captcha_info: CAPTCHA detection information
            
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            # Step 1: Capture CAPTCHA image
            image_base64 = await self.capture_captcha_image(page, captcha_info["element"])
            if not image_base64:
                logger.error("Failed to capture CAPTCHA image")
                return False
            
            # Step 2: Submit to solving service
            task_id = self.submit_captcha_to_service(image_base64)
            if not task_id:
                logger.error("Failed to submit CAPTCHA to solving service")
                return False
            
            # Step 3: Get solution
            solution = self.get_captcha_solution(task_id)
            if not solution:
                logger.error("Failed to get CAPTCHA solution")
                return False
            
            # Step 4: Find input field and submit solution
            input_selectors = [
                "input[name*='captcha']",
                "input[id*='captcha']",
                "#captchacharacters",
                "#auth-captcha-guess"
            ]
            
            input_element = None
            for selector in input_selectors:
                input_element = await page.query_selector(selector)
                if input_element:
                    break
            
            if not input_element:
                logger.error("Could not find CAPTCHA input field")
                return False
            
            # Type the solution
            await input_element.fill(solution)
            logger.info(f"CAPTCHA solution entered: {solution}")
            
            # Step 5: Submit the form
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "#auth-captcha-submit-button",
                ".captcha-submit"
            ]
            
            submit_element = None
            for selector in submit_selectors:
                submit_element = await page.query_selector(selector)
                if submit_element:
                    break
            
            if submit_element:
                await submit_element.click()
                logger.info("CAPTCHA form submitted")
                
                # Wait for page to process
                await page.wait_for_timeout(3000)
                
                # Check if CAPTCHA was solved successfully
                new_captcha_info = await self.detect_captcha(page)
                if not new_captcha_info:
                    logger.info("CAPTCHA solved successfully!")
                    return True
                else:
                    logger.warning("CAPTCHA still present after submission")
                    return False
            else:
                logger.error("Could not find CAPTCHA submit button")
                return False
                
        except Exception as e:
            logger.error(f"Error solving image CAPTCHA: {e}")
            return False
    
    async def _solve_input_captcha(self, page: Page, captcha_info: Dict[str, Any]) -> bool:
        """
        Solve input-based CAPTCHA (when input field is detected but image is elsewhere).
        
        Args:
            page: Playwright page object
            captcha_info: CAPTCHA detection information
            
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            # Look for associated image
            image_selectors = [
                "img[alt*='captcha']",
                "img[src*='captcha']",
                ".captcha-image",
                "#auth-captcha-image"
            ]
            
            image_element = None
            for selector in image_selectors:
                image_element = await page.query_selector(selector)
                if image_element:
                    break
            
            if not image_element:
                logger.error("Could not find CAPTCHA image for input field")
                return False
            
            # Use the image solving method
            fake_captcha_info = {
                "type": "image",
                "element": image_element,
                "selector": "dynamic",
                "method": "input_associated"
            }
            
            return await self._solve_image_captcha(page, fake_captcha_info)
            
        except Exception as e:
            logger.error(f"Error solving input CAPTCHA: {e}")
            return False

# Global CAPTCHA solver instance
captcha_solver = CaptchaSolver()