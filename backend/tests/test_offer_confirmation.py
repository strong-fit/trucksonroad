"""
Test suite for the new offer confirmation flow:
1. GET /api/confirm-offer/{id}/{token} - returns offer details without auto-confirming
2. POST /api/confirm-offer/{id}/{token} - confirms offer with payment method
3. GET after POST - shows already_confirmed=true with payment_method stored
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestOfferConfirmationFlow:
    """Test the new 2-step offer confirmation flow"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        return session
    
    @pytest.fixture(scope="class")
    def test_inquiry(self, admin_session):
        """Create a test inquiry for offer confirmation testing"""
        # Create inquiry via public endpoint
        inquiry_data = {
            "first_name": "TEST_Offer",
            "last_name": "Confirmation",
            "email": f"test_offer_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+41 79 123 45 67",
            "event_date": "2026-06-15",
            "event_time": "12:00 - 18:00",
            "location": "Zürich Test Location",
            "guest_count": 150,
            "event_type": "Firmenevent",
            "selected_trucks": ["Burger Truck"],
            "indoor_outdoor": "Outdoor",
            "privacy_accepted": True,
            "lang": "de"
        }
        resp = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert resp.status_code in [200, 201], f"Failed to create inquiry: {resp.text}"
        inquiry_id = resp.json().get("id")
        assert inquiry_id, "No inquiry ID returned"
        
        # Set invoice amount via admin
        admin_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/invoice", json={
            "invoice_amount": 3500.00
        })
        
        # Set status to offer_sent
        admin_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}", json={
            "status": "offer_sent"
        })
        
        # Get the confirm_token
        detail_resp = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert detail_resp.status_code == 200, f"Failed to get inquiry details: {detail_resp.text}"
        inquiry_detail = detail_resp.json()
        confirm_token = inquiry_detail.get("confirm_token")
        assert confirm_token, "No confirm_token found in inquiry"
        
        yield {
            "id": inquiry_id,
            "token": confirm_token,
            "data": inquiry_detail
        }
        
        # Cleanup: delete test inquiry
        admin_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
    
    def test_get_offer_details_returns_data_without_confirming(self, test_inquiry):
        """GET /api/confirm-offer/{id}/{token} should return offer details without auto-confirming"""
        resp = requests.get(f"{BASE_URL}/api/confirm-offer/{test_inquiry['id']}/{test_inquiry['token']}")
        assert resp.status_code == 200, f"GET confirm-offer failed: {resp.text}"
        
        data = resp.json()
        # Verify offer details are returned
        assert data.get("inquiry_id") == test_inquiry['id']
        assert data.get("status") == "offer_sent"
        assert data.get("already_confirmed") == False, "Should not be already confirmed"
        assert "first_name" in data
        assert "event_date" in data
        assert "location" in data
        assert "guest_count" in data
        assert "invoice_amount" in data
        assert data.get("invoice_amount") == 3500.00
        print(f"✓ GET returns offer details: {data.get('first_name')} {data.get('last_name')}, amount: {data.get('invoice_amount')}")
    
    def test_get_offer_with_invalid_token_fails(self, test_inquiry):
        """GET with invalid token should return 400"""
        resp = requests.get(f"{BASE_URL}/api/confirm-offer/{test_inquiry['id']}/invalid_token_123")
        assert resp.status_code == 400, f"Expected 400 for invalid token, got {resp.status_code}"
        print("✓ Invalid token correctly rejected")
    
    def test_get_offer_with_invalid_id_fails(self):
        """GET with invalid inquiry ID should return 404"""
        resp = requests.get(f"{BASE_URL}/api/confirm-offer/nonexistent_id_123/some_token")
        assert resp.status_code == 404, f"Expected 404 for invalid ID, got {resp.status_code}"
        print("✓ Invalid inquiry ID correctly returns 404")
    
    def test_post_confirm_offer_with_invoice_payment(self, test_inquiry):
        """POST /api/confirm-offer/{id}/{token} with payment_method='invoice' should confirm"""
        resp = requests.post(
            f"{BASE_URL}/api/confirm-offer/{test_inquiry['id']}/{test_inquiry['token']}",
            json={"payment_method": "invoice"}
        )
        assert resp.status_code == 200, f"POST confirm-offer failed: {resp.text}"
        
        data = resp.json()
        assert data.get("status") == "confirmed"
        assert "message" in data
        print(f"✓ Offer confirmed with invoice payment: {data.get('message')}")
    
    def test_get_after_confirm_shows_already_confirmed(self, test_inquiry):
        """GET after POST should show already_confirmed=true with payment_method stored"""
        resp = requests.get(f"{BASE_URL}/api/confirm-offer/{test_inquiry['id']}/{test_inquiry['token']}")
        assert resp.status_code == 200, f"GET after confirm failed: {resp.text}"
        
        data = resp.json()
        assert data.get("already_confirmed") == True, "Should be already confirmed"
        assert data.get("status") == "confirmed"
        assert data.get("payment_method") == "invoice", f"Payment method should be 'invoice', got {data.get('payment_method')}"
        assert data.get("confirmed_at") is not None, "confirmed_at should be set"
        print(f"✓ GET after confirm shows already_confirmed=True, payment_method={data.get('payment_method')}")
    
    def test_post_already_confirmed_returns_already_confirmed(self, test_inquiry):
        """POST on already confirmed offer should return already_confirmed=true"""
        resp = requests.post(
            f"{BASE_URL}/api/confirm-offer/{test_inquiry['id']}/{test_inquiry['token']}",
            json={"payment_method": "cash"}
        )
        assert resp.status_code == 200, f"POST on confirmed offer failed: {resp.text}"
        
        data = resp.json()
        assert data.get("already_confirmed") == True, "Should indicate already confirmed"
        print(f"✓ POST on already confirmed correctly returns already_confirmed=True")


class TestOfferConfirmationWithCashPayment:
    """Test offer confirmation with cash payment method"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        return session
    
    @pytest.fixture(scope="class")
    def test_inquiry_cash(self, admin_session):
        """Create a test inquiry for cash payment testing"""
        inquiry_data = {
            "first_name": "TEST_Cash",
            "last_name": "Payment",
            "email": f"test_cash_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+41 79 987 65 43",
            "event_date": "2026-07-20",
            "event_time": "14:00 - 22:00",
            "location": "Bern Test Location",
            "guest_count": 80,
            "event_type": "Hochzeit",
            "selected_trucks": ["Bowl Truck", "Empanadas"],
            "indoor_outdoor": "Indoor",
            "privacy_accepted": True,
            "lang": "de"
        }
        resp = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert resp.status_code in [200, 201], f"Failed to create inquiry: {resp.text}"
        inquiry_id = resp.json().get("id")
        
        # Set invoice amount and status
        admin_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/invoice", json={
            "invoice_amount": 2800.00
        })
        admin_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}", json={
            "status": "offer_sent"
        })
        
        # Get confirm_token
        detail_resp = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        inquiry_detail = detail_resp.json()
        confirm_token = inquiry_detail.get("confirm_token")
        
        yield {
            "id": inquiry_id,
            "token": confirm_token
        }
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
    
    def test_confirm_with_cash_payment(self, test_inquiry_cash):
        """POST with payment_method='cash' should confirm with cash"""
        # First verify it's not confirmed
        get_resp = requests.get(f"{BASE_URL}/api/confirm-offer/{test_inquiry_cash['id']}/{test_inquiry_cash['token']}")
        assert get_resp.json().get("already_confirmed") == False
        
        # Confirm with cash
        resp = requests.post(
            f"{BASE_URL}/api/confirm-offer/{test_inquiry_cash['id']}/{test_inquiry_cash['token']}",
            json={"payment_method": "cash"}
        )
        assert resp.status_code == 200
        assert resp.json().get("status") == "confirmed"
        
        # Verify cash payment stored
        verify_resp = requests.get(f"{BASE_URL}/api/confirm-offer/{test_inquiry_cash['id']}/{test_inquiry_cash['token']}")
        data = verify_resp.json()
        assert data.get("payment_method") == "cash", f"Expected 'cash', got {data.get('payment_method')}"
        assert data.get("already_confirmed") == True
        print(f"✓ Cash payment confirmation working correctly")


class TestTrucksPageAndHomepage:
    """/trucks page and homepage tests"""
    
    def test_trucks_page_returns_200(self):
        """GET /trucks should return 200"""
        resp = requests.get(f"{BASE_URL}/trucks")
        assert resp.status_code == 200, f"/trucks returned {resp.status_code}"
        print("✓ /trucks page returns 200")
    
    def test_homepage_returns_200(self):
        """GET / should return 200"""
        resp = requests.get(f"{BASE_URL}/")
        assert resp.status_code == 200, f"Homepage returned {resp.status_code}"
        print("✓ Homepage returns 200")
    
    def test_trucks_api_returns_data(self):
        """GET /api/trucks should return truck data"""
        resp = requests.get(f"{BASE_URL}/api/trucks")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0, "No trucks returned"
        print(f"✓ /api/trucks returns {len(data)} trucks")


class TestInquiryFormEndpoint:
    """Test inquiry form submission"""
    
    def test_create_inquiry_returns_id(self):
        """POST /api/inquiries should create inquiry and return ID"""
        inquiry_data = {
            "first_name": "TEST_Form",
            "last_name": "Submission",
            "email": f"test_form_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+41 79 111 22 33",
            "event_date": "2026-08-10",
            "location": "Test Location",
            "guest_count": 100,
            "event_type": "Festival",
            "privacy_accepted": True,
            "lang": "de"
        }
        resp = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert resp.status_code in [200, 201], f"Create inquiry failed: {resp.text}"
        data = resp.json()
        assert "id" in data, "No ID returned"
        print(f"✓ Inquiry created with ID: {data.get('id')}")
        
        # Cleanup
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        session.delete(f"{BASE_URL}/api/admin/inquiries/{data.get('id')}")


class TestAdminOfferDialog:
    """Test admin offer dialog functionality"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        assert login_resp.status_code == 200
        return session
    
    def test_admin_can_set_invoice_amount(self, admin_session):
        """Admin should be able to set invoice_amount before sending offer"""
        # Create test inquiry
        inquiry_data = {
            "first_name": "TEST_Admin",
            "last_name": "Invoice",
            "email": f"test_admin_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+41 79 444 55 66",
            "event_date": "2026-09-01",
            "location": "Admin Test",
            "guest_count": 200,
            "event_type": "Firmenevent",
            "privacy_accepted": True,
            "lang": "de"
        }
        resp = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        inquiry_id = resp.json().get("id")
        
        # Set invoice amount
        invoice_resp = admin_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/invoice", json={
            "invoice_amount": 5000.00
        })
        assert invoice_resp.status_code == 200, f"Set invoice amount failed: {invoice_resp.text}"
        
        # Verify amount is stored
        detail_resp = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail.get("invoice_amount") == 5000.00, f"Invoice amount not stored correctly"
        print(f"✓ Admin can set invoice_amount: {detail.get('invoice_amount')}")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
    
    def test_admin_can_set_status_to_offer_sent(self, admin_session):
        """Admin should be able to set status to offer_sent"""
        # Create test inquiry
        inquiry_data = {
            "first_name": "TEST_Status",
            "last_name": "OfferSent",
            "email": f"test_status_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+41 79 777 88 99",
            "event_date": "2026-10-15",
            "location": "Status Test",
            "guest_count": 50,
            "event_type": "Geburtstag",
            "privacy_accepted": True,
            "lang": "de"
        }
        resp = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        inquiry_id = resp.json().get("id")
        
        # Set status to offer_sent
        status_resp = admin_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}", json={
            "status": "offer_sent"
        })
        assert status_resp.status_code == 200, f"Set status failed: {status_resp.text}"
        
        # Verify status and confirm_token
        detail_resp = admin_session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        detail = detail_resp.json()
        assert detail.get("status") == "offer_sent"
        assert detail.get("confirm_token") is not None, "confirm_token should be generated"
        print(f"✓ Admin can set status to offer_sent, confirm_token generated")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
