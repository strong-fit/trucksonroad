"""
Test suite for Batch 5 features:
1. SEO sitemap.xml endpoint
2. PDF download for event organizers
3. Admin Trucks CRUD
4. Admin FAQs CRUD
5. Email template preview
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPublicEndpoints:
    """Public endpoints - no auth required"""
    
    def test_sitemap_returns_valid_xml(self):
        """Sitemap endpoint returns valid XML with all pages and truck slugs"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "")
        
        # Verify XML structure
        content = response.text
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in content
        
        # Verify required pages
        assert "https://truckonroad.ch/" in content
        assert "https://truckonroad.ch/fuer-veranstalter" in content
        assert "https://truckonroad.ch/private-events" in content
        assert "https://truckonroad.ch/ueber-uns" in content
        assert "https://truckonroad.ch/kontakt" in content
        assert "https://truckonroad.ch/anfrage" in content
        assert "https://truckonroad.ch/faq" in content
        
        # Verify truck slugs are included
        assert "https://truckonroad.ch/trucks/burger-truck" in content
        assert "https://truckonroad.ch/trucks/bowl-truck" in content
        assert "https://truckonroad.ch/trucks/empanadas-truck" in content
        assert "https://truckonroad.ch/trucks/retro-trailer" in content
        
        # Verify priority and changefreq attributes
        assert "<priority>" in content
        assert "<changefreq>" in content
        print("✓ Sitemap returns valid XML with all pages and truck slugs")
    
    def test_pdf_download_returns_valid_pdf(self):
        """PDF download endpoint returns valid PDF file"""
        response = requests.get(f"{BASE_URL}/api/download/veranstalter-pdf")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        
        # Verify Content-Disposition header for download
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp
        assert "TruckOnRoad_Veranstalter.pdf" in content_disp
        
        # Verify PDF magic bytes
        assert response.content[:4] == b'%PDF'
        print("✓ PDF download returns valid PDF with correct headers")
    
    def test_public_trucks_endpoint(self):
        """Public trucks endpoint returns all 6 trucks"""
        response = requests.get(f"{BASE_URL}/api/trucks")
        assert response.status_code == 200
        trucks = response.json()
        assert len(trucks) == 6
        
        # Verify truck slugs
        slugs = [t["slug"] for t in trucks]
        assert "burger-truck" in slugs
        assert "chicken-burger-truck" in slugs
        assert "bowl-truck" in slugs
        assert "pocket-bowl-truck" in slugs
        assert "empanadas-truck" in slugs
        assert "retro-trailer" in slugs
        print("✓ Public trucks endpoint returns all 6 trucks")
    
    def test_public_faqs_endpoint(self):
        """Public FAQs endpoint returns FAQs"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200
        faqs = response.json()
        assert len(faqs) >= 8  # Seeded FAQs
        
        # Verify FAQ structure
        faq = faqs[0]
        assert "id" in faq
        assert "question_de" in faq
        assert "answer_de" in faq
        assert "order" in faq
        print(f"✓ Public FAQs endpoint returns {len(faqs)} FAQs")


class TestAdminAuth:
    """Admin authentication tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return session
    
    def test_admin_login(self, auth_session):
        """Admin can login successfully"""
        response = auth_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        user = response.json()
        assert user["email"] == "admin@truckonroad.ch"
        assert user["role"] == "admin"
        print("✓ Admin login successful")


class TestAdminTrucks:
    """Admin Trucks CRUD tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_admin_get_trucks(self, auth_session):
        """Admin can get all trucks"""
        response = auth_session.get(f"{BASE_URL}/api/admin/trucks")
        assert response.status_code == 200
        trucks = response.json()
        assert len(trucks) == 6
        
        # Verify truck structure has editable fields
        truck = trucks[0]
        assert "slug" in truck
        assert "name_de" in truck
        assert "name_en" in truck
        assert "desc_de" in truck or "description_de" in truck
        assert "image" in truck
        assert "capacity" in truck
        assert "menu_de" in truck
        print("✓ Admin can get all 6 trucks with editable fields")
    
    def test_admin_update_truck(self, auth_session):
        """Admin can update a truck"""
        # Get current truck data
        response = auth_session.get(f"{BASE_URL}/api/admin/trucks")
        trucks = response.json()
        burger_truck = next(t for t in trucks if t["slug"] == "burger-truck")
        
        # Update truck
        original_capacity = burger_truck.get("capacity", "")
        update_data = {
            "name_de": burger_truck["name_de"],
            "capacity": "TEST_bis 350 Gäste/h"
        }
        response = auth_session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json=update_data)
        assert response.status_code == 200
        
        # Verify update persisted
        response = auth_session.get(f"{BASE_URL}/api/admin/trucks")
        trucks = response.json()
        updated_truck = next(t for t in trucks if t["slug"] == "burger-truck")
        assert updated_truck["capacity"] == "TEST_bis 350 Gäste/h"
        
        # Restore original
        auth_session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={"capacity": original_capacity})
        print("✓ Admin can update truck and changes persist")
    
    def test_admin_trucks_requires_auth(self):
        """Admin trucks endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/trucks")
        assert response.status_code == 401
        print("✓ Admin trucks endpoint requires authentication")


class TestAdminFAQs:
    """Admin FAQs CRUD tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_admin_get_faqs(self, auth_session):
        """Admin can get all FAQs"""
        response = auth_session.get(f"{BASE_URL}/api/admin/faqs")
        assert response.status_code == 200
        faqs = response.json()
        assert len(faqs) >= 8
        
        # Verify FAQ structure
        faq = faqs[0]
        assert "id" in faq
        assert "question_de" in faq
        assert "answer_de" in faq
        assert "question_en" in faq
        assert "answer_en" in faq
        assert "order" in faq
        print(f"✓ Admin can get {len(faqs)} FAQs")
    
    def test_admin_create_faq(self, auth_session):
        """Admin can create a new FAQ"""
        new_faq = {
            "question_de": "TEST_Testfrage?",
            "answer_de": "TEST_Testantwort.",
            "question_en": "TEST_Test question?",
            "answer_en": "TEST_Test answer.",
            "order": 99
        }
        response = auth_session.post(f"{BASE_URL}/api/admin/faqs", json=new_faq)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        faq_id = data["id"]
        
        # Verify FAQ was created
        response = auth_session.get(f"{BASE_URL}/api/admin/faqs")
        faqs = response.json()
        created_faq = next((f for f in faqs if f["id"] == faq_id), None)
        assert created_faq is not None
        assert created_faq["question_de"] == "TEST_Testfrage?"
        
        # Cleanup
        auth_session.delete(f"{BASE_URL}/api/admin/faqs/{faq_id}")
        print("✓ Admin can create FAQ and it persists")
    
    def test_admin_update_faq(self, auth_session):
        """Admin can update an existing FAQ"""
        # Create a test FAQ first
        new_faq = {
            "question_de": "TEST_Update Frage?",
            "answer_de": "TEST_Original Antwort.",
            "question_en": "TEST_Update question?",
            "answer_en": "TEST_Original answer.",
            "order": 98
        }
        response = auth_session.post(f"{BASE_URL}/api/admin/faqs", json=new_faq)
        faq_id = response.json()["id"]
        
        # Update the FAQ
        updated_faq = {
            "question_de": "TEST_Update Frage?",
            "answer_de": "TEST_Aktualisierte Antwort.",
            "question_en": "TEST_Update question?",
            "answer_en": "TEST_Updated answer.",
            "order": 98
        }
        response = auth_session.put(f"{BASE_URL}/api/admin/faqs/{faq_id}", json=updated_faq)
        assert response.status_code == 200
        
        # Verify update persisted
        response = auth_session.get(f"{BASE_URL}/api/admin/faqs")
        faqs = response.json()
        updated = next((f for f in faqs if f["id"] == faq_id), None)
        assert updated["answer_de"] == "TEST_Aktualisierte Antwort."
        
        # Cleanup
        auth_session.delete(f"{BASE_URL}/api/admin/faqs/{faq_id}")
        print("✓ Admin can update FAQ and changes persist")
    
    def test_admin_delete_faq(self, auth_session):
        """Admin can delete a FAQ"""
        # Create a test FAQ first
        new_faq = {
            "question_de": "TEST_Delete Frage?",
            "answer_de": "TEST_Delete Antwort.",
            "question_en": "TEST_Delete question?",
            "answer_en": "TEST_Delete answer.",
            "order": 97
        }
        response = auth_session.post(f"{BASE_URL}/api/admin/faqs", json=new_faq)
        faq_id = response.json()["id"]
        
        # Delete the FAQ
        response = auth_session.delete(f"{BASE_URL}/api/admin/faqs/{faq_id}")
        assert response.status_code == 200
        
        # Verify deletion
        response = auth_session.get(f"{BASE_URL}/api/admin/faqs")
        faqs = response.json()
        deleted = next((f for f in faqs if f["id"] == faq_id), None)
        assert deleted is None
        print("✓ Admin can delete FAQ")
    
    def test_admin_faqs_requires_auth(self):
        """Admin FAQs endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/faqs")
        assert response.status_code == 401
        print("✓ Admin FAQs endpoint requires authentication")


class TestEmailPreview:
    """Email preview endpoint tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_email_preview_returns_both_templates(self, auth_session):
        """Email preview returns confirmation and notification templates"""
        response = auth_session.get(f"{BASE_URL}/api/admin/email-preview")
        assert response.status_code == 200
        data = response.json()
        
        # Verify both templates present
        assert "confirmation" in data
        assert "notification" in data
        
        # Verify confirmation email content
        confirmation = data["confirmation"]
        assert "Max" in confirmation  # Sample name
        assert "Mustermann" in confirmation
        assert "15.06.2026" in confirmation  # Sample date
        assert "Zürich" in confirmation  # Sample location
        assert "TRUCKONROAD" in confirmation or "TruckOnRoad" in confirmation
        
        # Verify notification email content
        notification = data["notification"]
        assert "Max" in notification
        assert "Mustermann" in notification
        assert "NEUE ANFRAGE" in notification or "Neue Anfrage" in notification
        print("✓ Email preview returns both confirmation and notification templates")
    
    def test_email_preview_requires_auth(self):
        """Email preview endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/email-preview")
        assert response.status_code == 401
        print("✓ Email preview endpoint requires authentication")


class TestSEOMetaTags:
    """SEO meta tags verification (checked via index.html content)"""
    
    def test_index_html_has_meta_tags(self):
        """Verify index.html has required SEO meta tags"""
        # Read index.html directly
        with open("/app/frontend/public/index.html", "r") as f:
            content = f.read()
        
        # Required meta tags
        assert 'name="description"' in content
        assert 'property="og:title"' in content
        assert 'property="og:description"' in content
        assert 'name="twitter:card"' in content
        assert 'rel="canonical"' in content
        
        # Verify content
        assert "TruckOnRoad" in content
        assert "Foodtruck" in content or "Foodtrucks" in content
        assert "truckonroad.ch" in content
        print("✓ index.html has all required SEO meta tags")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
