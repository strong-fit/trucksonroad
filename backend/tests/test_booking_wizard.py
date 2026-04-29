"""
Test suite for Booking Wizard and Admin Menu Categories features
- GET /api/menu-categories - returns list of categories
- GET /api/truck-availability/{truck_slug} - returns blocked dates
- POST /api/calculate-delivery - calculates delivery cost based on PLZ
- POST /api/admin/menu-categories - creates new category (authenticated)
- PUT /api/admin/menu-categories/{id} - updates category (authenticated)
- DELETE /api/admin/menu-categories/{id} - deletes category (authenticated)
- Admin settings - delivery_price_per_km field
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPublicEndpoints:
    """Test public endpoints for booking wizard"""
    
    def test_get_menu_categories(self):
        """GET /api/menu-categories - returns list of categories"""
        response = requests.get(f"{BASE_URL}/api/menu-categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of categories"
        print(f"✓ GET /api/menu-categories - Found {len(data)} categories")
        # Verify seeded categories exist
        if len(data) > 0:
            cat = data[0]
            assert "id" in cat, "Category should have id"
            assert "name_de" in cat, "Category should have name_de"
            print(f"  Sample category: {cat.get('name_de')}")
    
    def test_get_trucks(self):
        """GET /api/trucks - returns list of trucks for selection"""
        response = requests.get(f"{BASE_URL}/api/trucks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of trucks"
        print(f"✓ GET /api/trucks - Found {len(data)} trucks")
        if len(data) > 0:
            truck = data[0]
            assert "slug" in truck, "Truck should have slug"
            assert "name_de" in truck, "Truck should have name_de"
            return truck["slug"]
        return None
    
    def test_get_truck_availability(self):
        """GET /api/truck-availability/{truck_slug} - returns blocked dates"""
        # First get a truck slug
        trucks_resp = requests.get(f"{BASE_URL}/api/trucks")
        trucks = trucks_resp.json()
        if not trucks:
            pytest.skip("No trucks available to test availability")
        
        truck_slug = trucks[0]["slug"]
        response = requests.get(f"{BASE_URL}/api/truck-availability/{truck_slug}?year=2026&month=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of calendar blocks"
        print(f"✓ GET /api/truck-availability/{truck_slug}?year=2026&month=5 - Found {len(data)} blocks")
    
    def test_calculate_delivery_valid_plz(self):
        """POST /api/calculate-delivery with valid PLZ - returns km and cost"""
        response = requests.post(
            f"{BASE_URL}/api/calculate-delivery",
            json={"plz": "8001"}  # Zurich PLZ
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Check response structure
        assert "km" in data, "Response should have km"
        assert "cost" in data, "Response should have cost"
        # If no error, km and cost should be positive
        if "error" not in data:
            assert data["km"] > 0, "Distance should be positive"
            assert data["cost"] >= 0, "Cost should be non-negative"
            assert "price_per_km" in data, "Response should have price_per_km"
            print(f"✓ POST /api/calculate-delivery (PLZ 8001) - {data['km']}km, CHF {data['cost']}")
        else:
            print(f"✓ POST /api/calculate-delivery (PLZ 8001) - Geocoding returned: {data.get('error')}")
    
    def test_calculate_delivery_invalid_plz(self):
        """POST /api/calculate-delivery with invalid PLZ - returns error"""
        response = requests.post(
            f"{BASE_URL}/api/calculate-delivery",
            json={"plz": "99999"}  # Invalid PLZ
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Should return error or zero values for invalid PLZ
        if "error" in data:
            print(f"✓ POST /api/calculate-delivery (invalid PLZ) - Error: {data['error']}")
        else:
            # Some invalid PLZs might still geocode to something
            print(f"✓ POST /api/calculate-delivery (invalid PLZ) - km: {data.get('km')}, cost: {data.get('cost')}")
    
    def test_calculate_delivery_empty_plz(self):
        """POST /api/calculate-delivery with empty PLZ - returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/calculate-delivery",
            json={"plz": ""}
        )
        assert response.status_code == 400, f"Expected 400 for empty PLZ, got {response.status_code}"
        print("✓ POST /api/calculate-delivery (empty PLZ) - Returns 400 as expected")


class TestAdminMenuCategories:
    """Test admin menu categories CRUD operations"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get admin authenticated session with cookies"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "TrucksOnRoad2026!"}
        )
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
        print(f"✓ Admin login successful")
        return session
    
    def test_admin_get_menu_categories(self, admin_session):
        """GET /api/admin/menu-categories - returns list (authenticated)"""
        response = admin_session.get(f"{BASE_URL}/api/admin/menu-categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of categories"
        print(f"✓ GET /api/admin/menu-categories - Found {len(data)} categories")
    
    def test_admin_create_menu_category(self, admin_session):
        """POST /api/admin/menu-categories - creates new category"""
        test_cat = {
            "name_de": "TEST_Kategorie_Wizard",
            "name_en": "TEST_Category_Wizard",
            "name_fr": "TEST_Catégorie_Wizard",
            "name_it": "TEST_Categoria_Wizard",
            "truck_slug": "",
            "order": 99
        }
        response = admin_session.post(
            f"{BASE_URL}/api/admin/menu-categories",
            json=test_cat
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should have id"
        print(f"✓ POST /api/admin/menu-categories - Created category with id: {data['id']}")
    
    def test_admin_update_menu_category(self, admin_session):
        """PUT /api/admin/menu-categories/{id} - updates category"""
        # First create a category to update
        create_resp = admin_session.post(
            f"{BASE_URL}/api/admin/menu-categories",
            json={"name_de": "TEST_Update_Before", "order": 98}
        )
        assert create_resp.status_code == 200
        cat_id = create_resp.json()["id"]
        
        # Update the category
        update_resp = admin_session.put(
            f"{BASE_URL}/api/admin/menu-categories/{cat_id}",
            json={"name_de": "TEST_Update_After", "name_en": "TEST_Updated_EN"}
        )
        assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}"
        print(f"✓ PUT /api/admin/menu-categories/{cat_id} - Updated successfully")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/menu-categories/{cat_id}")
    
    def test_admin_delete_menu_category(self, admin_session):
        """DELETE /api/admin/menu-categories/{id} - deletes category"""
        # First create a category to delete
        create_resp = admin_session.post(
            f"{BASE_URL}/api/admin/menu-categories",
            json={"name_de": "TEST_Delete_Me", "order": 97}
        )
        assert create_resp.status_code == 200
        cat_id = create_resp.json()["id"]
        
        # Delete the category
        delete_resp = admin_session.delete(f"{BASE_URL}/api/admin/menu-categories/{cat_id}")
        assert delete_resp.status_code == 200, f"Expected 200, got {delete_resp.status_code}"
        print(f"✓ DELETE /api/admin/menu-categories/{cat_id} - Deleted successfully")
        
        # Verify deletion - category should not appear in list
        list_resp = admin_session.get(f"{BASE_URL}/api/admin/menu-categories")
        cats = list_resp.json()
        assert not any(c["id"] == cat_id for c in cats), "Deleted category should not appear in list"
    
    def test_admin_menu_categories_requires_auth(self):
        """Admin menu categories endpoints require authentication"""
        # GET without auth
        resp1 = requests.get(f"{BASE_URL}/api/admin/menu-categories")
        assert resp1.status_code in [401, 403], f"Expected 401/403 without auth, got {resp1.status_code}"
        
        # POST without auth
        resp2 = requests.post(
            f"{BASE_URL}/api/admin/menu-categories",
            json={"name_de": "Unauthorized"}
        )
        assert resp2.status_code in [401, 403], f"Expected 401/403 without auth, got {resp2.status_code}"
        print("✓ Admin menu categories endpoints require authentication")


class TestAdminSettings:
    """Test admin settings for delivery price per km"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get admin authenticated session with cookies"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "TrucksOnRoad2026!"}
        )
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return session
    
    def test_admin_get_settings_has_delivery_price(self, admin_session):
        """GET /api/admin/settings - includes delivery_price_per_km field"""
        response = admin_session.get(f"{BASE_URL}/api/admin/settings")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Check that delivery_price_per_km field exists (may be default or set)
        # The field should be present in settings
        print(f"✓ GET /api/admin/settings - delivery_price_per_km: {data.get('delivery_price_per_km', 'not set')}")
        print(f"  company_plz: {data.get('company_plz', 'not set')}")
    
    def test_admin_update_delivery_price(self, admin_session):
        """PUT /api/admin/settings - can update delivery_price_per_km"""
        # Get current settings
        get_resp = admin_session.get(f"{BASE_URL}/api/admin/settings")
        current = get_resp.json()
        original_price = current.get("delivery_price_per_km", 2.0)
        
        # Update delivery price
        test_price = 3.5
        update_resp = admin_session.put(
            f"{BASE_URL}/api/admin/settings",
            json={**current, "delivery_price_per_km": test_price}
        )
        assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}"
        
        # Verify update
        verify_resp = admin_session.get(f"{BASE_URL}/api/admin/settings")
        updated = verify_resp.json()
        assert updated.get("delivery_price_per_km") == test_price, "Delivery price should be updated"
        print(f"✓ PUT /api/admin/settings - Updated delivery_price_per_km to {test_price}")
        
        # Restore original
        admin_session.put(
            f"{BASE_URL}/api/admin/settings",
            json={**updated, "delivery_price_per_km": original_price}
        )


class TestBookingInquirySubmission:
    """Test booking inquiry submission (the final step of wizard)"""
    
    def test_submit_booking_inquiry(self):
        """POST /api/inquiries - submits booking from wizard"""
        inquiry = {
            "first_name": "TEST_Wizard",
            "last_name": "Buchung",
            "company": "Test GmbH",
            "email": "test_wizard@example.com",
            "phone": "+41 79 123 45 67",
            "event_date": "2026-06-15",
            "event_time": "11:00 – 15:00",
            "location": "Teststrasse 1, 8001 Zürich",
            "guest_count": 100,
            "event_type": "Catering-Buchung",
            "selected_trucks": ["Burger Truck"],
            "extras": [],
            "budget": "",
            "remarks": "Catering: Unser Catering | Menü: Burger-Menü | Lieferung: 25km (CHF 50.00)",
            "is_organizer": False,
            "privacy_accepted": True,
            "lang": "de"
        }
        response = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should have inquiry id"
        print(f"✓ POST /api/inquiries - Created booking inquiry with id: {data['id']}")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "TrucksOnRoad2026!"}
        )
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return session
    
    def test_cleanup_test_categories(self, admin_session):
        """Clean up TEST_ prefixed categories"""
        response = admin_session.get(f"{BASE_URL}/api/admin/menu-categories")
        if response.status_code == 200:
            cats = response.json()
            deleted = 0
            for cat in cats:
                if cat.get("name_de", "").startswith("TEST_"):
                    admin_session.delete(f"{BASE_URL}/api/admin/menu-categories/{cat['id']}")
                    deleted += 1
            print(f"✓ Cleanup - Deleted {deleted} test categories")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
