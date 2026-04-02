"""
Test suite for Agenda and Event Scout features
- GET /api/agenda - Public agenda endpoint
- Event Scout CRUD operations
- Admin authentication required for Event Scout
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@truckonroad.ch"
ADMIN_PASSWORD = "TruckOnRoad2026!"


class TestPublicAgenda:
    """Test public agenda endpoint"""
    
    def test_agenda_endpoint_returns_200(self):
        """GET /api/agenda should return 200"""
        response = requests.get(f"{BASE_URL}/api/agenda")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ GET /api/agenda returns 200")
        
    def test_agenda_returns_list(self):
        """GET /api/agenda should return a list"""
        response = requests.get(f"{BASE_URL}/api/agenda")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ GET /api/agenda returns list with {len(data)} events")
        
    def test_agenda_event_structure(self):
        """Agenda events should have expected fields"""
        response = requests.get(f"{BASE_URL}/api/agenda")
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            event = data[0]
            # Check expected fields exist
            expected_fields = ['id', 'event_date', 'location']
            for field in expected_fields:
                assert field in event, f"Missing field: {field}"
            print(f"✓ Agenda event has expected fields: {list(event.keys())}")
        else:
            print("⚠ No events in agenda to verify structure")


class TestAdminAuth:
    """Test admin authentication for Event Scout"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return session
    
    def test_admin_login(self):
        """Admin should be able to login"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = response.json()
        assert data.get("role") == "admin", f"Expected admin role, got {data.get('role')}"
        print(f"✓ Admin login successful: {data.get('email')}")
        return session


class TestEventScoutSearch:
    """Test Event Scout search endpoint"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return session
    
    def test_search_requires_auth(self):
        """Event Scout search should require authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/event-scout/search", json={
            "query": "Weihnachtsmarkt",
            "region": "Zürich"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Event Scout search requires authentication")
    
    def test_search_without_api_key(self, admin_session):
        """Search should return error when no Perplexity API key configured"""
        response = admin_session.post(f"{BASE_URL}/api/admin/event-scout/search", json={
            "query": "Weihnachtsmarkt",
            "region": "Zürich"
        })
        # Expected: 400 with message about missing API key
        # OR 500 if API key is configured but invalid
        assert response.status_code in [400, 500], f"Expected 400 or 500, got {response.status_code}"
        if response.status_code == 400:
            data = response.json()
            assert "API-Key" in data.get("detail", "") or "api" in data.get("detail", "").lower(), \
                f"Expected API key error message, got: {data.get('detail')}"
            print(f"✓ Search returns expected error when no API key: {data.get('detail')}")
        else:
            print(f"✓ Search returns 500 (API key may be configured but invalid)")
    
    def test_search_requires_query(self, admin_session):
        """Search should require a query parameter"""
        response = admin_session.post(f"{BASE_URL}/api/admin/event-scout/search", json={
            "query": "",
            "region": "Zürich"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Search requires query parameter")


class TestEventScoutCRUD:
    """Test Event Scout CRUD operations"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return session
    
    def test_get_scouted_events_requires_auth(self):
        """GET scouted events should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/event-scout/events")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET scouted events requires authentication")
    
    def test_get_scouted_events(self, admin_session):
        """GET scouted events should return list"""
        response = admin_session.get(f"{BASE_URL}/api/admin/event-scout/events")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ GET scouted events returns list with {len(data)} events")
    
    def test_create_scouted_event(self, admin_session):
        """POST should create a new scouted event"""
        test_event = {
            "name": "TEST_Weihnachtsmarkt Zürich 2026",
            "date": "15.-24. Dezember 2026",
            "location": "Zürich Hauptbahnhof",
            "type": "weihnachtsmarkt",
            "description": "Traditioneller Weihnachtsmarkt am HB",
            "organizer_email": "test@example.com",
            "website": "https://example.com/weihnachtsmarkt"
        }
        response = admin_session.post(f"{BASE_URL}/api/admin/event-scout/events", json=test_event)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "id" in data, "Response should contain id"
        assert data.get("name") == test_event["name"], "Name should match"
        assert data.get("status") == "new", "Initial status should be 'new'"
        print(f"✓ Created scouted event: {data.get('id')}")
        return data.get("id")
    
    def test_update_scouted_event_status(self, admin_session):
        """PUT should update event status"""
        # First create an event
        test_event = {
            "name": "TEST_Update Status Event",
            "date": "2026-06-15",
            "location": "Basel",
            "type": "festival"
        }
        create_response = admin_session.post(f"{BASE_URL}/api/admin/event-scout/events", json=test_event)
        assert create_response.status_code == 200
        event_id = create_response.json().get("id")
        
        # Update status
        update_response = admin_session.put(f"{BASE_URL}/api/admin/event-scout/events/{event_id}", json={
            "status": "contacted"
        })
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}"
        print(f"✓ Updated event status to 'contacted'")
        
        # Verify update
        get_response = admin_session.get(f"{BASE_URL}/api/admin/event-scout/events")
        events = get_response.json()
        updated_event = next((e for e in events if e.get("id") == event_id), None)
        assert updated_event is not None, "Event should exist"
        assert updated_event.get("status") == "contacted", f"Status should be 'contacted', got {updated_event.get('status')}"
        print(f"✓ Verified event status is 'contacted'")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/event-scout/events/{event_id}")
    
    def test_delete_scouted_event(self, admin_session):
        """DELETE should remove event"""
        # First create an event
        test_event = {
            "name": "TEST_Delete Event",
            "date": "2026-07-01",
            "location": "Bern",
            "type": "markt"
        }
        create_response = admin_session.post(f"{BASE_URL}/api/admin/event-scout/events", json=test_event)
        assert create_response.status_code == 200
        event_id = create_response.json().get("id")
        
        # Delete event
        delete_response = admin_session.delete(f"{BASE_URL}/api/admin/event-scout/events/{event_id}")
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        print(f"✓ Deleted event: {event_id}")
        
        # Verify deletion
        get_response = admin_session.get(f"{BASE_URL}/api/admin/event-scout/events")
        events = get_response.json()
        deleted_event = next((e for e in events if e.get("id") == event_id), None)
        assert deleted_event is None, "Event should be deleted"
        print(f"✓ Verified event is deleted")


class TestAdminSettings:
    """Test Perplexity API key in settings"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return session
    
    def test_settings_has_perplexity_key_field(self, admin_session):
        """Settings should include perplexity_api_key field"""
        response = admin_session.get(f"{BASE_URL}/api/admin/settings")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "perplexity_api_key" in data, "Settings should have perplexity_api_key field"
        print(f"✓ Settings includes perplexity_api_key field (value: {'set' if data.get('perplexity_api_key') else 'empty'})")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return session
    
    def test_cleanup_test_events(self, admin_session):
        """Clean up TEST_ prefixed events"""
        response = admin_session.get(f"{BASE_URL}/api/admin/event-scout/events")
        if response.status_code == 200:
            events = response.json()
            test_events = [e for e in events if e.get("name", "").startswith("TEST_")]
            for event in test_events:
                admin_session.delete(f"{BASE_URL}/api/admin/event-scout/events/{event['id']}")
                print(f"  Cleaned up: {event['name']}")
            print(f"✓ Cleaned up {len(test_events)} test events")
        else:
            print("⚠ Could not fetch events for cleanup")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
