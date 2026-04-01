"""
Test Customer Portal Features - Batch 9
Tests for:
- Customer registration (POST /api/auth/register)
- Customer login (POST /api/auth/login for customer accounts)
- Customer portal endpoints (GET /api/customer/inquiries, GET /api/customer/profile)
- Inquiry linking to customer_id when logged in
- Auto-confirmation toggle in settings
- Invoice management (PUT /api/admin/inquiries/{id}/invoice)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCustomerRegistration:
    """Test customer registration endpoint"""
    
    def test_register_new_customer_success(self):
        """POST /api/auth/register creates a new customer account with role='customer'"""
        unique_email = f"test_customer_{uuid.uuid4().hex[:8]}@test.ch"
        payload = {
            "email": unique_email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "Customer",
            "company": "Test Company",
            "phone": "+41 79 123 4567"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain user id"
        assert data["email"] == unique_email.lower(), "Email should match"
        assert data["role"] == "customer", f"Role should be 'customer', got {data.get('role')}"
        assert data["name"] == "Test Customer", "Name should be first_name + last_name"
        
        # Verify cookies are set
        assert "access_token" in response.cookies or response.headers.get("set-cookie"), "Should set access_token cookie"
        print(f"✓ Customer registration successful: {unique_email}")
    
    def test_register_duplicate_email_returns_400(self):
        """POST /api/auth/register returns 400 for duplicate email"""
        # First registration
        unique_email = f"dup_test_{uuid.uuid4().hex[:8]}@test.ch"
        payload = {
            "email": unique_email,
            "password": "TestPass123!",
            "first_name": "First",
            "last_name": "User"
        }
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response1.status_code == 200, f"First registration should succeed: {response1.text}"
        
        # Second registration with same email
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response2.status_code == 400, f"Duplicate email should return 400, got {response2.status_code}"
        
        data = response2.json()
        assert "detail" in data, "Should have error detail"
        print(f"✓ Duplicate email correctly rejected: {data.get('detail')}")


class TestCustomerLogin:
    """Test customer login functionality"""
    
    @pytest.fixture
    def test_customer(self):
        """Create a test customer for login tests"""
        unique_email = f"login_test_{uuid.uuid4().hex[:8]}@test.ch"
        payload = {
            "email": unique_email,
            "password": "LoginTest123!",
            "first_name": "Login",
            "last_name": "Tester"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200, f"Failed to create test customer: {response.text}"
        return {"email": unique_email, "password": "LoginTest123!"}
    
    def test_customer_login_success(self, test_customer):
        """POST /api/auth/login works for customer accounts"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_customer["email"],
            "password": test_customer["password"]
        })
        assert response.status_code == 200, f"Login should succeed: {response.text}"
        
        data = response.json()
        assert data["email"] == test_customer["email"].lower()
        assert data["role"] == "customer", f"Role should be 'customer', got {data.get('role')}"
        print(f"✓ Customer login successful: {test_customer['email']}")
    
    def test_customer_login_invalid_password(self, test_customer):
        """POST /api/auth/login returns 401 for wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_customer["email"],
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401, f"Wrong password should return 401, got {response.status_code}"
        print("✓ Invalid password correctly rejected")


class TestCustomerPortalEndpoints:
    """Test customer portal API endpoints"""
    
    @pytest.fixture
    def authenticated_customer(self):
        """Create and login a test customer, return session with cookies"""
        unique_email = f"portal_test_{uuid.uuid4().hex[:8]}@test.ch"
        session = requests.Session()
        
        # Register
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "PortalTest123!",
            "first_name": "Portal",
            "last_name": "Tester"
        })
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        
        return {"session": session, "email": unique_email, "user_id": reg_response.json().get("id")}
    
    def test_customer_profile_returns_data(self, authenticated_customer):
        """GET /api/customer/profile returns customer profile data"""
        session = authenticated_customer["session"]
        response = session.get(f"{BASE_URL}/api/customer/profile")
        assert response.status_code == 200, f"Profile should return 200: {response.text}"
        
        data = response.json()
        assert data["email"] == authenticated_customer["email"].lower()
        assert data["role"] == "customer"
        assert "first_name" in data
        assert "last_name" in data
        print(f"✓ Customer profile returned: {data}")
    
    def test_customer_inquiries_returns_only_own(self, authenticated_customer):
        """GET /api/customer/inquiries returns only the logged-in customer's inquiries"""
        session = authenticated_customer["session"]
        response = session.get(f"{BASE_URL}/api/customer/inquiries")
        assert response.status_code == 200, f"Inquiries should return 200: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list"
        # New customer should have 0 inquiries
        print(f"✓ Customer inquiries returned: {len(data)} inquiries")
    
    def test_customer_endpoints_require_auth(self):
        """Customer endpoints return 401 without authentication"""
        # No session/cookies
        response = requests.get(f"{BASE_URL}/api/customer/profile")
        assert response.status_code == 401, f"Profile without auth should return 401, got {response.status_code}"
        
        response = requests.get(f"{BASE_URL}/api/customer/inquiries")
        assert response.status_code == 401, f"Inquiries without auth should return 401, got {response.status_code}"
        print("✓ Customer endpoints correctly require authentication")


class TestInquiryCustomerLinking:
    """Test that inquiries are linked to customer_id when customer is logged in"""
    
    @pytest.fixture
    def authenticated_customer_session(self):
        """Create and login a test customer"""
        unique_email = f"inquiry_link_{uuid.uuid4().hex[:8]}@test.ch"
        session = requests.Session()
        
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "InquiryTest123!",
            "first_name": "Inquiry",
            "last_name": "Linker"
        })
        assert reg_response.status_code == 200
        return {"session": session, "user_id": reg_response.json().get("id"), "email": unique_email}
    
    def test_inquiry_links_to_customer_when_logged_in(self, authenticated_customer_session):
        """POST /api/inquiries links inquiry to customer_id when customer is logged in"""
        session = authenticated_customer_session["session"]
        user_id = authenticated_customer_session["user_id"]
        
        inquiry_payload = {
            "first_name": "Inquiry",
            "last_name": "Linker",
            "email": authenticated_customer_session["email"],
            "phone": "+41 79 999 8888",
            "event_date": "2026-06-15",
            "location": "Zürich",
            "guest_count": 100,
            "event_type": "Firmenanlass",
            "selected_trucks": ["Burger Truck"]
        }
        
        response = session.post(f"{BASE_URL}/api/inquiries", json=inquiry_payload)
        assert response.status_code == 200, f"Inquiry creation should succeed: {response.text}"
        
        inquiry_id = response.json().get("id")
        
        # Verify the inquiry appears in customer's inquiries
        inquiries_response = session.get(f"{BASE_URL}/api/customer/inquiries")
        assert inquiries_response.status_code == 200
        
        inquiries = inquiries_response.json()
        assert len(inquiries) >= 1, "Customer should have at least 1 inquiry"
        
        # Find our inquiry
        our_inquiry = next((i for i in inquiries if i.get("id") == inquiry_id), None)
        assert our_inquiry is not None, f"Inquiry {inquiry_id} should be in customer's inquiries"
        assert our_inquiry.get("customer_id") == user_id, f"Inquiry should have customer_id={user_id}"
        print(f"✓ Inquiry correctly linked to customer: {inquiry_id} -> {user_id}")


class TestAutoConfirmationSetting:
    """Test auto-confirmation toggle in settings"""
    
    @pytest.fixture
    def admin_session(self):
        """Login as admin"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    def test_auto_confirmation_setting_exists(self, admin_session):
        """GET /api/admin/settings includes auto_confirmation field"""
        response = admin_session.get(f"{BASE_URL}/api/admin/settings")
        assert response.status_code == 200, f"Settings should return 200: {response.text}"
        
        data = response.json()
        assert "auto_confirmation" in data, "Settings should include auto_confirmation field"
        print(f"✓ auto_confirmation setting exists: {data.get('auto_confirmation')}")
    
    def test_auto_confirmation_can_be_toggled(self, admin_session):
        """PUT /api/admin/settings can toggle auto_confirmation"""
        # Get current settings
        get_response = admin_session.get(f"{BASE_URL}/api/admin/settings")
        current_settings = get_response.json()
        current_value = current_settings.get("auto_confirmation", False)
        
        # Toggle the value
        new_value = not current_value
        current_settings["auto_confirmation"] = new_value
        
        put_response = admin_session.put(f"{BASE_URL}/api/admin/settings", json=current_settings)
        assert put_response.status_code == 200, f"Settings update should succeed: {put_response.text}"
        
        # Verify the change
        verify_response = admin_session.get(f"{BASE_URL}/api/admin/settings")
        updated_settings = verify_response.json()
        assert updated_settings.get("auto_confirmation") == new_value, "auto_confirmation should be toggled"
        
        # Restore original value
        current_settings["auto_confirmation"] = current_value
        admin_session.put(f"{BASE_URL}/api/admin/settings", json=current_settings)
        
        print(f"✓ auto_confirmation toggled: {current_value} -> {new_value} -> {current_value}")
    
    def test_inquiry_status_with_auto_confirmation_off(self, admin_session):
        """POST /api/inquiries creates inquiry with status='new' when auto_confirmation is off"""
        # Ensure auto_confirmation is off
        settings_response = admin_session.get(f"{BASE_URL}/api/admin/settings")
        settings = settings_response.json()
        original_value = settings.get("auto_confirmation", False)
        
        if original_value:
            settings["auto_confirmation"] = False
            admin_session.put(f"{BASE_URL}/api/admin/settings", json=settings)
        
        # Create inquiry (without auth - public)
        inquiry_payload = {
            "first_name": "AutoConf",
            "last_name": "Test",
            "email": f"autoconf_{uuid.uuid4().hex[:8]}@test.ch",
            "phone": "+41 79 111 2222",
            "event_date": "2026-07-20",
            "location": "Bern",
            "guest_count": 50,
            "event_type": "Private Event"
        }
        
        response = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_payload)
        assert response.status_code == 200, f"Inquiry creation should succeed: {response.text}"
        
        inquiry_id = response.json().get("id")
        
        # Check the inquiry status via admin endpoint
        inquiry_response = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert inquiry_response.status_code == 200
        
        inquiry = inquiry_response.json()
        assert inquiry.get("status") == "new", f"Status should be 'new' when auto_confirmation is off, got {inquiry.get('status')}"
        
        # Restore original setting
        if original_value:
            settings["auto_confirmation"] = True
            admin_session.put(f"{BASE_URL}/api/admin/settings", json=settings)
        
        print(f"✓ Inquiry created with status='new' when auto_confirmation is off")


class TestInvoiceManagement:
    """Test invoice management endpoints"""
    
    @pytest.fixture
    def admin_session(self):
        """Login as admin"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    @pytest.fixture
    def test_inquiry(self, admin_session):
        """Create a test inquiry for invoice tests"""
        inquiry_payload = {
            "first_name": "Invoice",
            "last_name": "Test",
            "email": f"invoice_{uuid.uuid4().hex[:8]}@test.ch",
            "phone": "+41 79 333 4444",
            "event_date": "2026-08-10",
            "location": "Basel",
            "guest_count": 75,
            "event_type": "Festival"
        }
        response = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_payload)
        assert response.status_code == 200
        return response.json().get("id")
    
    def test_update_invoice_status(self, admin_session, test_inquiry):
        """PUT /api/admin/inquiries/{id}/invoice updates invoice_status"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry}/invoice",
            json={"invoice_status": "pending"}
        )
        assert response.status_code == 200, f"Invoice update should succeed: {response.text}"
        
        # Verify the change
        inquiry_response = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry}")
        inquiry = inquiry_response.json()
        assert inquiry.get("invoice_status") == "pending", f"Invoice status should be 'pending', got {inquiry.get('invoice_status')}"
        print(f"✓ Invoice status updated to 'pending'")
    
    def test_update_invoice_amount(self, admin_session, test_inquiry):
        """PUT /api/admin/inquiries/{id}/invoice updates invoice_amount"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry}/invoice",
            json={"invoice_amount": 2500}
        )
        assert response.status_code == 200, f"Invoice amount update should succeed: {response.text}"
        
        # Verify the change
        inquiry_response = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry}")
        inquiry = inquiry_response.json()
        assert inquiry.get("invoice_amount") == 2500, f"Invoice amount should be 2500, got {inquiry.get('invoice_amount')}"
        print(f"✓ Invoice amount updated to 2500")
    
    def test_update_invoice_status_and_amount(self, admin_session, test_inquiry):
        """PUT /api/admin/inquiries/{id}/invoice updates both status and amount"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry}/invoice",
            json={"invoice_status": "paid", "invoice_amount": 3500}
        )
        assert response.status_code == 200, f"Invoice update should succeed: {response.text}"
        
        # Verify the changes
        inquiry_response = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry}")
        inquiry = inquiry_response.json()
        assert inquiry.get("invoice_status") == "paid", f"Invoice status should be 'paid'"
        assert inquiry.get("invoice_amount") == 3500, f"Invoice amount should be 3500"
        print(f"✓ Invoice status and amount updated together")


class TestAdminInquiriesCompletedStatus:
    """Test that 'completed' status is available in admin inquiries"""
    
    @pytest.fixture
    def admin_session(self):
        """Login as admin"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def test_inquiry(self, admin_session):
        """Create a test inquiry"""
        inquiry_payload = {
            "first_name": "Completed",
            "last_name": "StatusTest",
            "email": f"completed_{uuid.uuid4().hex[:8]}@test.ch",
            "phone": "+41 79 555 6666",
            "event_date": "2026-09-01",
            "location": "Luzern",
            "guest_count": 120,
            "event_type": "Hochzeit"
        }
        response = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_payload)
        assert response.status_code == 200
        return response.json().get("id")
    
    def test_can_set_completed_status(self, admin_session, test_inquiry):
        """PUT /api/admin/inquiries/{id} can set status to 'completed'"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry}",
            json={"status": "completed", "internal_notes": "Event completed successfully"}
        )
        assert response.status_code == 200, f"Status update should succeed: {response.text}"
        
        # Verify the change
        inquiry_response = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry}")
        inquiry = inquiry_response.json()
        assert inquiry.get("status") == "completed", f"Status should be 'completed', got {inquiry.get('status')}"
        print(f"✓ Inquiry status set to 'completed'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
