"""
Test suite for multilingual support (ES) and Quick Inquiry Widget
Tests: Spanish language support, Quick Inquiry API endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestQuickInquiryAPI:
    """Quick Inquiry endpoint tests"""
    
    def test_quick_inquiry_with_name_and_contact(self):
        """Test POST /api/quick-inquiry with name and contact (phone/email)"""
        response = requests.post(f"{BASE_URL}/api/quick-inquiry", json={
            "name": "Test User",
            "contact": "+41 79 123 4567"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "id" in data
        assert len(data["id"]) > 0
        print(f"✓ Quick inquiry created with ID: {data['id']}")
    
    def test_quick_inquiry_with_email_contact(self):
        """Test POST /api/quick-inquiry with email as contact"""
        response = requests.post(f"{BASE_URL}/api/quick-inquiry", json={
            "name": "Email Test User",
            "contact": "test@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "id" in data
        print(f"✓ Quick inquiry with email created with ID: {data['id']}")
    
    def test_quick_inquiry_minimal_payload(self):
        """Test POST /api/quick-inquiry with minimal required fields"""
        response = requests.post(f"{BASE_URL}/api/quick-inquiry", json={
            "name": "Minimal Test"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"✓ Quick inquiry with minimal payload created")
    
    def test_quick_inquiry_full_payload(self):
        """Test POST /api/quick-inquiry with all optional fields"""
        response = requests.post(f"{BASE_URL}/api/quick-inquiry", json={
            "name": "Full Test User",
            "contact": "+41 79 999 8888",
            "event_date": "2026-06-15",
            "location": "Zürich",
            "guest_count": 100,
            "concept": "Burger Truck",
            "email": "full@example.com",
            "phone": "+41 79 999 8888"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"✓ Quick inquiry with full payload created")


class TestPublicEndpoints:
    """Test public endpoints that support multilingual content"""
    
    def test_trucks_endpoint(self):
        """Test GET /api/trucks returns truck data"""
        response = requests.get(f"{BASE_URL}/api/trucks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Trucks endpoint returned {len(data)} trucks")
    
    def test_faqs_endpoint(self):
        """Test GET /api/faqs returns FAQ data"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ FAQs endpoint returned {len(data)} FAQs")
    
    def test_contact_info_endpoint(self):
        """Test GET /api/contact-info returns contact information"""
        response = requests.get(f"{BASE_URL}/api/contact-info")
        assert response.status_code == 200
        data = response.json()
        assert "company_name" in data
        assert "phone" in data
        assert "email" in data
        print(f"✓ Contact info endpoint working")
    
    def test_reviews_endpoint(self):
        """Test GET /api/reviews returns reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Reviews endpoint returned {len(data)} reviews")


class TestAvailabilityEndpoint:
    """Test availability endpoint"""
    
    def test_availability_endpoint(self):
        """Test GET /api/availability returns availability data"""
        response = requests.get(f"{BASE_URL}/api/availability")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Availability endpoint returned {len(data)} entries")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
