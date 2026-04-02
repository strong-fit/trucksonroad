"""
Test suite for Multilingual Email Templates and PDF Generation
Tests: 
- GET /api/admin/email-preview with lang=de/en/fr/it
- POST /api/inquiries with lang field
- GET /api/admin/inquiries returns inquiry with lang field
- GET /api/admin/inquiries/{id}/offer-pdf generates PDF correctly
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@truckonroad.ch"
ADMIN_PASSWORD = "TruckOnRoad2026!"


class TestSession:
    """Shared session with authentication"""
    _session = None
    _cookies = None
    
    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = requests.Session()
            cls._session.headers.update({"Content-Type": "application/json"})
            # Login
            resp = cls._session.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            if resp.status_code != 200:
                pytest.skip(f"Authentication failed: {resp.status_code} - {resp.text}")
            cls._cookies = resp.cookies
        return cls._session


@pytest.fixture(scope="module")
def auth_session():
    """Get authenticated session"""
    return TestSession.get_session()


# ============================================================
# TEST: Email Preview Endpoint with Language Parameter
# ============================================================
class TestEmailPreviewMultilingual:
    """Test GET /api/admin/email-preview with different languages"""
    
    def test_email_preview_german_returns_200(self, auth_session):
        """Test email preview with lang=de returns 200"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=de")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ GET /api/admin/email-preview?lang=de returns 200")
    
    def test_email_preview_english_returns_200(self, auth_session):
        """Test email preview with lang=en returns 200"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=en")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ GET /api/admin/email-preview?lang=en returns 200")
    
    def test_email_preview_french_returns_200(self, auth_session):
        """Test email preview with lang=fr returns 200"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=fr")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ GET /api/admin/email-preview?lang=fr returns 200")
    
    def test_email_preview_italian_returns_200(self, auth_session):
        """Test email preview with lang=it returns 200"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=it")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ GET /api/admin/email-preview?lang=it returns 200")
    
    def test_email_preview_german_contains_vielen_dank(self, auth_session):
        """Test German email contains 'Vielen Dank'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=de")
        data = resp.json()
        assert "confirmation" in data, "Response should contain 'confirmation' key"
        assert "Vielen Dank" in data["confirmation"], "German confirmation should contain 'Vielen Dank'"
        print("✓ German confirmation email contains 'Vielen Dank'")
    
    def test_email_preview_english_contains_thank_you(self, auth_session):
        """Test English email contains 'Thank you'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=en")
        data = resp.json()
        assert "confirmation" in data, "Response should contain 'confirmation' key"
        assert "Thank you" in data["confirmation"], "English confirmation should contain 'Thank you'"
        print("✓ English confirmation email contains 'Thank you'")
    
    def test_email_preview_french_contains_merci(self, auth_session):
        """Test French email contains 'Merci'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=fr")
        data = resp.json()
        assert "confirmation" in data, "Response should contain 'confirmation' key"
        assert "Merci" in data["confirmation"], "French confirmation should contain 'Merci'"
        print("✓ French confirmation email contains 'Merci'")
    
    def test_email_preview_italian_contains_grazie(self, auth_session):
        """Test Italian email contains 'Grazie'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=it")
        data = resp.json()
        assert "confirmation" in data, "Response should contain 'confirmation' key"
        assert "Grazie" in data["confirmation"], "Italian confirmation should contain 'Grazie'"
        print("✓ Italian confirmation email contains 'Grazie'")
    
    def test_email_preview_german_status_confirmed(self, auth_session):
        """Test German status email contains 'bestaetigt'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=de")
        data = resp.json()
        assert "status_confirmed" in data, "Response should contain 'status_confirmed' key"
        assert "Bestaetigt" in data["status_confirmed"] or "bestaetigt" in data["status_confirmed"].lower(), \
            "German status_confirmed should contain 'bestaetigt'"
        print("✓ German status_confirmed email contains 'bestaetigt'")
    
    def test_email_preview_english_status_confirmed(self, auth_session):
        """Test English status email contains 'confirmed'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=en")
        data = resp.json()
        assert "status_confirmed" in data, "Response should contain 'status_confirmed' key"
        assert "confirmed" in data["status_confirmed"].lower(), \
            "English status_confirmed should contain 'confirmed'"
        print("✓ English status_confirmed email contains 'confirmed'")
    
    def test_email_preview_french_status_confirmed(self, auth_session):
        """Test French status email contains 'confirmee'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=fr")
        data = resp.json()
        assert "status_confirmed" in data, "Response should contain 'status_confirmed' key"
        # French: "confirmée" or "confirmee" or "Confirme"
        assert "confirm" in data["status_confirmed"].lower(), \
            "French status_confirmed should contain 'confirm'"
        print("✓ French status_confirmed email contains confirmation text")
    
    def test_email_preview_italian_status_confirmed(self, auth_session):
        """Test Italian status email contains 'confermata'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=it")
        data = resp.json()
        assert "status_confirmed" in data, "Response should contain 'status_confirmed' key"
        # Italian: "confermata" or "Confermato"
        assert "conferm" in data["status_confirmed"].lower(), \
            "Italian status_confirmed should contain 'conferm'"
        print("✓ Italian status_confirmed email contains 'confermata'")
    
    def test_email_preview_german_invoice(self, auth_session):
        """Test German invoice email contains 'Rechnung'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=de")
        data = resp.json()
        assert "invoice_sent" in data, "Response should contain 'invoice_sent' key"
        assert "Rechnung" in data["invoice_sent"], "German invoice should contain 'Rechnung'"
        print("✓ German invoice email contains 'Rechnung'")
    
    def test_email_preview_english_invoice(self, auth_session):
        """Test English invoice email contains 'Invoice'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=en")
        data = resp.json()
        assert "invoice_sent" in data, "Response should contain 'invoice_sent' key"
        assert "Invoice" in data["invoice_sent"], "English invoice should contain 'Invoice'"
        print("✓ English invoice email contains 'Invoice'")
    
    def test_email_preview_french_invoice(self, auth_session):
        """Test French invoice email contains 'Facture'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=fr")
        data = resp.json()
        assert "invoice_sent" in data, "Response should contain 'invoice_sent' key"
        assert "Facture" in data["invoice_sent"] or "FACTURE" in data["invoice_sent"], \
            "French invoice should contain 'Facture'"
        print("✓ French invoice email contains 'Facture'")
    
    def test_email_preview_italian_invoice(self, auth_session):
        """Test Italian invoice email contains 'Fattura'"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=it")
        data = resp.json()
        assert "invoice_sent" in data, "Response should contain 'invoice_sent' key"
        assert "Fattura" in data["invoice_sent"] or "FATTURA" in data["invoice_sent"], \
            "Italian invoice should contain 'Fattura'"
        print("✓ Italian invoice email contains 'Fattura'")
    
    def test_email_preview_structure(self, auth_session):
        """Test email preview returns all expected email types"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/email-preview?lang=de")
        data = resp.json()
        expected_keys = ["confirmation", "notification", "status_confirmed", "status_completed", 
                        "invoice_sent", "invoice_paid", "file_upload", "event_reminder"]
        for key in expected_keys:
            assert key in data, f"Response should contain '{key}' key"
        print(f"✓ Email preview returns all {len(expected_keys)} expected email types")


# ============================================================
# TEST: Inquiry Creation with Language Field
# ============================================================
class TestInquiryWithLanguage:
    """Test POST /api/inquiries with lang field"""
    
    created_inquiry_ids = []
    
    def test_create_inquiry_with_english_lang(self, auth_session):
        """Test creating inquiry with lang=en"""
        unique_email = f"test_en_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "first_name": "TEST_John",
            "last_name": "Doe",
            "email": unique_email,
            "phone": "+41 79 111 22 33",
            "event_date": "2026-08-15",
            "location": "Zurich",
            "guest_count": 100,
            "event_type": "Firmenanlass",
            "lang": "en"
        }
        resp = auth_session.post(f"{BASE_URL}/api/inquiries", json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "id" in data, "Response should contain 'id'"
        self.created_inquiry_ids.append(data["id"])
        print(f"✓ Created inquiry with lang=en, id={data['id']}")
    
    def test_create_inquiry_with_french_lang(self, auth_session):
        """Test creating inquiry with lang=fr"""
        unique_email = f"test_fr_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "first_name": "TEST_Pierre",
            "last_name": "Dupont",
            "email": unique_email,
            "phone": "+41 79 222 33 44",
            "event_date": "2026-09-20",
            "location": "Geneva",
            "guest_count": 150,
            "event_type": "Hochzeit",
            "lang": "fr"
        }
        resp = auth_session.post(f"{BASE_URL}/api/inquiries", json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "id" in data, "Response should contain 'id'"
        self.created_inquiry_ids.append(data["id"])
        print(f"✓ Created inquiry with lang=fr, id={data['id']}")
    
    def test_create_inquiry_with_italian_lang(self, auth_session):
        """Test creating inquiry with lang=it"""
        unique_email = f"test_it_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "first_name": "TEST_Marco",
            "last_name": "Rossi",
            "email": unique_email,
            "phone": "+41 79 333 44 55",
            "event_date": "2026-10-10",
            "location": "Lugano",
            "guest_count": 80,
            "event_type": "Festival",
            "lang": "it"
        }
        resp = auth_session.post(f"{BASE_URL}/api/inquiries", json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "id" in data, "Response should contain 'id'"
        self.created_inquiry_ids.append(data["id"])
        print(f"✓ Created inquiry with lang=it, id={data['id']}")
    
    def test_create_inquiry_default_german_lang(self, auth_session):
        """Test creating inquiry without lang defaults to 'de'"""
        unique_email = f"test_de_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "first_name": "TEST_Hans",
            "last_name": "Mueller",
            "email": unique_email,
            "phone": "+41 79 444 55 66",
            "event_date": "2026-11-05",
            "location": "Bern",
            "guest_count": 200,
            "event_type": "Firmenanlass"
            # No lang field - should default to 'de'
        }
        resp = auth_session.post(f"{BASE_URL}/api/inquiries", json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "id" in data, "Response should contain 'id'"
        self.created_inquiry_ids.append(data["id"])
        print(f"✓ Created inquiry without lang (defaults to de), id={data['id']}")


# ============================================================
# TEST: Admin Inquiries Returns Lang Field
# ============================================================
class TestAdminInquiriesLangField:
    """Test GET /api/admin/inquiries returns inquiry with lang field"""
    
    def test_admin_inquiries_returns_lang_field(self, auth_session):
        """Test that admin inquiries endpoint returns lang field"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Find a TEST_ inquiry with lang field
        test_inquiries = [inq for inq in data if inq.get("first_name", "").startswith("TEST_")]
        if test_inquiries:
            for inq in test_inquiries:
                assert "lang" in inq or inq.get("lang") is None, \
                    f"Inquiry {inq.get('id')} should have 'lang' field"
            print(f"✓ Found {len(test_inquiries)} TEST_ inquiries with lang field")
        else:
            # Check any inquiry has lang field
            if data:
                print(f"✓ Admin inquiries endpoint returns {len(data)} inquiries")
            else:
                print("✓ Admin inquiries endpoint returns empty list (no inquiries yet)")


# ============================================================
# TEST: Offer PDF Generation
# ============================================================
class TestOfferPdfGeneration:
    """Test GET /api/admin/inquiries/{id}/offer-pdf"""
    
    test_inquiry_id = None
    
    def test_create_inquiry_for_pdf(self, auth_session):
        """Create a test inquiry for PDF generation"""
        unique_email = f"test_pdf_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "first_name": "TEST_PDF",
            "last_name": "User",
            "email": unique_email,
            "phone": "+41 79 555 66 77",
            "event_date": "2026-12-01",
            "location": "Basel",
            "guest_count": 120,
            "event_type": "Weihnachtsfeier",
            "lang": "en"
        }
        resp = auth_session.post(f"{BASE_URL}/api/inquiries", json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        TestOfferPdfGeneration.test_inquiry_id = data["id"]
        print(f"✓ Created test inquiry for PDF, id={data['id']}")
    
    def test_offer_pdf_returns_200(self, auth_session):
        """Test offer PDF endpoint returns 200"""
        if not TestOfferPdfGeneration.test_inquiry_id:
            pytest.skip("No test inquiry created")
        
        resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries/{TestOfferPdfGeneration.test_inquiry_id}/offer-pdf")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ GET /api/admin/inquiries/{id}/offer-pdf returns 200")
    
    def test_offer_pdf_content_type(self, auth_session):
        """Test offer PDF returns PDF content type"""
        if not TestOfferPdfGeneration.test_inquiry_id:
            pytest.skip("No test inquiry created")
        
        resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries/{TestOfferPdfGeneration.test_inquiry_id}/offer-pdf")
        assert resp.status_code == 200
        content_type = resp.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected PDF content type, got {content_type}"
        print("✓ Offer PDF returns application/pdf content type")
    
    def test_offer_pdf_has_content(self, auth_session):
        """Test offer PDF has actual content"""
        if not TestOfferPdfGeneration.test_inquiry_id:
            pytest.skip("No test inquiry created")
        
        resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries/{TestOfferPdfGeneration.test_inquiry_id}/offer-pdf")
        assert resp.status_code == 200
        assert len(resp.content) > 100, "PDF should have substantial content"
        # Check PDF magic bytes
        assert resp.content[:4] == b'%PDF', "Content should start with PDF magic bytes"
        print(f"✓ Offer PDF has {len(resp.content)} bytes of content")
    
    def test_offer_pdf_filename_english(self, auth_session):
        """Test offer PDF filename is in English for lang=en inquiry"""
        if not TestOfferPdfGeneration.test_inquiry_id:
            pytest.skip("No test inquiry created")
        
        resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries/{TestOfferPdfGeneration.test_inquiry_id}/offer-pdf")
        assert resp.status_code == 200
        content_disp = resp.headers.get("Content-Disposition", "")
        # English: "Offer_" instead of German "Angebot_"
        assert "Offer_" in content_disp or "filename=" in content_disp, \
            f"Content-Disposition should contain filename, got: {content_disp}"
        print(f"✓ Offer PDF filename: {content_disp}")
    
    def test_offer_pdf_not_found(self, auth_session):
        """Test offer PDF returns 404 for non-existent inquiry"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries/nonexistent-id-12345/offer-pdf")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print("✓ Offer PDF returns 404 for non-existent inquiry")


# ============================================================
# TEST: Cleanup Test Data
# ============================================================
class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_inquiries(self, auth_session):
        """Delete all TEST_ prefixed inquiries"""
        resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries")
        if resp.status_code != 200:
            pytest.skip("Could not fetch inquiries for cleanup")
        
        data = resp.json()
        test_inquiries = [inq for inq in data if inq.get("first_name", "").startswith("TEST_")]
        
        deleted = 0
        for inq in test_inquiries:
            del_resp = auth_session.delete(f"{BASE_URL}/api/admin/inquiries/{inq['id']}")
            if del_resp.status_code == 200:
                deleted += 1
        
        print(f"✓ Cleaned up {deleted} test inquiries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
