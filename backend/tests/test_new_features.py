"""
Backend API tests for TruckOnRoad new features:
- About page (no backend needed)
- Contact page with /api/contact-info endpoint
- Admin Settings with /api/admin/settings endpoints
- Inquiry API regression test
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

class TestPublicContactInfo:
    """Test public /api/contact-info endpoint"""
    
    def test_contact_info_returns_correct_data(self):
        """Contact info endpoint should return company details"""
        response = requests.get(f"{BASE_URL}/api/contact-info")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "company_name" in data, "Missing company_name"
        assert "address" in data, "Missing address"
        assert "phone" in data, "Missing phone"
        assert "email" in data, "Missing email"
        assert "whatsapp" in data, "Missing whatsapp"
        
        # Verify default values
        assert data["company_name"] == "TruckOnRoad", f"Expected TruckOnRoad, got {data['company_name']}"
        assert "Bahnhofstrasse 75" in data["address"], f"Address should contain Bahnhofstrasse 75, got {data['address']}"
        assert "8620 Wetzikon" in data["address"], f"Address should contain 8620 Wetzikon, got {data['address']}"
        assert data["phone"] == "+41 79 696 98 99", f"Expected +41 79 696 98 99, got {data['phone']}"
        assert data["email"] == "info@truckonroad.ch", f"Expected info@truckonroad.ch, got {data['email']}"
        print("✓ Contact info endpoint returns correct company data")


class TestInquiryAPI:
    """Regression test for inquiry submission"""
    
    def test_create_inquiry_success(self):
        """Test creating a new inquiry (contact form submission)"""
        payload = {
            "first_name": "TEST_Contact",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "+41 79 123 45 67",
            "event_date": "-",
            "location": "-",
            "guest_count": 0,
            "event_type": "Kontaktanfrage",
            "remarks": "Test message from contact form",
            "selected_trucks": [],
            "extras": [],
            "privacy_accepted": True
        }
        response = requests.post(f"{BASE_URL}/api/inquiries", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain inquiry id"
        assert "message" in data, "Response should contain message"
        print(f"✓ Inquiry created successfully with id: {data['id']}")
        return data["id"]
    
    def test_create_full_inquiry(self):
        """Test creating a full event inquiry"""
        payload = {
            "first_name": "TEST_Event",
            "last_name": "Organizer",
            "company": "Test Company",
            "email": "event@example.com",
            "phone": "+41 79 999 88 77",
            "event_date": "2026-06-15",
            "event_time": "18:00",
            "location": "Zürich",
            "guest_count": 150,
            "event_type": "Firmenevent",
            "indoor_outdoor": "Outdoor",
            "selected_trucks": ["burger-truck", "bowl-truck"],
            "extras": ["Getränke"],
            "budget": "5000-10000",
            "remarks": "Test event inquiry",
            "is_organizer": True,
            "privacy_accepted": True,
            "customer_type": "Firmenkunde"
        }
        response = requests.post(f"{BASE_URL}/api/inquiries", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        print(f"✓ Full event inquiry created with id: {data['id']}")


class TestAuthFlow:
    """Test authentication for admin endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.text}")
        return session
    
    def test_login_success(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert data["email"] == "admin@truckonroad.ch"
        assert data["role"] == "admin"
        print("✓ Admin login successful")
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected")


class TestAdminSettings:
    """Test admin settings endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.text}")
        return session
    
    def test_get_settings_requires_auth(self):
        """Settings endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/settings")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ Settings endpoint requires authentication")
    
    def test_get_settings_authenticated(self, auth_session):
        """Get settings with authentication"""
        response = auth_session.get(f"{BASE_URL}/api/admin/settings")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify company data fields
        assert "company_name" in data, "Missing company_name"
        assert "company_address" in data, "Missing company_address"
        assert "company_phone" in data, "Missing company_phone"
        assert "company_email" in data, "Missing company_email"
        assert "whatsapp_number" in data, "Missing whatsapp_number"
        
        # Verify SMTP fields
        assert "smtp_host" in data, "Missing smtp_host"
        assert "smtp_port" in data, "Missing smtp_port"
        assert "smtp_email" in data, "Missing smtp_email"
        assert "smtp_password" in data, "Missing smtp_password"
        assert "email_notifications" in data, "Missing email_notifications"
        
        print("✓ Settings endpoint returns all required fields")
        print(f"  Company: {data.get('company_name')}")
        print(f"  Address: {data.get('company_address')}")
        print(f"  SMTP Host: {data.get('smtp_host')}")
    
    def test_update_settings(self, auth_session):
        """Test updating settings"""
        # First get current settings
        get_response = auth_session.get(f"{BASE_URL}/api/admin/settings")
        assert get_response.status_code == 200
        original = get_response.json()
        
        # Update with test values
        update_payload = {
            "company_name": "TruckOnRoad",
            "company_address": "Bahnhofstrasse 75, 8620 Wetzikon",
            "company_phone": "+41 79 696 98 99",
            "company_email": "info@truckonroad.ch",
            "whatsapp_number": "+41796969899",
            "email_notifications": False,
            "notification_email": "",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_email": "",
            "smtp_password": ""
        }
        
        update_response = auth_session.put(f"{BASE_URL}/api/admin/settings", json=update_payload)
        assert update_response.status_code == 200, f"Update failed: {update_response.text}"
        
        # Verify update persisted
        verify_response = auth_session.get(f"{BASE_URL}/api/admin/settings")
        assert verify_response.status_code == 200
        updated = verify_response.json()
        
        assert updated["company_name"] == "TruckOnRoad"
        assert updated["company_address"] == "Bahnhofstrasse 75, 8620 Wetzikon"
        print("✓ Settings update and persistence verified")
    
    def test_test_email_endpoint(self, auth_session):
        """Test the test-email endpoint exists and requires email"""
        # Test without email
        response = auth_session.post(f"{BASE_URL}/api/admin/settings/test-email", json={})
        assert response.status_code == 400, f"Expected 400 without email, got {response.status_code}"
        
        # Test with email (will log warning since SMTP not configured)
        response = auth_session.post(f"{BASE_URL}/api/admin/settings/test-email", json={"to": "test@example.com"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        print("✓ Test email endpoint works (SMTP not configured - expected)")


class TestAdminInquiries:
    """Regression test for admin inquiries"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.text}")
        return session
    
    def test_get_inquiries(self, auth_session):
        """Test getting all inquiries"""
        response = auth_session.get(f"{BASE_URL}/api/admin/inquiries")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list of inquiries"
        print(f"✓ Retrieved {len(data)} inquiries")


class TestPublicEndpoints:
    """Test other public endpoints still work"""
    
    def test_trucks_endpoint(self):
        """Test trucks endpoint"""
        response = requests.get(f"{BASE_URL}/api/trucks")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 6, f"Expected at least 6 trucks, got {len(data)}"
        print(f"✓ Trucks endpoint returns {len(data)} trucks")
    
    def test_faqs_endpoint(self):
        """Test FAQs endpoint"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ FAQs endpoint returns {len(data)} FAQs")
    
    def test_availability_endpoint(self):
        """Test availability endpoint"""
        response = requests.get(f"{BASE_URL}/api/availability")
        assert response.status_code == 200
        print("✓ Availability endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
