#!/usr/bin/env python3

import requests
import sys
from datetime import datetime
import json
from bs4 import BeautifulSoup

class TrucksOnRoadAPITester:
    def __init__(self, base_url="https://trucks-on-road.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_api_test(self, name, endpoint, expected_status=200):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: GET {url}")
        
        try:
            response = self.session.get(url)
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Show response details for key endpoints
                if response.content:
                    try:
                        response_data = response.json()
                        if isinstance(response_data, list):
                            print(f"   Response: {len(response_data)} items")
                            if len(response_data) > 0 and isinstance(response_data[0], dict):
                                # Show first item keys for structure verification
                                keys = list(response_data[0].keys())
                                print(f"   First item keys: {keys[:5]}{'...' if len(keys) > 5 else ''}")
                        elif isinstance(response_data, dict):
                            keys = list(response_data.keys())
                            print(f"   Response keys: {keys[:5]}{'...' if len(keys) > 5 else ''}")
                    except:
                        print(f"   Response length: {len(response.content)} bytes")
                
                return True, response
            else:
                self.tests_passed += 0
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text[:200]}")
                return False, response

        except Exception as e:
            self.failed_tests.append(f"{name}: Exception - {str(e)}")
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def run_html_test(self, name, endpoint, expected_status=200):
        """Run a single HTML page test"""
        url = f"{self.base_url}{endpoint}"
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: GET {url}")
        
        try:
            response = self.session.get(url)
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return True, response
            else:
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                return False, response

        except Exception as e:
            self.failed_tests.append(f"{name}: Exception - {str(e)}")
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def verify_trucks_api_data(self, trucks_data):
        """Verify trucks API returns proper data structure"""
        if not isinstance(trucks_data, list):
            print(f"❌ Trucks API should return list, got {type(trucks_data)}")
            return False
        
        if len(trucks_data) == 0:
            print(f"❌ Trucks API returned empty list")
            return False
        
        # Check first truck has required fields
        first_truck = trucks_data[0]
        required_fields = ['slug', 'name_de', 'image']
        missing_fields = [field for field in required_fields if field not in first_truck]
        
        if missing_fields:
            print(f"❌ First truck missing fields: {missing_fields}")
            return False
        
        print(f"✅ Trucks data structure verified - {len(trucks_data)} trucks with required fields")
        return True

    def verify_faqs_api_data(self, faqs_data):
        """Verify FAQs API returns proper data structure"""
        if not isinstance(faqs_data, list):
            print(f"❌ FAQs API should return list, got {type(faqs_data)}")
            return False
        
        if len(faqs_data) == 0:
            print(f"❌ FAQs API returned empty list")
            return False
        
        print(f"✅ FAQs data structure verified - {len(faqs_data)} FAQs")
        return True

    def verify_structured_data_api(self, structured_data):
        """Verify structured data API returns valid JSON-LD"""
        if not isinstance(structured_data, dict):
            print(f"❌ Structured data should return dict, got {type(structured_data)}")
            return False
        
        required_fields = ['@context', '@type', 'name']
        missing_fields = [field for field in required_fields if field not in structured_data]
        
        if missing_fields:
            print(f"❌ Structured data missing fields: {missing_fields}")
            return False
        
        if structured_data.get('@context') != 'https://schema.org':
            print(f"❌ Invalid @context: {structured_data.get('@context')}")
            return False
        
        print(f"✅ Structured data JSON-LD verified - type: {structured_data.get('@type')}")
        return True

    def verify_html_seo_elements(self, name, html_content, expected_canonical, expected_jsonld_ids):
        """Verify HTML contains proper canonical tags and JSON-LD scripts"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check canonical tag
        canonical = soup.find('link', {'rel': 'canonical'})
        if not canonical:
            print(f"❌ {name}: No canonical tag found")
            return False
        
        canonical_href = canonical.get('href')
        if canonical_href != expected_canonical:
            print(f"❌ {name}: Wrong canonical URL - expected {expected_canonical}, got {canonical_href}")
            return False
        
        print(f"✅ {name}: Canonical tag verified - {canonical_href}")
        
        # Check JSON-LD scripts
        jsonld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        if not jsonld_scripts:
            print(f"❌ {name}: No JSON-LD scripts found")
            return False
        
        found_ids = []
        for script in jsonld_scripts:
            script_id = script.get('id')
            if script_id:
                found_ids.append(script_id)
        
        # Check if all expected JSON-LD IDs are present
        missing_ids = [id for id in expected_jsonld_ids if id not in found_ids]
        if missing_ids:
            print(f"❌ {name}: Missing JSON-LD scripts: {missing_ids}")
            print(f"   Found IDs: {found_ids}")
            return False
        
        print(f"✅ {name}: JSON-LD scripts verified - found {len(jsonld_scripts)} scripts")
        print(f"   Script IDs: {found_ids}")
        return True

    def test_backend_api_endpoints(self):
        """Test the backend API endpoints as specified in the German review request"""
        print("\n" + "="*60)
        print("TESTING BACKEND API ENDPOINTS")
        print("="*60)
        
        # 1. GET /api/trucks -> 200, liefert mehrere Trucks mit slug/name/image
        success, response = self.run_api_test("GET /api/trucks", "trucks")
        if success and response:
            try:
                trucks_data = response.json()
                self.verify_trucks_api_data(trucks_data)
            except:
                print("❌ Failed to parse trucks JSON response")
        
        # 2. GET /api/faqs -> 200, liefert FAQ-Daten
        success, response = self.run_api_test("GET /api/faqs", "faqs")
        if success and response:
            try:
                faqs_data = response.json()
                self.verify_faqs_api_data(faqs_data)
            except:
                print("❌ Failed to parse FAQs JSON response")
        
        # 3. GET /api/seo/structured-data -> 200, liefert valides JSON-LD
        success, response = self.run_api_test("GET /api/seo/structured-data", "seo/structured-data")
        if success and response:
            try:
                structured_data = response.json()
                self.verify_structured_data_api(structured_data)
            except:
                print("❌ Failed to parse structured data JSON response")

    def test_html_seo_endpoints(self):
        """Test the HTML endpoints for SEO elements as specified in the German review request"""
        print("\n" + "="*60)
        print("TESTING HTML SEO ENDPOINTS")
        print("="*60)
        
        # 4. GET /trucks -> 200, HTML enthält canonical und JSON-LD für ItemList/BreadcrumbList/layout-jsonld
        success, response = self.run_html_test("GET /trucks (HTML)", "/trucks")
        if success and response:
            expected_canonical = "https://trucksonroad.ch/trucks"
            expected_jsonld_ids = ["trucks-list-jsonld", "trucks-breadcrumb-jsonld", "layout-jsonld-0"]
            self.verify_html_seo_elements("Trucks Page", response.text, expected_canonical, expected_jsonld_ids)
        
        # 5. GET /faq -> 200, HTML enthält canonical und JSON-LD für FAQPage/BreadcrumbList/layout-jsonld
        success, response = self.run_html_test("GET /faq (HTML)", "/faq")
        if success and response:
            expected_canonical = "https://trucksonroad.ch/faq"
            expected_jsonld_ids = ["faq-jsonld", "faq-breadcrumb-jsonld", "layout-jsonld-0"]
            self.verify_html_seo_elements("FAQ Page", response.text, expected_canonical, expected_jsonld_ids)
        
        # 6. GET /trucks/burger-truck -> 200, HTML enthält canonical und truck-detail-jsonld/truck-breadcrumb-jsonld
        success, response = self.run_html_test("GET /trucks/burger-truck (HTML)", "/trucks/burger-truck")
        if success and response:
            expected_canonical = "https://trucksonroad.ch/trucks/burger-truck"
            expected_jsonld_ids = ["truck-detail-jsonld-burger-truck", "truck-breadcrumb-jsonld-burger-truck", "layout-jsonld-0"]
            self.verify_html_seo_elements("Truck Detail Page", response.text, expected_canonical, expected_jsonld_ids)

    def test_regression_check(self):
        """Test that no regression of public SEO/data endpoints is visible"""
        print("\n" + "="*60)
        print("TESTING REGRESSION CHECK - PUBLIC SEO/DATA ENDPOINTS")
        print("="*60)
        
        # Test additional public endpoints to ensure no regression
        self.run_api_test("GET /api/availability", "availability")
        self.run_api_test("GET /api/contact-info", "contact-info")
        self.run_api_test("GET /api/reviews", "reviews")
        self.run_api_test("GET /api/robots.txt", "robots.txt")
        self.run_api_test("GET /api/sitemap.xml", "sitemap.xml")

def main():
    print("🚀 Starting TrucksOnRoad API Tests")
    print("📋 Testing SSR-SEO Output as requested in German review")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = TrucksOnRoadAPITester()
    
    try:
        # Run all test suites as specified in the German review request
        tester.test_backend_api_endpoints()
        tester.test_html_seo_endpoints()
        tester.test_regression_check()
        
        # Print final results
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
        success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        if tester.failed_tests:
            print(f"\n❌ Failed tests:")
            for failed_test in tester.failed_tests:
                print(f"   - {failed_test}")
        
        if tester.tests_passed == tester.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())