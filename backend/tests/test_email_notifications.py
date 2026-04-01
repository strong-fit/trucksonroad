"""
Test Email Notification Features (Batch 10)
- Status change notifications (confirmed, completed, cancelled, in_review)
- Invoice status notifications (pending, sent, paid, overdue)
- Email preview endpoint with 6 templates
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEmailNotifications:
    """Test email notification triggers on status/invoice changes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin and get session"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        yield
        self.session.close()
    
    @pytest.fixture
    def test_inquiry_id(self):
        """Create a test inquiry for notification tests"""
        inquiry_data = {
            "first_name": "EmailTest",
            "last_name": f"User{uuid.uuid4().hex[:6]}",
            "email": f"emailtest_{uuid.uuid4().hex[:6]}@test.ch",
            "phone": "+41 79 123 45 67",
            "event_date": "2026-07-15",
            "location": "Zürich Test",
            "guest_count": 100,
            "event_type": "Firmenanlass",
            "selected_trucks": ["Burger Truck"],
            "privacy_accepted": True
        }
        resp = self.session.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert resp.status_code == 200, f"Failed to create test inquiry: {resp.text}"
        data = resp.json()
        inquiry_id = data.get("id")
        assert inquiry_id, "No inquiry ID returned"
        yield inquiry_id
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
    
    # --- Status Change Notification Tests ---
    
    def test_status_confirmed_triggers_notification(self, test_inquiry_id):
        """PUT /api/admin/inquiries/{id} with status='confirmed' returns 200"""
        resp = self.session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}",
            json={"status": "confirmed", "internal_notes": ""}
        )
        assert resp.status_code == 200, f"Status update to confirmed failed: {resp.text}"
        data = resp.json()
        assert data.get("message") == "Updated", f"Unexpected response: {data}"
        
        # Verify status was actually updated
        get_resp = self.session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}")
        assert get_resp.status_code == 200
        inquiry = get_resp.json()
        assert inquiry.get("status") == "confirmed", f"Status not updated: {inquiry.get('status')}"
    
    def test_status_completed_triggers_notification(self, test_inquiry_id):
        """PUT /api/admin/inquiries/{id} with status='completed' returns 200"""
        resp = self.session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}",
            json={"status": "completed", "internal_notes": ""}
        )
        assert resp.status_code == 200, f"Status update to completed failed: {resp.text}"
        data = resp.json()
        assert data.get("message") == "Updated"
        
        # Verify status was actually updated
        get_resp = self.session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}")
        assert get_resp.status_code == 200
        inquiry = get_resp.json()
        assert inquiry.get("status") == "completed"
    
    def test_status_cancelled_triggers_notification(self, test_inquiry_id):
        """PUT /api/admin/inquiries/{id} with status='cancelled' returns 200"""
        resp = self.session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}",
            json={"status": "cancelled", "internal_notes": "Test cancellation"}
        )
        assert resp.status_code == 200, f"Status update to cancelled failed: {resp.text}"
        data = resp.json()
        assert data.get("message") == "Updated"
        
        # Verify status was actually updated
        get_resp = self.session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}")
        assert get_resp.status_code == 200
        inquiry = get_resp.json()
        assert inquiry.get("status") == "cancelled"
    
    def test_status_in_review_triggers_notification(self, test_inquiry_id):
        """PUT /api/admin/inquiries/{id} with status='in_review' returns 200"""
        resp = self.session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}",
            json={"status": "in_review", "internal_notes": ""}
        )
        assert resp.status_code == 200, f"Status update to in_review failed: {resp.text}"
        data = resp.json()
        assert data.get("message") == "Updated"
        
        # Verify status was actually updated
        get_resp = self.session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}")
        assert get_resp.status_code == 200
        inquiry = get_resp.json()
        assert inquiry.get("status") == "in_review"
    
    # --- Invoice Status Notification Tests ---
    
    def test_invoice_sent_triggers_notification(self, test_inquiry_id):
        """PUT /api/admin/inquiries/{id}/invoice with invoice_status='sent' returns 200"""
        resp = self.session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}/invoice",
            json={"invoice_status": "sent", "invoice_amount": 2500}
        )
        assert resp.status_code == 200, f"Invoice update to sent failed: {resp.text}"
        data = resp.json()
        assert data.get("message") == "Invoice updated", f"Unexpected response: {data}"
        
        # Verify invoice status was updated
        get_resp = self.session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}")
        assert get_resp.status_code == 200
        inquiry = get_resp.json()
        assert inquiry.get("invoice_status") == "sent"
        assert inquiry.get("invoice_amount") == 2500
    
    def test_invoice_paid_triggers_notification(self, test_inquiry_id):
        """PUT /api/admin/inquiries/{id}/invoice with invoice_status='paid' returns 200"""
        resp = self.session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}/invoice",
            json={"invoice_status": "paid", "invoice_amount": 3000}
        )
        assert resp.status_code == 200, f"Invoice update to paid failed: {resp.text}"
        data = resp.json()
        assert data.get("message") == "Invoice updated"
        
        # Verify invoice status was updated
        get_resp = self.session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}")
        assert get_resp.status_code == 200
        inquiry = get_resp.json()
        assert inquiry.get("invoice_status") == "paid"
        assert inquiry.get("invoice_amount") == 3000
    
    def test_invoice_pending_triggers_notification(self, test_inquiry_id):
        """PUT /api/admin/inquiries/{id}/invoice with invoice_status='pending' returns 200"""
        resp = self.session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}/invoice",
            json={"invoice_status": "pending", "invoice_amount": 1500}
        )
        assert resp.status_code == 200, f"Invoice update to pending failed: {resp.text}"
        data = resp.json()
        assert data.get("message") == "Invoice updated"
        
        # Verify invoice status was updated
        get_resp = self.session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}")
        assert get_resp.status_code == 200
        inquiry = get_resp.json()
        assert inquiry.get("invoice_status") == "pending"
    
    def test_invoice_overdue_triggers_notification(self, test_inquiry_id):
        """PUT /api/admin/inquiries/{id}/invoice with invoice_status='overdue' returns 200"""
        resp = self.session.put(
            f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}/invoice",
            json={"invoice_status": "overdue", "invoice_amount": 4000}
        )
        assert resp.status_code == 200, f"Invoice update to overdue failed: {resp.text}"
        data = resp.json()
        assert data.get("message") == "Invoice updated"
        
        # Verify invoice status was updated
        get_resp = self.session.get(f"{BASE_URL}/api/admin/inquiries/{test_inquiry_id}")
        assert get_resp.status_code == 200
        inquiry = get_resp.json()
        assert inquiry.get("invoice_status") == "overdue"


class TestEmailPreview:
    """Test email preview endpoint returns all 6 templates"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        yield
        self.session.close()
    
    def test_email_preview_returns_6_templates(self):
        """GET /api/admin/email-preview returns 6 templates"""
        resp = self.session.get(f"{BASE_URL}/api/admin/email-preview")
        assert resp.status_code == 200, f"Email preview failed: {resp.text}"
        data = resp.json()
        
        # Check all 6 templates are present
        expected_templates = [
            "confirmation",
            "notification", 
            "status_confirmed",
            "status_completed",
            "invoice_sent",
            "invoice_paid"
        ]
        
        for template in expected_templates:
            assert template in data, f"Missing template: {template}"
            assert isinstance(data[template], str), f"Template {template} is not a string"
            assert len(data[template]) > 100, f"Template {template} seems too short"
            assert "TRUCKONROAD" in data[template].upper() or "TRUCK" in data[template].upper(), \
                f"Template {template} missing branding"
    
    def test_email_preview_confirmation_template(self):
        """Confirmation template contains expected content"""
        resp = self.session.get(f"{BASE_URL}/api/admin/email-preview")
        assert resp.status_code == 200
        data = resp.json()
        
        confirmation = data.get("confirmation", "")
        assert "Max" in confirmation or "Mustermann" in confirmation, "Missing sample name"
        assert "Zürich" in confirmation or "Sechseläutenplatz" in confirmation, "Missing sample location"
    
    def test_email_preview_status_confirmed_template(self):
        """Status confirmed template contains expected content"""
        resp = self.session.get(f"{BASE_URL}/api/admin/email-preview")
        assert resp.status_code == 200
        data = resp.json()
        
        status_confirmed = data.get("status_confirmed", "")
        assert "Bestaetigt" in status_confirmed or "bestätigt" in status_confirmed.lower(), \
            "Missing confirmed status label"
    
    def test_email_preview_invoice_sent_template(self):
        """Invoice sent template contains expected content"""
        resp = self.session.get(f"{BASE_URL}/api/admin/email-preview")
        assert resp.status_code == 200
        data = resp.json()
        
        invoice_sent = data.get("invoice_sent", "")
        assert "Rechnung" in invoice_sent, "Missing invoice label"
        assert "4500" in invoice_sent or "4,500" in invoice_sent or "4'500" in invoice_sent, \
            "Missing sample invoice amount"
    
    def test_email_preview_requires_auth(self):
        """Email preview requires authentication"""
        unauth_session = requests.Session()
        resp = unauth_session.get(f"{BASE_URL}/api/admin/email-preview")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        unauth_session.close()


class TestAutoConfirmationSetting:
    """Test auto-confirmation toggle in admin settings"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        yield
        self.session.close()
    
    def test_settings_include_auto_confirmation(self):
        """GET /api/admin/settings includes auto_confirmation field"""
        resp = self.session.get(f"{BASE_URL}/api/admin/settings")
        assert resp.status_code == 200, f"Settings fetch failed: {resp.text}"
        data = resp.json()
        assert "auto_confirmation" in data, "Missing auto_confirmation field"
        assert isinstance(data["auto_confirmation"], bool), "auto_confirmation should be boolean"
    
    def test_toggle_auto_confirmation(self):
        """PUT /api/admin/settings can toggle auto_confirmation"""
        # Get current setting
        get_resp = self.session.get(f"{BASE_URL}/api/admin/settings")
        assert get_resp.status_code == 200
        current = get_resp.json().get("auto_confirmation", False)
        
        # Toggle it
        new_value = not current
        put_resp = self.session.put(f"{BASE_URL}/api/admin/settings", json={
            "auto_confirmation": new_value
        })
        assert put_resp.status_code == 200, f"Settings update failed: {put_resp.text}"
        
        # Verify change
        verify_resp = self.session.get(f"{BASE_URL}/api/admin/settings")
        assert verify_resp.status_code == 200
        assert verify_resp.json().get("auto_confirmation") == new_value
        
        # Restore original
        self.session.put(f"{BASE_URL}/api/admin/settings", json={
            "auto_confirmation": current
        })


class TestCustomerPortalStatusDisplay:
    """Test customer portal shows updated status and invoice badges"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin and customer sessions"""
        self.admin_session = requests.Session()
        login_resp = self.admin_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        
        # Create a test customer
        self.customer_email = f"portaltest_{uuid.uuid4().hex[:6]}@test.ch"
        self.customer_password = "TestPass123!"
        
        self.customer_session = requests.Session()
        reg_resp = self.customer_session.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.customer_email,
            "password": self.customer_password,
            "first_name": "Portal",
            "last_name": "Tester",
            "phone": "+41 79 999 88 77"
        })
        assert reg_resp.status_code == 200, f"Customer registration failed: {reg_resp.text}"
        
        yield
        
        self.admin_session.close()
        self.customer_session.close()
    
    def test_customer_sees_status_after_admin_change(self):
        """Customer portal shows updated status after admin changes it"""
        # Customer creates inquiry
        inquiry_data = {
            "first_name": "Portal",
            "last_name": "Tester",
            "email": self.customer_email,
            "phone": "+41 79 999 88 77",
            "event_date": "2026-08-20",
            "location": "Basel Test",
            "guest_count": 150,
            "event_type": "Hochzeit",
            "selected_trucks": ["Bowl Truck"],
            "privacy_accepted": True
        }
        create_resp = self.customer_session.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert create_resp.status_code == 200, f"Inquiry creation failed: {create_resp.text}"
        inquiry_id = create_resp.json().get("id")
        
        # Admin updates status to confirmed
        admin_update = self.admin_session.put(
            f"{BASE_URL}/api/admin/inquiries/{inquiry_id}",
            json={"status": "confirmed", "internal_notes": ""}
        )
        assert admin_update.status_code == 200
        
        # Customer checks their inquiries
        customer_inquiries = self.customer_session.get(f"{BASE_URL}/api/customer/inquiries")
        assert customer_inquiries.status_code == 200
        inquiries = customer_inquiries.json()
        
        # Find the inquiry and check status
        found = next((i for i in inquiries if i.get("id") == inquiry_id), None)
        assert found is not None, "Inquiry not found in customer portal"
        assert found.get("status") == "confirmed", f"Status not updated: {found.get('status')}"
        
        # Cleanup
        self.admin_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
    
    def test_customer_sees_invoice_after_admin_update(self):
        """Customer portal shows invoice badge after admin updates invoice"""
        # Customer creates inquiry
        inquiry_data = {
            "first_name": "Portal",
            "last_name": "Tester",
            "email": self.customer_email,
            "phone": "+41 79 999 88 77",
            "event_date": "2026-09-10",
            "location": "Bern Test",
            "guest_count": 80,
            "event_type": "Geburtstag",
            "selected_trucks": ["Burger Truck"],
            "privacy_accepted": True
        }
        create_resp = self.customer_session.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert create_resp.status_code == 200
        inquiry_id = create_resp.json().get("id")
        
        # Admin updates invoice status
        admin_invoice = self.admin_session.put(
            f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/invoice",
            json={"invoice_status": "sent", "invoice_amount": 1800}
        )
        assert admin_invoice.status_code == 200
        
        # Customer checks their inquiries
        customer_inquiries = self.customer_session.get(f"{BASE_URL}/api/customer/inquiries")
        assert customer_inquiries.status_code == 200
        inquiries = customer_inquiries.json()
        
        # Find the inquiry and check invoice
        found = next((i for i in inquiries if i.get("id") == inquiry_id), None)
        assert found is not None, "Inquiry not found in customer portal"
        assert found.get("invoice_status") == "sent", f"Invoice status not updated: {found.get('invoice_status')}"
        assert found.get("invoice_amount") == 1800, f"Invoice amount not updated: {found.get('invoice_amount')}"
        
        # Cleanup
        self.admin_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
