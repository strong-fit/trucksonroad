#!/usr/bin/env python3

import requests
import sys
from datetime import datetime, timedelta
import json

class StrongFoodAPITester:
    def __init__(self, base_url="https://hellpetrol-staging.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, cookies=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {method} {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers, cookies=cookies)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers, cookies=cookies)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers, cookies=cookies)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers, cookies=cookies)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) <= 5:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) <= 3:
                        print(f"   Response: {len(response_data)} items")
                except:
                    pass
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text[:200]}")

            return success, response.json() if response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_public_endpoints(self):
        """Test public endpoints that don't require authentication"""
        print("\n" + "="*50)
        print("TESTING PUBLIC ENDPOINTS")
        print("="*50)
        
        # Test trucks endpoint
        success, trucks = self.run_test("Get Trucks", "GET", "trucks", 200)
        if success and isinstance(trucks, list):
            print(f"   Found {len(trucks)} trucks")
            if len(trucks) > 0:
                print(f"   First truck: {trucks[0].get('name_de', 'Unknown')}")
        
        # Test individual truck
        if trucks and len(trucks) > 0:
            truck_slug = trucks[0].get('slug', 'burger-truck')
            self.run_test(f"Get Truck {truck_slug}", "GET", f"trucks/{truck_slug}", 200)
        
        # Test FAQs
        success, faqs = self.run_test("Get FAQs", "GET", "faqs", 200)
        if success and isinstance(faqs, list):
            print(f"   Found {len(faqs)} FAQs")
        
        # Test availability
        self.run_test("Get Availability", "GET", "availability", 200)
        
        # Test specific date availability
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.run_test(f"Check Date {tomorrow}", "GET", f"availability/{tomorrow}", 200)

    def test_inquiry_endpoints(self):
        """Test inquiry creation endpoints"""
        print("\n" + "="*50)
        print("TESTING INQUIRY ENDPOINTS")
        print("="*50)
        
        # Test regular inquiry
        inquiry_data = {
            "first_name": "Test",
            "last_name": "User",
            "company": "Test Company",
            "email": "test@example.com",
            "phone": "+41791234567",
            "event_date": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            "event_time": "12:00 - 20:00",
            "location": "Zurich",
            "guest_count": 100,
            "event_type": "Firmenevent",
            "indoor_outdoor": "Outdoor",
            "selected_trucks": ["Burger Truck"],
            "extras": ["Getränke"],
            "budget": "5000-10000 CHF",
            "remarks": "Test inquiry",
            "is_organizer": False,
            "privacy_accepted": True,
            "customer_type": "Privatkunde"
        }
        
        success, response = self.run_test("Create Inquiry", "POST", "inquiries", 200, inquiry_data)
        if success:
            self.inquiry_id = response.get('id')
            print(f"   Created inquiry with ID: {self.inquiry_id}")
        
        # Test quick inquiry
        quick_inquiry_data = {
            "name": "Quick Test",
            "event_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
            "location": "Basel",
            "guest_count": 50,
            "concept": "Street Food",
            "email": "quick@example.com",
            "phone": "+41791234568"
        }
        
        self.run_test("Create Quick Inquiry", "POST", "quick-inquiry", 200, quick_inquiry_data)

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n" + "="*50)
        print("TESTING AUTH ENDPOINTS")
        print("="*50)
        
        # Test login with correct credentials
        login_data = {
            "email": "admin@strongfood.ch",
            "password": "StrongFood2026!"
        }
        
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, login_data)
        if success:
            print(f"   Logged in as: {response.get('email')} (Role: {response.get('role')})")
            # Store cookies for subsequent requests
            self.admin_cookies = self.session.cookies
        
        # Test login with wrong credentials
        wrong_login_data = {
            "email": "admin@strongfood.ch",
            "password": "wrongpassword"
        }
        
        self.run_test("Wrong Password Login", "POST", "auth/login", 401, wrong_login_data)
        
        # Test /me endpoint
        if hasattr(self, 'admin_cookies'):
            self.run_test("Get Current User", "GET", "auth/me", 200, cookies=self.admin_cookies)
        
        # Test refresh token
        if hasattr(self, 'admin_cookies'):
            self.run_test("Refresh Token", "POST", "auth/refresh", 200, cookies=self.admin_cookies)

    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        print("\n" + "="*50)
        print("TESTING ADMIN ENDPOINTS")
        print("="*50)
        
        if not hasattr(self, 'admin_cookies'):
            print("❌ Skipping admin tests - no admin session")
            return
        
        # Test admin stats
        success, stats = self.run_test("Admin Stats", "GET", "admin/stats", 200, cookies=self.admin_cookies)
        if success:
            print(f"   Stats: {stats}")
        
        # Test admin inquiries
        success, inquiries = self.run_test("Admin Get Inquiries", "GET", "admin/inquiries", 200, cookies=self.admin_cookies)
        if success and isinstance(inquiries, list):
            print(f"   Found {len(inquiries)} inquiries")
            if len(inquiries) > 0:
                inquiry_id = inquiries[0].get('id')
                if inquiry_id:
                    # Test get single inquiry
                    self.run_test("Admin Get Single Inquiry", "GET", f"admin/inquiries/{inquiry_id}", 200, cookies=self.admin_cookies)
                    
                    # Test update inquiry status
                    update_data = {
                        "status": "in_review",
                        "internal_notes": "Test note from API test"
                    }
                    self.run_test("Admin Update Inquiry", "PUT", f"admin/inquiries/{inquiry_id}", 200, update_data, cookies=self.admin_cookies)
        
        # Test admin trucks
        success, trucks = self.run_test("Admin Get Trucks", "GET", "admin/trucks", 200, cookies=self.admin_cookies)
        if success and isinstance(trucks, list) and len(trucks) > 0:
            truck_slug = trucks[0].get('slug')
            if truck_slug:
                update_truck_data = {"is_active": True}
                self.run_test("Admin Update Truck", "PUT", f"admin/trucks/{truck_slug}", 200, update_truck_data, cookies=self.admin_cookies)
        
        # Test admin calendar
        self.run_test("Admin Get Calendar", "GET", "admin/calendar", 200, cookies=self.admin_cookies)
        
        # Test create calendar block
        block_data = {
            "truck_slug": "burger-truck",
            "date": (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
            "status": "blocked",
            "notes": "API test block"
        }
        success, block_response = self.run_test("Admin Create Calendar Block", "POST", "admin/calendar", 200, block_data, cookies=self.admin_cookies)
        
        # Test admin settings
        self.run_test("Admin Get Settings", "GET", "admin/settings", 200, cookies=self.admin_cookies)
        
        settings_data = {
            "company_name": "StrongFood",
            "email_notifications": True,
            "notification_email": "admin@strongfood.ch",
            "whatsapp_number": "+41791234567"
        }
        self.run_test("Admin Update Settings", "PUT", "admin/settings", 200, settings_data, cookies=self.admin_cookies)

    def test_error_cases(self):
        """Test error handling"""
        print("\n" + "="*50)
        print("TESTING ERROR CASES")
        print("="*50)
        
        # Test non-existent truck
        self.run_test("Get Non-existent Truck", "GET", "trucks/non-existent", 404)
        
        # Test admin endpoint without auth
        self.run_test("Admin Stats Without Auth", "GET", "admin/stats", 401)
        
        # Test invalid inquiry data
        invalid_inquiry = {
            "first_name": "",  # Required field empty
            "email": "invalid-email",  # Invalid email
            "guest_count": "not-a-number"  # Invalid number
        }
        self.run_test("Invalid Inquiry Data", "POST", "inquiries", 422, invalid_inquiry)

    def test_logout(self):
        """Test logout"""
        print("\n" + "="*50)
        print("TESTING LOGOUT")
        print("="*50)
        
        if hasattr(self, 'admin_cookies'):
            self.run_test("Admin Logout", "POST", "auth/logout", 200, cookies=self.admin_cookies)
            
            # Test that protected endpoint now fails
            self.run_test("Admin Stats After Logout", "GET", "admin/stats", 401, cookies=self.admin_cookies)

def main():
    print("🚀 Starting StrongFood API Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = StrongFoodAPITester()
    
    try:
        # Run all test suites
        tester.test_public_endpoints()
        tester.test_inquiry_endpoints()
        tester.test_auth_endpoints()
        tester.test_admin_endpoints()
        tester.test_error_cases()
        tester.test_logout()
        
        # Print final results
        print("\n" + "="*50)
        print("TEST RESULTS")
        print("="*50)
        print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
        success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        
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