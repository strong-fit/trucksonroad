"""
Test Event Scout Auto-Scan Features (Iteration 15)
- GET /api/admin/event-scout/sources - returns default keywords and empty sources
- PUT /api/admin/event-scout/sources - updates sources, keywords, and scan_enabled
- POST /api/admin/event-scout/scan-now - triggers background scan (returns 200)
- Event CRUD still works
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEventScoutSources:
    """Test Event Scout sources/keywords/auto-scan config endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookie"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        yield
        self.session.close()
    
    def test_get_sources_returns_200(self):
        """GET /api/admin/event-scout/sources returns 200"""
        resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    def test_get_sources_structure(self):
        """GET /api/admin/event-scout/sources returns correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        assert resp.status_code == 200
        data = resp.json()
        
        # Check required fields exist
        assert "sources" in data, "Missing 'sources' field"
        assert "keywords" in data, "Missing 'keywords' field"
        assert "scan_enabled" in data, "Missing 'scan_enabled' field"
        assert "last_scan" in data, "Missing 'last_scan' field"
        assert "last_scan_count" in data, "Missing 'last_scan_count' field"
        
        # Check types
        assert isinstance(data["sources"], list), "sources should be a list"
        assert isinstance(data["keywords"], list), "keywords should be a list"
        assert isinstance(data["scan_enabled"], bool), "scan_enabled should be boolean"
    
    def test_get_sources_default_keywords(self):
        """GET /api/admin/event-scout/sources returns default keywords if none set"""
        resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        assert resp.status_code == 200
        data = resp.json()
        
        # Should have default keywords
        keywords = data.get("keywords", [])
        assert len(keywords) > 0, "Should have default keywords"
        # Default keywords include Festival, Weihnachtsmarkt, etc.
        print(f"Keywords found: {keywords}")
    
    def test_put_sources_update_sources(self):
        """PUT /api/admin/event-scout/sources updates sources list"""
        test_sources = ["https://test-eventkalender.ch", "https://test-festivalguide.ch"]
        
        resp = self.session.put(f"{BASE_URL}/api/admin/event-scout/sources", json={
            "sources": test_sources
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        # Verify update
        get_resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["sources"] == test_sources, f"Sources not updated: {data['sources']}"
    
    def test_put_sources_update_keywords(self):
        """PUT /api/admin/event-scout/sources updates keywords list"""
        test_keywords = ["TEST_Festival", "TEST_Markt", "TEST_Event"]
        
        resp = self.session.put(f"{BASE_URL}/api/admin/event-scout/sources", json={
            "keywords": test_keywords
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        # Verify update
        get_resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["keywords"] == test_keywords, f"Keywords not updated: {data['keywords']}"
    
    def test_put_sources_update_scan_enabled(self):
        """PUT /api/admin/event-scout/sources updates scan_enabled flag"""
        # Enable scan
        resp = self.session.put(f"{BASE_URL}/api/admin/event-scout/sources", json={
            "scan_enabled": True
        })
        assert resp.status_code == 200
        
        get_resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        data = get_resp.json()
        assert data["scan_enabled"] == True, "scan_enabled should be True"
        
        # Disable scan
        resp = self.session.put(f"{BASE_URL}/api/admin/event-scout/sources", json={
            "scan_enabled": False
        })
        assert resp.status_code == 200
        
        get_resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        data = get_resp.json()
        assert data["scan_enabled"] == False, "scan_enabled should be False"
    
    def test_put_sources_update_all_fields(self):
        """PUT /api/admin/event-scout/sources updates all fields at once"""
        test_data = {
            "sources": ["https://combined-test.ch"],
            "keywords": ["Combined", "Test"],
            "scan_enabled": True
        }
        
        resp = self.session.put(f"{BASE_URL}/api/admin/event-scout/sources", json=test_data)
        assert resp.status_code == 200
        
        get_resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/sources")
        data = get_resp.json()
        assert data["sources"] == test_data["sources"]
        assert data["keywords"] == test_data["keywords"]
        assert data["scan_enabled"] == test_data["scan_enabled"]


class TestEventScoutScanNow:
    """Test manual scan trigger endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookie"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        yield
        self.session.close()
    
    def test_scan_now_returns_200(self):
        """POST /api/admin/event-scout/scan-now returns 200"""
        resp = self.session.post(f"{BASE_URL}/api/admin/event-scout/scan-now")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    def test_scan_now_returns_message(self):
        """POST /api/admin/event-scout/scan-now returns success message"""
        resp = self.session.post(f"{BASE_URL}/api/admin/event-scout/scan-now")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data, "Response should contain message"
        print(f"Scan response: {data}")
    
    def test_scan_now_requires_auth(self):
        """POST /api/admin/event-scout/scan-now requires authentication"""
        # Use new session without login
        new_session = requests.Session()
        resp = new_session.post(f"{BASE_URL}/api/admin/event-scout/scan-now")
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        new_session.close()


class TestEventScoutCRUD:
    """Test Event Scout CRUD operations still work"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookie"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.created_event_id = None
        yield
        # Cleanup
        if self.created_event_id:
            self.session.delete(f"{BASE_URL}/api/admin/event-scout/events/{self.created_event_id}")
        self.session.close()
    
    def test_create_event(self):
        """POST /api/admin/event-scout/events creates event"""
        event_data = {
            "name": "TEST_AutoScan_Event",
            "date": "2026-06-15",
            "location": "Zürich",
            "type": "festival",
            "description": "Test event for auto-scan testing",
            "organizer_email": "test@example.ch",
            "website": "https://test-event.ch"
        }
        
        resp = self.session.post(f"{BASE_URL}/api/admin/event-scout/events", json=event_data)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "id" in data, "Response should contain id"
        assert data["name"] == event_data["name"]
        assert data["status"] == "new"
        self.created_event_id = data["id"]
    
    def test_get_events(self):
        """GET /api/admin/event-scout/events returns list"""
        resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/events")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list), "Should return a list"
    
    def test_update_event_status(self):
        """PUT /api/admin/event-scout/events/{id} updates status"""
        # First create an event
        event_data = {
            "name": "TEST_Update_Status_Event",
            "date": "2026-07-20",
            "location": "Bern",
            "type": "markt"
        }
        create_resp = self.session.post(f"{BASE_URL}/api/admin/event-scout/events", json=event_data)
        assert create_resp.status_code == 200
        event_id = create_resp.json()["id"]
        self.created_event_id = event_id
        
        # Update status
        update_resp = self.session.put(f"{BASE_URL}/api/admin/event-scout/events/{event_id}", json={
            "status": "contacted"
        })
        assert update_resp.status_code == 200
        
        # Verify update
        get_resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/events")
        events = get_resp.json()
        updated_event = next((e for e in events if e["id"] == event_id), None)
        assert updated_event is not None, "Event should exist"
        assert updated_event["status"] == "contacted", f"Status should be 'contacted', got {updated_event['status']}"
    
    def test_delete_event(self):
        """DELETE /api/admin/event-scout/events/{id} deletes event"""
        # First create an event
        event_data = {
            "name": "TEST_Delete_Event",
            "date": "2026-08-10",
            "location": "Basel",
            "type": "strassenfest"
        }
        create_resp = self.session.post(f"{BASE_URL}/api/admin/event-scout/events", json=event_data)
        assert create_resp.status_code == 200
        event_id = create_resp.json()["id"]
        
        # Delete event
        delete_resp = self.session.delete(f"{BASE_URL}/api/admin/event-scout/events/{event_id}")
        assert delete_resp.status_code == 200
        
        # Verify deletion
        get_resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/events")
        events = get_resp.json()
        deleted_event = next((e for e in events if e["id"] == event_id), None)
        assert deleted_event is None, "Event should be deleted"
        
        # Clear created_event_id since we already deleted it
        self.created_event_id = None


class TestPublicAgenda:
    """Test public agenda endpoint still works"""
    
    def test_agenda_returns_200(self):
        """GET /api/agenda returns 200"""
        resp = requests.get(f"{BASE_URL}/api/agenda")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    def test_agenda_returns_list(self):
        """GET /api/agenda returns a list"""
        resp = requests.get(f"{BASE_URL}/api/agenda")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list), "Should return a list"


class TestSourcesRequiresAuth:
    """Test that sources endpoints require authentication"""
    
    def test_get_sources_requires_auth(self):
        """GET /api/admin/event-scout/sources requires auth"""
        resp = requests.get(f"{BASE_URL}/api/admin/event-scout/sources")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
    
    def test_put_sources_requires_auth(self):
        """PUT /api/admin/event-scout/sources requires auth"""
        resp = requests.put(f"{BASE_URL}/api/admin/event-scout/sources", json={"sources": []})
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


class TestCleanup:
    """Cleanup test data and restore defaults"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookie"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200
        yield
        self.session.close()
    
    def test_cleanup_test_events(self):
        """Clean up TEST_ prefixed events"""
        resp = self.session.get(f"{BASE_URL}/api/admin/event-scout/events")
        if resp.status_code == 200:
            events = resp.json()
            for event in events:
                if event.get("name", "").startswith("TEST_"):
                    self.session.delete(f"{BASE_URL}/api/admin/event-scout/events/{event['id']}")
        assert True
    
    def test_restore_default_keywords(self):
        """Restore default keywords"""
        default_keywords = ["Festival", "Weihnachtsmarkt", "Strassenfest", "Food Festival", "Markt"]
        resp = self.session.put(f"{BASE_URL}/api/admin/event-scout/sources", json={
            "keywords": default_keywords,
            "scan_enabled": False
        })
        assert resp.status_code == 200
