"""
Test Refactored Backend - Post-Refactoring Verification
Tests all API endpoints to ensure the refactoring from single server.py to modular architecture
didn't break any functionality.

Modules tested:
- routes/auth_routes.py (Auth endpoints)
- routes/public.py (Public endpoints)
- routes/customer.py (Customer portal endpoints)
- routes/admin.py (Admin endpoints)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============================================================================
# AUTH ENDPOINTS (routes/auth_routes.py)
# ============================================================================

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_admin_login(self):
        """POST /api/auth/login - Admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["email"] == "admin@truckonroad.ch"
        assert data["role"] == "admin"
        assert "id" in data
        print("✓ POST /api/auth/login (admin) - 200 OK")
    
    def test_customer_login(self):
        """POST /api/auth/login - Customer login"""
        # First register a customer
        session = requests.Session()
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": "test_refactor@kunde.ch",
            "password": "TestPass2026!",
            "first_name": "Test",
            "last_name": "Refactor"
        })
        # May already exist, that's ok
        
        # Now login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test_refactor@kunde.ch",
            "password": "TestPass2026!"
        })
        if response.status_code == 200:
            data = response.json()
            assert data["role"] == "customer"
            print("✓ POST /api/auth/login (customer) - 200 OK")
        else:
            # Try with existing test customer
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": "test2@kunde.ch",
                "password": "Kunde2026!"
            })
            assert response.status_code == 200, f"Customer login failed: {response.text}"
            print("✓ POST /api/auth/login (customer) - 200 OK (using test2@kunde.ch)")
    
    def test_register_customer(self):
        """POST /api/auth/register - Register new customer"""
        import uuid
        unique_email = f"test_{uuid.uuid4().hex[:8]}@test.ch"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass2026!",
            "first_name": "TEST_New",
            "last_name": "Customer"
        })
        assert response.status_code == 200, f"Register failed: {response.text}"
        data = response.json()
        assert data["email"] == unique_email
        assert data["role"] == "customer"
        print(f"✓ POST /api/auth/register - 200 OK (created {unique_email})")
    
    def test_auth_me(self):
        """GET /api/auth/me - Get current user"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert data["email"] == "admin@truckonroad.ch"
        print("✓ GET /api/auth/me - 200 OK")
    
    def test_auth_refresh(self):
        """POST /api/auth/refresh - Refresh token"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200
        
        response = session.post(f"{BASE_URL}/api/auth/refresh")
        assert response.status_code == 200, f"Refresh failed: {response.text}"
        data = response.json()
        assert data["message"] == "Refreshed"
        print("✓ POST /api/auth/refresh - 200 OK")
    
    def test_auth_logout(self):
        """POST /api/auth/logout - Logout"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200
        
        response = session.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200, f"Logout failed: {response.text}"
        data = response.json()
        assert data["message"] == "Logged out"
        print("✓ POST /api/auth/logout - 200 OK")


# ============================================================================
# PUBLIC ENDPOINTS (routes/public.py)
# ============================================================================

class TestPublicEndpoints:
    """Test public endpoints"""
    
    def test_get_trucks(self):
        """GET /api/trucks - Get all trucks"""
        response = requests.get(f"{BASE_URL}/api/trucks")
        assert response.status_code == 200, f"Get trucks failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Verify truck structure
        truck = data[0]
        assert "slug" in truck
        assert "name_de" in truck
        print(f"✓ GET /api/trucks - 200 OK ({len(data)} trucks)")
    
    def test_get_truck_by_slug(self):
        """GET /api/trucks/{slug} - Get truck by slug"""
        response = requests.get(f"{BASE_URL}/api/trucks/burger-truck")
        assert response.status_code == 200, f"Get truck failed: {response.text}"
        data = response.json()
        assert data["slug"] == "burger-truck"
        assert "name_de" in data
        assert "description_de" in data
        print("✓ GET /api/trucks/burger-truck - 200 OK")
    
    def test_get_faqs(self):
        """GET /api/faqs - Get FAQs"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200, f"Get FAQs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        faq = data[0]
        assert "question_de" in faq
        assert "answer_de" in faq
        print(f"✓ GET /api/faqs - 200 OK ({len(data)} FAQs)")
    
    def test_get_availability(self):
        """GET /api/availability - Get availability"""
        response = requests.get(f"{BASE_URL}/api/availability")
        assert response.status_code == 200, f"Get availability failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/availability - 200 OK ({len(data)} blocks)")
    
    def test_get_contact_info(self):
        """GET /api/contact-info - Get contact info"""
        response = requests.get(f"{BASE_URL}/api/contact-info")
        assert response.status_code == 200, f"Get contact info failed: {response.text}"
        data = response.json()
        assert "company_name" in data
        assert "phone" in data
        assert "email" in data
        print("✓ GET /api/contact-info - 200 OK")
    
    def test_get_reviews(self):
        """GET /api/reviews - Get public reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200, f"Get reviews failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/reviews - 200 OK ({len(data)} reviews)")
    
    def test_get_structured_data(self):
        """GET /api/seo/structured-data - Get SEO structured data"""
        response = requests.get(f"{BASE_URL}/api/seo/structured-data")
        assert response.status_code == 200, f"Get structured data failed: {response.text}"
        data = response.json()
        assert "@context" in data
        assert data["@type"] == "FoodEstablishment"
        print("✓ GET /api/seo/structured-data - 200 OK")
    
    def test_get_robots_txt(self):
        """GET /api/robots.txt - Get robots.txt"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200, f"Get robots.txt failed: {response.text}"
        assert "User-agent" in response.text
        assert "Sitemap" in response.text
        print("✓ GET /api/robots.txt - 200 OK")
    
    def test_get_sitemap(self):
        """GET /api/sitemap.xml - Get sitemap"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Get sitemap failed: {response.text}"
        assert "<?xml" in response.text
        assert "<urlset" in response.text
        print("✓ GET /api/sitemap.xml - 200 OK")
    
    def test_get_agenda(self):
        """GET /api/agenda - Get public agenda"""
        response = requests.get(f"{BASE_URL}/api/agenda")
        assert response.status_code == 200, f"Get agenda failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/agenda - 200 OK ({len(data)} events)")
    
    def test_download_veranstalter_pdf(self):
        """GET /api/download/veranstalter-pdf - Download PDF"""
        response = requests.get(f"{BASE_URL}/api/download/veranstalter-pdf")
        assert response.status_code == 200, f"Download PDF failed: {response.text}"
        assert "application/pdf" in response.headers.get("content-type", "")
        assert response.content[:4] == b'%PDF'
        print("✓ GET /api/download/veranstalter-pdf - 200 OK")


# ============================================================================
# CUSTOMER ENDPOINTS (routes/customer.py)
# ============================================================================

class TestCustomerEndpoints:
    """Test customer portal endpoints"""
    
    @pytest.fixture(scope="class")
    def customer_session(self):
        """Create authenticated customer session"""
        session = requests.Session()
        # Try test2@kunde.ch first
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test2@kunde.ch",
            "password": "Kunde2026!"
        })
        if response.status_code != 200:
            # Register new customer
            import uuid
            email = f"test_cust_{uuid.uuid4().hex[:6]}@test.ch"
            session.post(f"{BASE_URL}/api/auth/register", json={
                "email": email,
                "password": "TestPass2026!",
                "first_name": "Test",
                "last_name": "Customer"
            })
        return session
    
    def test_customer_get_inquiries(self, customer_session):
        """GET /api/customer/inquiries - Get customer inquiries"""
        response = customer_session.get(f"{BASE_URL}/api/customer/inquiries")
        assert response.status_code == 200, f"Get inquiries failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/customer/inquiries - 200 OK ({len(data)} inquiries)")
    
    def test_customer_get_profile(self, customer_session):
        """GET /api/customer/profile - Get customer profile"""
        response = customer_session.get(f"{BASE_URL}/api/customer/profile")
        assert response.status_code == 200, f"Get profile failed: {response.text}"
        data = response.json()
        assert "email" in data
        assert "lang" in data
        print("✓ GET /api/customer/profile - 200 OK")
    
    def test_customer_update_profile_lang(self, customer_session):
        """PUT /api/customer/profile - Update language"""
        response = customer_session.put(f"{BASE_URL}/api/customer/profile", json={
            "lang": "en"
        })
        assert response.status_code == 200, f"Update profile failed: {response.text}"
        
        # Verify
        profile = customer_session.get(f"{BASE_URL}/api/customer/profile").json()
        assert profile["lang"] == "en"
        
        # Reset to German
        customer_session.put(f"{BASE_URL}/api/customer/profile", json={"lang": "de"})
        print("✓ PUT /api/customer/profile (lang change) - 200 OK")


# ============================================================================
# ADMIN ENDPOINTS (routes/admin.py)
# ============================================================================

class TestAdminEndpoints:
    """Test admin endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Create authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    def test_admin_get_inquiries(self, admin_session):
        """GET /api/admin/inquiries - Get all inquiries"""
        response = admin_session.get(f"{BASE_URL}/api/admin/inquiries")
        assert response.status_code == 200, f"Get inquiries failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/admin/inquiries - 200 OK ({len(data)} inquiries)")
    
    def test_admin_get_stats(self, admin_session):
        """GET /api/admin/stats - Get admin stats"""
        response = admin_session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200, f"Get stats failed: {response.text}"
        data = response.json()
        assert "total_inquiries" in data
        assert "new_inquiries" in data
        assert "confirmed" in data
        assert "total_trucks" in data
        print("✓ GET /api/admin/stats - 200 OK")
    
    def test_admin_get_settings(self, admin_session):
        """GET /api/admin/settings - Get admin settings"""
        response = admin_session.get(f"{BASE_URL}/api/admin/settings")
        assert response.status_code == 200, f"Get settings failed: {response.text}"
        data = response.json()
        assert "company_name" in data
        assert "company_email" in data
        print("✓ GET /api/admin/settings - 200 OK")
    
    def test_admin_get_trucks(self, admin_session):
        """GET /api/admin/trucks - Get all trucks (admin)"""
        response = admin_session.get(f"{BASE_URL}/api/admin/trucks")
        assert response.status_code == 200, f"Get trucks failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✓ GET /api/admin/trucks - 200 OK ({len(data)} trucks)")
    
    def test_admin_get_faqs(self, admin_session):
        """GET /api/admin/faqs - Get all FAQs (admin)"""
        response = admin_session.get(f"{BASE_URL}/api/admin/faqs")
        assert response.status_code == 200, f"Get FAQs failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/admin/faqs - 200 OK ({len(data)} FAQs)")
    
    def test_admin_get_employees(self, admin_session):
        """GET /api/admin/employees - Get all employees"""
        response = admin_session.get(f"{BASE_URL}/api/admin/employees")
        assert response.status_code == 200, f"Get employees failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/admin/employees - 200 OK ({len(data)} employees)")
    
    def test_admin_get_reviews(self, admin_session):
        """GET /api/admin/reviews - Get all reviews (admin)"""
        response = admin_session.get(f"{BASE_URL}/api/admin/reviews")
        assert response.status_code == 200, f"Get reviews failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/admin/reviews - 200 OK ({len(data)} reviews)")
    
    def test_admin_finance_overview(self, admin_session):
        """GET /api/admin/finance/overview - Get finance overview"""
        response = admin_session.get(f"{BASE_URL}/api/admin/finance/overview")
        assert response.status_code == 200, f"Get finance failed: {response.text}"
        data = response.json()
        assert "total_revenue" in data
        assert "total_costs" in data
        assert "total_profit" in data
        print("✓ GET /api/admin/finance/overview - 200 OK")
    
    def test_admin_events_map(self, admin_session):
        """GET /api/admin/events-map - Get events map data"""
        response = admin_session.get(f"{BASE_URL}/api/admin/events-map")
        assert response.status_code == 200, f"Get events map failed: {response.text}"
        data = response.json()
        assert "events" in data
        assert "base" in data
        print(f"✓ GET /api/admin/events-map - 200 OK ({len(data['events'])} events)")
    
    def test_admin_email_preview_de(self, admin_session):
        """GET /api/admin/email-preview?lang=de - Email preview German"""
        response = admin_session.get(f"{BASE_URL}/api/admin/email-preview?lang=de")
        assert response.status_code == 200, f"Email preview DE failed: {response.text}"
        data = response.json()
        assert "confirmation" in data
        assert "Vielen Dank" in data["confirmation"]
        print("✓ GET /api/admin/email-preview?lang=de - 200 OK")
    
    def test_admin_email_preview_fr(self, admin_session):
        """GET /api/admin/email-preview?lang=fr - Email preview French"""
        response = admin_session.get(f"{BASE_URL}/api/admin/email-preview?lang=fr")
        assert response.status_code == 200, f"Email preview FR failed: {response.text}"
        data = response.json()
        assert "confirmation" in data
        assert "Merci" in data["confirmation"]
        print("✓ GET /api/admin/email-preview?lang=fr - 200 OK")
    
    def test_admin_event_scout_events(self, admin_session):
        """GET /api/admin/event-scout/events - Get scouted events"""
        response = admin_session.get(f"{BASE_URL}/api/admin/event-scout/events")
        assert response.status_code == 200, f"Get scouted events failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/admin/event-scout/events - 200 OK ({len(data)} events)")
    
    def test_admin_event_scout_sources(self, admin_session):
        """GET /api/admin/event-scout/sources - Get scout sources"""
        response = admin_session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        assert response.status_code == 200, f"Get scout sources failed: {response.text}"
        data = response.json()
        assert "sources" in data
        assert "keywords" in data
        print("✓ GET /api/admin/event-scout/sources - 200 OK")
    
    def test_admin_export_inquiries_csv(self, admin_session):
        """GET /api/admin/export/inquiries?format=csv - Export inquiries CSV"""
        response = admin_session.get(f"{BASE_URL}/api/admin/export/inquiries?format=csv")
        assert response.status_code == 200, f"Export CSV failed: {response.text}"
        assert "text/csv" in response.headers.get("content-type", "")
        print("✓ GET /api/admin/export/inquiries?format=csv - 200 OK")


# ============================================================================
# INQUIRY CRUD (routes/admin.py)
# ============================================================================

class TestInquiryCRUD:
    """Test inquiry create and admin update"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_create_inquiry(self):
        """POST /api/inquiries - Create inquiry"""
        response = requests.post(f"{BASE_URL}/api/inquiries", json={
            "first_name": "TEST_Refactor",
            "last_name": "Verification",
            "email": "test_refactor@example.com",
            "phone": "+41 79 123 45 67",
            "event_date": "2026-08-15",
            "location": "Zürich",
            "guest_count": 150,
            "event_type": "Firmenanlass",
            "selected_trucks": ["Burger Truck"],
            "lang": "de"
        })
        assert response.status_code == 200, f"Create inquiry failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["message"] == "Anfrage erfolgreich gesendet"
        print(f"✓ POST /api/inquiries - 200 OK (id: {data['id'][:8]}...)")
        return data["id"]
    
    def test_admin_update_inquiry_lang(self, admin_session):
        """PUT /api/admin/inquiries/{id}/lang - Update inquiry language"""
        # First create an inquiry
        create_resp = requests.post(f"{BASE_URL}/api/inquiries", json={
            "first_name": "TEST_Lang",
            "last_name": "Update",
            "email": "test_lang@example.com",
            "phone": "+41 79 111 22 33",
            "event_date": "2026-09-01",
            "location": "Bern",
            "guest_count": 100,
            "event_type": "Festival"
        })
        assert create_resp.status_code == 200
        inquiry_id = create_resp.json()["id"]
        
        # Update language
        response = admin_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/lang", json={
            "lang": "fr"
        })
        assert response.status_code == 200, f"Update lang failed: {response.text}"
        
        # Verify
        get_resp = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert get_resp.json()["lang"] == "fr"
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        print("✓ PUT /api/admin/inquiries/{id}/lang - 200 OK")


# ============================================================================
# CLEANUP
# ============================================================================

class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_cleanup_test_inquiries(self, admin_session):
        """Clean up TEST_ prefixed inquiries"""
        response = admin_session.get(f"{BASE_URL}/api/admin/inquiries")
        if response.status_code == 200:
            inquiries = response.json()
            cleaned = 0
            for inq in inquiries:
                if inq.get("first_name", "").startswith("TEST_"):
                    admin_session.delete(f"{BASE_URL}/api/admin/inquiries/{inq['id']}")
                    cleaned += 1
            print(f"✓ Cleaned up {cleaned} test inquiries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
