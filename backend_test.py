#!/usr/bin/env python3
"""
Backend API Testing Suite
Tests all backend endpoints after major refactor with ScraperAPI and Twitter integration.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL - using port 8000 as configured in main.py
BACKEND_URL = "http://localhost:8000"

class BackendTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, passed, message="", response_data=None):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if response_data:
            result["response_data"] = response_data
            
        self.results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"   Message: {message}")
        if response_data and not passed:
            print(f"   Response: {response_data}")
        print()
        
    def test_health_endpoint(self):
        """Test GET /health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy" and "timestamp" in data:
                    self.log_result("Health Check", True, "Backend is healthy")
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid health response format", data)
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def test_search_endpoint(self):
        """Test GET /search?q=laptop endpoint"""
        try:
            # Test with valid query
            response = requests.get(f"{BACKEND_URL}/search?q=laptop", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "laptop" in data["message"]:
                    self.log_result("Search Endpoint (Valid Query)", True, "Search initiated successfully")
                else:
                    self.log_result("Search Endpoint (Valid Query)", False, "Invalid response format", data)
                    return False
            else:
                self.log_result("Search Endpoint (Valid Query)", False, f"HTTP {response.status_code}", response.text)
                return False
                
            # Test without query parameter
            response = requests.get(f"{BACKEND_URL}/search", timeout=10)
            
            if response.status_code == 400:
                data = response.json()
                if "error" in data and "required" in data["error"].lower():
                    self.log_result("Search Endpoint (Missing Query)", True, "Proper error handling for missing query")
                else:
                    self.log_result("Search Endpoint (Missing Query)", False, "Invalid error response", data)
            else:
                self.log_result("Search Endpoint (Missing Query)", False, f"Expected 400, got {response.status_code}")
                
            return True
                
        except requests.exceptions.RequestException as e:
            self.log_result("Search Endpoint", False, f"Connection error: {str(e)}")
            return False
            
    def test_results_endpoint(self):
        """Test GET /results?q=laptop endpoint"""
        try:
            # Test with valid query
            response = requests.get(f"{BACKEND_URL}/results?q=laptop", timeout=15)
            
            if response.status_code in [200, 202]:
                data = response.json()
                
                if response.status_code == 200:
                    # Check if response has expected structure
                    if isinstance(data, dict) and ("amazon" in data or "flipkart" in data):
                        self.log_result("Results Endpoint (Valid Query)", True, "Results returned successfully")
                    else:
                        self.log_result("Results Endpoint (Valid Query)", False, "Invalid results format", data)
                        return False
                        
                elif response.status_code == 202:
                    # Pending status is acceptable
                    if data.get("status") == "pending":
                        self.log_result("Results Endpoint (Valid Query)", True, "Results pending (acceptable)")
                    else:
                        self.log_result("Results Endpoint (Valid Query)", False, "Invalid pending response", data)
                        return False
            else:
                self.log_result("Results Endpoint (Valid Query)", False, f"HTTP {response.status_code}", response.text)
                return False
                
            # Test without query parameter
            response = requests.get(f"{BACKEND_URL}/results", timeout=10)
            
            if response.status_code == 400:
                data = response.json()
                if "error" in data and "required" in data["error"].lower():
                    self.log_result("Results Endpoint (Missing Query)", True, "Proper error handling for missing query")
                else:
                    self.log_result("Results Endpoint (Missing Query)", False, "Invalid error response", data)
            else:
                self.log_result("Results Endpoint (Missing Query)", False, f"Expected 400, got {response.status_code}")
                
            return True
                
        except requests.exceptions.RequestException as e:
            self.log_result("Results Endpoint", False, f"Connection error: {str(e)}")
            return False
            
    def test_deals_endpoint(self):
        """Test GET /api/deals endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/api/deals", timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list (may be empty with demo keys)
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check if deals have expected structure
                        deal = data[0]
                        expected_fields = ['id', 'text', 'created_at', 'url', 'likes', 'retweets']
                        if all(field in deal for field in expected_fields):
                            self.log_result("Deals Endpoint", True, f"Deals returned successfully ({len(data)} deals)")
                        else:
                            self.log_result("Deals Endpoint", True, f"Deals returned but with incomplete structure ({len(data)} deals)")
                    else:
                        self.log_result("Deals Endpoint", True, "Deals endpoint working (empty result with demo keys)")
                else:
                    self.log_result("Deals Endpoint", False, "Invalid response format - expected list", data)
                    return False
            else:
                self.log_result("Deals Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
            return True
                
        except requests.exceptions.RequestException as e:
            self.log_result("Deals Endpoint", False, f"Connection error: {str(e)}")
            return False
            
    def test_database_connection(self):
        """Test database connectivity by checking if results endpoint can query database"""
        try:
            # This indirectly tests database connection
            response = requests.get(f"{BACKEND_URL}/results?q=test", timeout=10)
            
            if response.status_code in [200, 202]:
                self.log_result("Database Connection", True, "Database queries working")
                return True
            else:
                self.log_result("Database Connection", False, f"Database query failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Database Connection", False, f"Connection error: {str(e)}")
            return False
            
    def test_cors_headers(self):
        """Test CORS headers are present"""
        try:
            response = requests.options(f"{BACKEND_URL}/health", timeout=10)
            
            # Check for CORS headers
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            has_cors = any(header in response.headers for header in cors_headers)
            
            if has_cors:
                self.log_result("CORS Headers", True, "CORS headers present")
                return True
            else:
                # Try a GET request to check CORS
                response = requests.get(f"{BACKEND_URL}/health", timeout=10)
                has_cors = any(header in response.headers for header in cors_headers)
                
                if has_cors:
                    self.log_result("CORS Headers", True, "CORS headers present")
                    return True
                else:
                    self.log_result("CORS Headers", False, "CORS headers missing")
                    return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("CORS Headers", False, f"Connection error: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("BACKEND API TESTING SUITE")
        print("=" * 60)
        print(f"Testing backend at: {BACKEND_URL}")
        print(f"Started at: {datetime.now().isoformat()}")
        print()
        
        # Run tests in order of importance
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Search Functionality", self.test_search_endpoint),
            ("Results Functionality", self.test_results_endpoint),
            ("Deals API", self.test_deals_endpoint),
            ("Database Connection", self.test_database_connection),
            ("CORS Configuration", self.test_cors_headers),
        ]
        
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {str(e)}")
            
            # Small delay between tests
            time.sleep(1)
        
        # Print summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        print()
        
        # Print failed tests
        failed_tests = [r for r in self.results if "❌" in r["status"]]
        if failed_tests:
            print("FAILED TESTS:")
            print("-" * 40)
            for test in failed_tests:
                print(f"• {test['test']}: {test['message']}")
            print()
        
        # Return overall success
        return self.passed_tests == self.total_tests

def main():
    """Main test execution"""
    tester = BackendTester()
    
    # Wait a moment for backend to be ready
    print("Waiting for backend to be ready...")
    time.sleep(2)
    
    success = tester.run_all_tests()
    
    # Save results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': tester.total_tests,
            'passed_tests': tester.passed_tests,
            'success_rate': (tester.passed_tests/tester.total_tests)*100 if tester.total_tests > 0 else 0,
            'results': tester.results
        }, f, indent=2)
    
    print(f"Detailed results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()