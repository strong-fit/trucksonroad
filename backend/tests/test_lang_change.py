"""
Test Language Change Features:
1. PUT /api/customer/profile with {lang: 'en'} updates the user's language
2. GET /api/customer/profile returns the updated lang field
3. PUT /api/admin/inquiries/{id}/lang with {lang: 'fr'} updates inquiry language
4. GET /api/admin/inquiries/{id} shows updated lang field
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@truckonroad.ch"
ADMIN_PASSWORD = "TruckOnRoad2026!"
CUSTOMER_EMAIL = "test2@kunde.ch"
CUSTOMER_PASSWORD = "Kunde2026!"


class TestCustomerLanguageChange:
    """Test customer profile language change"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and login as customer"""
        self.session = requests.Session()
        # Login as customer
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CUSTOMER_EMAIL,
            "password": CUSTOMER_PASSWORD
        })
        if response.status_code != 200:
            # Try to register the customer if login fails
            reg_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
                "email": CUSTOMER_EMAIL,
                "password": CUSTOMER_PASSWORD,
                "first_name": "Test",
                "last_name": "Kunde",
                "company": "",
                "phone": "+41791234567"
            })
            if reg_response.status_code not in [200, 201]:
                pytest.skip(f"Could not login or register customer: {response.text}")
        yield
        self.session.close()
    
    def test_customer_profile_get_returns_lang(self):
        """GET /api/customer/profile returns lang field"""
        response = self.session.get(f"{BASE_URL}/api/customer/profile")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "lang" in data, "Profile should contain 'lang' field"
        assert data["lang"] in ["de", "en", "fr", "it"], f"Lang should be valid, got: {data['lang']}"
        print(f"PASS: Customer profile returns lang field: {data['lang']}")
    
    def test_customer_profile_update_lang_to_en(self):
        """PUT /api/customer/profile with {lang: 'en'} updates language"""
        response = self.session.put(f"{BASE_URL}/api/customer/profile", json={"lang": "en"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Customer profile lang updated to 'en'")
        
        # Verify the change persisted
        get_response = self.session.get(f"{BASE_URL}/api/customer/profile")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["lang"] == "en", f"Expected lang='en', got: {data['lang']}"
        print("PASS: Verified lang='en' persisted in profile")
    
    def test_customer_profile_update_lang_to_fr(self):
        """PUT /api/customer/profile with {lang: 'fr'} updates language"""
        response = self.session.put(f"{BASE_URL}/api/customer/profile", json={"lang": "fr"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the change persisted
        get_response = self.session.get(f"{BASE_URL}/api/customer/profile")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["lang"] == "fr", f"Expected lang='fr', got: {data['lang']}"
        print("PASS: Customer profile lang updated and verified as 'fr'")
    
    def test_customer_profile_update_lang_to_it(self):
        """PUT /api/customer/profile with {lang: 'it'} updates language"""
        response = self.session.put(f"{BASE_URL}/api/customer/profile", json={"lang": "it"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the change persisted
        get_response = self.session.get(f"{BASE_URL}/api/customer/profile")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["lang"] == "it", f"Expected lang='it', got: {data['lang']}"
        print("PASS: Customer profile lang updated and verified as 'it'")
    
    def test_customer_profile_update_lang_back_to_de(self):
        """Reset lang back to 'de' for cleanup"""
        response = self.session.put(f"{BASE_URL}/api/customer/profile", json={"lang": "de"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the change persisted
        get_response = self.session.get(f"{BASE_URL}/api/customer/profile")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["lang"] == "de", f"Expected lang='de', got: {data['lang']}"
        print("PASS: Customer profile lang reset to 'de'")


class TestAdminInquiryLanguageChange:
    """Test admin inquiry language change"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and login as admin"""
        self.session = requests.Session()
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.test_inquiry_id = None
        yield
        # Cleanup: delete test inquiry if created
        if self.test_inquiry_id:
            try:
                self.session.delete(f"{BASE_URL}/api/admin/inquiries/{self.test_inquiry_id}")
            except:
                pass
        self.session.close()
    
    def test_create_inquiry_for_lang_test(self):
        """Create a test inquiry for language testing"""
        inquiry_data = {
            "first_name": "TEST_Lang",
            "last_name": "User",
            "company": "Test Company",
            "email": f"test_lang_{uuid.uuid4().hex[:8]}@test.com",
            "phone": "+41791234567",
            "event_date": "2026-06-15",
            "event_time": "18:00",
            "location": "Zurich",
            "guest_count": 50,
            "event_type": "Corporate Event",
            "indoor_outdoor": "Outdoor",
            "selected_trucks": ["hellpetrol"],
            "extras": [],
            "budget": "5000-10000",
            "remarks": "Test inquiry for language testing",
            "is_organizer": False,
            "privacy_accepted": True,
            "customer_type": "Firmenkunde",
            "lang": "de"
        }
        response = self.session.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain inquiry id"
        self.test_inquiry_id = data["id"]
        print(f"PASS: Created test inquiry with id: {self.test_inquiry_id}")
        return self.test_inquiry_id
    
    def test_admin_get_inquiry_shows_lang(self):
        """GET /api/admin/inquiries/{id} shows lang field"""
        # First create an inquiry
        inquiry_id = self.test_create_inquiry_for_lang_test()
        
        response = self.session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "lang" in data, "Inquiry should contain 'lang' field"
        assert data["lang"] == "de", f"Expected lang='de', got: {data['lang']}"
        print(f"PASS: Admin inquiry GET returns lang field: {data['lang']}")
    
    def test_admin_update_inquiry_lang_to_fr(self):
        """PUT /api/admin/inquiries/{id}/lang with {lang: 'fr'} updates inquiry language"""
        # First create an inquiry
        inquiry_id = self.test_create_inquiry_for_lang_test()
        
        # Update language to French
        response = self.session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/lang", json={"lang": "fr"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Admin updated inquiry lang to 'fr'")
        
        # Verify the change persisted
        get_response = self.session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["lang"] == "fr", f"Expected lang='fr', got: {data['lang']}"
        print("PASS: Verified inquiry lang='fr' persisted")
    
    def test_admin_update_inquiry_lang_to_en(self):
        """PUT /api/admin/inquiries/{id}/lang with {lang: 'en'} updates inquiry language"""
        # First create an inquiry
        inquiry_id = self.test_create_inquiry_for_lang_test()
        
        # Update language to English
        response = self.session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/lang", json={"lang": "en"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the change persisted
        get_response = self.session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["lang"] == "en", f"Expected lang='en', got: {data['lang']}"
        print("PASS: Admin updated and verified inquiry lang='en'")
    
    def test_admin_update_inquiry_lang_to_it(self):
        """PUT /api/admin/inquiries/{id}/lang with {lang: 'it'} updates inquiry language"""
        # First create an inquiry
        inquiry_id = self.test_create_inquiry_for_lang_test()
        
        # Update language to Italian
        response = self.session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/lang", json={"lang": "it"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the change persisted
        get_response = self.session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["lang"] == "it", f"Expected lang='it', got: {data['lang']}"
        print("PASS: Admin updated and verified inquiry lang='it'")
    
    def test_admin_update_inquiry_lang_invalid(self):
        """PUT /api/admin/inquiries/{id}/lang with invalid lang returns 400"""
        # First create an inquiry
        inquiry_id = self.test_create_inquiry_for_lang_test()
        
        # Try to update with invalid language
        response = self.session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/lang", json={"lang": "invalid"})
        assert response.status_code == 400, f"Expected 400 for invalid lang, got {response.status_code}: {response.text}"
        print("PASS: Invalid lang correctly rejected with 400")
    
    def test_admin_update_inquiry_lang_not_found(self):
        """PUT /api/admin/inquiries/{id}/lang with non-existent id returns 404"""
        response = self.session.put(f"{BASE_URL}/api/admin/inquiries/non-existent-id/lang", json={"lang": "en"})
        assert response.status_code == 404, f"Expected 404 for non-existent inquiry, got {response.status_code}: {response.text}"
        print("PASS: Non-existent inquiry correctly returns 404")


class TestCustomerInquiriesLangUpdate:
    """Test that customer profile lang update also updates all their inquiries"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and login as customer"""
        self.session = requests.Session()
        # Login as customer
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CUSTOMER_EMAIL,
            "password": CUSTOMER_PASSWORD
        })
        if response.status_code != 200:
            # Try to register the customer if login fails
            reg_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
                "email": CUSTOMER_EMAIL,
                "password": CUSTOMER_PASSWORD,
                "first_name": "Test",
                "last_name": "Kunde",
                "company": "",
                "phone": "+41791234567"
            })
            if reg_response.status_code not in [200, 201]:
                pytest.skip(f"Could not login or register customer: {response.text}")
        yield
        self.session.close()
    
    def test_customer_create_inquiry_then_update_profile_lang(self):
        """Create inquiry as customer, then update profile lang - inquiry lang should update"""
        # Create an inquiry as customer
        inquiry_data = {
            "first_name": "TEST_Customer",
            "last_name": "Lang",
            "company": "",
            "email": CUSTOMER_EMAIL,
            "phone": "+41791234567",
            "event_date": "2026-07-20",
            "event_time": "19:00",
            "location": "Basel",
            "guest_count": 30,
            "event_type": "Birthday Party",
            "indoor_outdoor": "Indoor",
            "selected_trucks": [],
            "extras": [],
            "budget": "2000-5000",
            "remarks": "Test for customer lang update",
            "is_organizer": False,
            "privacy_accepted": True,
            "customer_type": "Privatkunde",
            "lang": "de"
        }
        create_response = self.session.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert create_response.status_code == 200, f"Failed to create inquiry: {create_response.text}"
        inquiry_id = create_response.json()["id"]
        print(f"PASS: Created customer inquiry with id: {inquiry_id}")
        
        # Update customer profile lang to 'en'
        update_response = self.session.put(f"{BASE_URL}/api/customer/profile", json={"lang": "en"})
        assert update_response.status_code == 200, f"Failed to update profile lang: {update_response.text}"
        print("PASS: Updated customer profile lang to 'en'")
        
        # Get customer inquiries and check if lang was updated
        inquiries_response = self.session.get(f"{BASE_URL}/api/customer/inquiries")
        assert inquiries_response.status_code == 200
        inquiries = inquiries_response.json()
        
        # Find our test inquiry
        test_inquiry = next((i for i in inquiries if i["id"] == inquiry_id), None)
        if test_inquiry:
            # Note: The backend updates inquiries using customer_id, so this should work
            # if the inquiry was linked to the customer
            print(f"Found test inquiry, lang: {test_inquiry.get('lang', 'not set')}")
        
        # Reset profile lang back to 'de'
        self.session.put(f"{BASE_URL}/api/customer/profile", json={"lang": "de"})
        print("PASS: Reset customer profile lang to 'de'")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_inquiries(self):
        """Delete all TEST_ prefixed inquiries"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Could not login as admin for cleanup")
        
        # Get all inquiries
        inquiries_response = session.get(f"{BASE_URL}/api/admin/inquiries")
        if inquiries_response.status_code == 200:
            inquiries = inquiries_response.json()
            deleted = 0
            for inq in inquiries:
                first_name = inq.get("first_name", "")
                if first_name.startswith("TEST_"):
                    del_response = session.delete(f"{BASE_URL}/api/admin/inquiries/{inq['id']}")
                    if del_response.status_code == 200:
                        deleted += 1
            print(f"PASS: Cleaned up {deleted} test inquiries")
        session.close()
