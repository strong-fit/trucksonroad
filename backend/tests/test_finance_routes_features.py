"""
Test Finance and Routes Features - Batch 7
Tests for:
- Finance API: PUT /api/admin/inquiries/{id}/finance
- Finance API: GET /api/admin/finance/overview
- Geocode API: GET /api/admin/geocode
- Route API: GET /api/admin/route
- Route Optimize API: GET /api/admin/route/optimize
- Events Map API: GET /api/admin/events-map
- Coords Update API: PUT /api/admin/inquiries/{id}/coords
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication for admin endpoints"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create authenticated session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_resp = s.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        print(f"✓ Login successful")
        return s


class TestFinanceAPI(TestAuth):
    """Finance endpoint tests"""
    
    def test_finance_overview_endpoint(self, session):
        """GET /api/admin/finance/overview returns totals, by_truck, by_month"""
        resp = session.get(f"{BASE_URL}/api/admin/finance/overview")
        assert resp.status_code == 200, f"Finance overview failed: {resp.text}"
        
        data = resp.json()
        # Verify structure
        assert "total_revenue" in data, "Missing total_revenue"
        assert "total_costs" in data, "Missing total_costs"
        assert "total_profit" in data, "Missing total_profit"
        assert "events_with_finance" in data, "Missing events_with_finance"
        assert "by_month" in data, "Missing by_month"
        assert "by_truck" in data, "Missing by_truck"
        
        # Verify types
        assert isinstance(data["total_revenue"], (int, float))
        assert isinstance(data["total_costs"], (int, float))
        assert isinstance(data["total_profit"], (int, float))
        assert isinstance(data["events_with_finance"], int)
        assert isinstance(data["by_month"], dict)
        assert isinstance(data["by_truck"], dict)
        
        print(f"✓ Finance overview: revenue={data['total_revenue']}, costs={data['total_costs']}, profit={data['total_profit']}")
    
    def test_create_inquiry_for_finance_test(self, session):
        """Create a test inquiry for finance testing"""
        # First create a quick inquiry
        inquiry_data = {
            "name": f"TEST_Finance_{uuid.uuid4().hex[:6]}",
            "event_date": "2026-06-15",
            "location": "Zurich",
            "guest_count": 100,
            "concept": "Firmenanlass",
            "email": "test@example.com",
            "phone": "+41791234567"
        }
        resp = session.post(f"{BASE_URL}/api/quick-inquiry", json=inquiry_data)
        assert resp.status_code == 200, f"Create inquiry failed: {resp.text}"
        
        inquiry_id = resp.json()["id"]
        print(f"✓ Created test inquiry: {inquiry_id}")
        
        # Update status to confirmed so it shows in finance
        status_resp = session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}", json={
            "status": "confirmed",
            "internal_notes": "Test inquiry for finance"
        })
        assert status_resp.status_code == 200, f"Status update failed: {status_resp.text}"
        print(f"✓ Updated inquiry status to confirmed")
        
        return inquiry_id
    
    def test_update_finance_data(self, session):
        """PUT /api/admin/inquiries/{id}/finance updates financial data"""
        # Create inquiry first
        inquiry_id = self.test_create_inquiry_for_finance_test(session)
        
        # Update finance data
        finance_data = {
            "revenue": 5000,
            "personnel_cost": 800,
            "material_cost": 500,
            "travel_cost": 200,
            "other_cost": 100,
            "finance_notes": "Test finance entry"
        }
        resp = session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/finance", json=finance_data)
        assert resp.status_code == 200, f"Finance update failed: {resp.text}"
        
        # Verify data was saved
        get_resp = session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert get_resp.status_code == 200
        
        saved = get_resp.json()
        assert saved["revenue"] == 5000, f"Revenue not saved: {saved.get('revenue')}"
        assert saved["personnel_cost"] == 800, f"Personnel cost not saved"
        assert saved["material_cost"] == 500, f"Material cost not saved"
        assert saved["travel_cost"] == 200, f"Travel cost not saved"
        assert saved["other_cost"] == 100, f"Other cost not saved"
        
        print(f"✓ Finance data saved: revenue={saved['revenue']}, total_costs={800+500+200+100}")
        
        # Cleanup
        session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        return inquiry_id
    
    def test_finance_overview_reflects_updates(self, session):
        """Verify finance overview reflects updated data"""
        # Create and update inquiry with finance data
        inquiry_id = self.test_create_inquiry_for_finance_test(session)
        
        finance_data = {
            "revenue": 3000,
            "personnel_cost": 400,
            "material_cost": 300,
            "travel_cost": 100,
            "other_cost": 50
        }
        session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/finance", json=finance_data)
        
        # Check overview
        resp = session.get(f"{BASE_URL}/api/admin/finance/overview")
        assert resp.status_code == 200
        
        data = resp.json()
        assert data["events_with_finance"] >= 1, "Should have at least 1 event with finance"
        print(f"✓ Finance overview shows {data['events_with_finance']} events with finance data")
        
        # Cleanup
        session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")


class TestGeocodeAPI(TestAuth):
    """Geocoding endpoint tests"""
    
    def test_geocode_zurich(self, session):
        """GET /api/admin/geocode?address=Zurich returns coordinates"""
        resp = session.get(f"{BASE_URL}/api/admin/geocode", params={"address": "Zurich"})
        assert resp.status_code == 200, f"Geocode failed: {resp.text}"
        
        data = resp.json()
        assert data["found"] == True, "Zurich should be found"
        assert "lat" in data, "Missing lat"
        assert "lon" in data, "Missing lon"
        
        # Zurich is approximately at 47.37, 8.54
        assert 47.0 < data["lat"] < 48.0, f"Lat out of range: {data['lat']}"
        assert 8.0 < data["lon"] < 9.0, f"Lon out of range: {data['lon']}"
        
        print(f"✓ Geocoded Zurich: lat={data['lat']}, lon={data['lon']}")
    
    def test_geocode_wetzikon(self, session):
        """GET /api/admin/geocode?address=Wetzikon returns coordinates"""
        resp = session.get(f"{BASE_URL}/api/admin/geocode", params={"address": "Wetzikon"})
        assert resp.status_code == 200
        
        data = resp.json()
        assert data["found"] == True, "Wetzikon should be found"
        
        # Wetzikon is approximately at 47.32, 8.80
        assert 47.0 < data["lat"] < 48.0, f"Lat out of range: {data['lat']}"
        assert 8.5 < data["lon"] < 9.0, f"Lon out of range: {data['lon']}"
        
        print(f"✓ Geocoded Wetzikon: lat={data['lat']}, lon={data['lon']}")
    
    def test_geocode_basel(self, session):
        """GET /api/admin/geocode?address=Basel returns coordinates"""
        resp = session.get(f"{BASE_URL}/api/admin/geocode", params={"address": "Basel"})
        assert resp.status_code == 200
        
        data = resp.json()
        assert data["found"] == True, "Basel should be found"
        
        # Basel is approximately at 47.56, 7.59
        assert 47.0 < data["lat"] < 48.0, f"Lat out of range: {data['lat']}"
        assert 7.0 < data["lon"] < 8.0, f"Lon out of range: {data['lon']}"
        
        print(f"✓ Geocoded Basel: lat={data['lat']}, lon={data['lon']}")
    
    def test_geocode_invalid_address(self, session):
        """GET /api/admin/geocode with invalid address returns found=false"""
        resp = session.get(f"{BASE_URL}/api/admin/geocode", params={"address": "xyznonexistent12345"})
        assert resp.status_code == 200
        
        data = resp.json()
        assert data["found"] == False, "Invalid address should not be found"
        
        print(f"✓ Invalid address correctly returns found=false")


class TestRouteAPI(TestAuth):
    """Route calculation endpoint tests"""
    
    def test_route_wetzikon_to_zurich(self, session):
        """GET /api/admin/route calculates distance and duration"""
        # Wetzikon to Zurich
        params = {
            "from_lat": 47.3231,
            "from_lon": 8.7994,
            "to_lat": 47.3769,
            "to_lon": 8.5417
        }
        resp = session.get(f"{BASE_URL}/api/admin/route", params=params)
        assert resp.status_code == 200, f"Route calculation failed: {resp.text}"
        
        data = resp.json()
        assert data["found"] == True, "Route should be found"
        assert "distance_km" in data, "Missing distance_km"
        assert "duration_min" in data, "Missing duration_min"
        assert "geometry" in data, "Missing geometry"
        
        # Wetzikon to Zurich is about 25-35 km
        assert 15 < data["distance_km"] < 50, f"Distance out of range: {data['distance_km']}"
        assert data["duration_min"] > 0, "Duration should be positive"
        
        print(f"✓ Route Wetzikon→Zurich: {data['distance_km']}km, {data['duration_min']}min")
    
    def test_route_geometry_format(self, session):
        """Verify route geometry is in GeoJSON format"""
        params = {
            "from_lat": 47.3231,
            "from_lon": 8.7994,
            "to_lat": 47.5596,
            "to_lon": 7.5886  # Basel
        }
        resp = session.get(f"{BASE_URL}/api/admin/route", params=params)
        assert resp.status_code == 200
        
        data = resp.json()
        assert data["found"] == True
        
        geometry = data["geometry"]
        assert "type" in geometry, "Geometry should have type"
        assert "coordinates" in geometry, "Geometry should have coordinates"
        assert geometry["type"] == "LineString", f"Expected LineString, got {geometry['type']}"
        assert len(geometry["coordinates"]) > 0, "Should have coordinates"
        
        print(f"✓ Route geometry: {len(geometry['coordinates'])} points")


class TestRouteOptimizeAPI(TestAuth):
    """Route optimization endpoint tests"""
    
    def test_route_optimize_multiple_stops(self, session):
        """GET /api/admin/route/optimize calculates optimized route"""
        # Wetzikon (base) -> Zurich -> Basel (round trip)
        coords = "8.7994,47.3231;8.5417,47.3769;7.5886,47.5596"
        
        resp = session.get(f"{BASE_URL}/api/admin/route/optimize", params={"coords": coords})
        assert resp.status_code == 200, f"Route optimize failed: {resp.text}"
        
        data = resp.json()
        assert data["found"] == True, "Optimized route should be found"
        assert "distance_km" in data, "Missing distance_km"
        assert "duration_min" in data, "Missing duration_min"
        assert "geometry" in data, "Missing geometry"
        
        # Round trip should be significant distance
        assert data["distance_km"] > 100, f"Round trip should be >100km: {data['distance_km']}"
        
        print(f"✓ Optimized route: {data['distance_km']}km, {data['duration_min']}min")
    
    def test_route_optimize_no_coords(self, session):
        """GET /api/admin/route/optimize without coords returns error"""
        resp = session.get(f"{BASE_URL}/api/admin/route/optimize")
        assert resp.status_code == 200
        
        data = resp.json()
        assert data["found"] == False, "Should return found=false without coords"
        
        print(f"✓ Route optimize correctly handles missing coords")


class TestEventsMapAPI(TestAuth):
    """Events map endpoint tests"""
    
    def test_events_map_returns_base_location(self, session):
        """GET /api/admin/events-map returns events list with base location"""
        resp = session.get(f"{BASE_URL}/api/admin/events-map")
        assert resp.status_code == 200, f"Events map failed: {resp.text}"
        
        data = resp.json()
        assert "events" in data, "Missing events"
        assert "base" in data, "Missing base location"
        
        # Verify base is Wetzikon
        base = data["base"]
        assert "lat" in base, "Base missing lat"
        assert "lon" in base, "Base missing lon"
        assert abs(base["lat"] - 47.3231) < 0.01, f"Base lat should be Wetzikon: {base['lat']}"
        assert abs(base["lon"] - 8.7994) < 0.01, f"Base lon should be Wetzikon: {base['lon']}"
        
        print(f"✓ Events map: base={base}, {len(data['events'])} events")
    
    def test_events_map_event_structure(self, session):
        """Verify event structure in events-map response"""
        # Create a confirmed inquiry first
        inquiry_data = {
            "name": f"TEST_Map_{uuid.uuid4().hex[:6]}",
            "event_date": "2026-07-20",
            "location": "Bern",
            "guest_count": 150,
            "concept": "Festival"
        }
        create_resp = session.post(f"{BASE_URL}/api/quick-inquiry", json=inquiry_data)
        inquiry_id = create_resp.json()["id"]
        
        # Update to confirmed status
        session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}", json={
            "status": "confirmed",
            "internal_notes": ""
        })
        
        # Get events map
        resp = session.get(f"{BASE_URL}/api/admin/events-map")
        assert resp.status_code == 200
        
        data = resp.json()
        events = data["events"]
        
        # Find our test event
        test_event = next((e for e in events if e["id"] == inquiry_id), None)
        assert test_event is not None, "Test event should be in events list"
        
        # Verify structure
        assert "id" in test_event
        assert "name" in test_event
        assert "event_date" in test_event
        assert "location" in test_event
        assert "status" in test_event
        
        print(f"✓ Event structure verified: {test_event['name']}")
        
        # Cleanup
        session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")


class TestCoordsUpdateAPI(TestAuth):
    """Coordinates update endpoint tests"""
    
    def test_update_inquiry_coords(self, session):
        """PUT /api/admin/inquiries/{id}/coords updates coordinates"""
        # Create inquiry
        inquiry_data = {
            "name": f"TEST_Coords_{uuid.uuid4().hex[:6]}",
            "event_date": "2026-08-10",
            "location": "Luzern",
            "guest_count": 200,
            "concept": "Hochzeit"
        }
        create_resp = session.post(f"{BASE_URL}/api/quick-inquiry", json=inquiry_data)
        inquiry_id = create_resp.json()["id"]
        
        # Update coordinates
        coords = {"lat": 47.0502, "lon": 8.3093}  # Luzern
        resp = session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/coords", json=coords)
        assert resp.status_code == 200, f"Coords update failed: {resp.text}"
        
        # Verify saved
        get_resp = session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert get_resp.status_code == 200
        
        saved = get_resp.json()
        assert saved["lat"] == 47.0502, f"Lat not saved: {saved.get('lat')}"
        assert saved["lon"] == 8.3093, f"Lon not saved: {saved.get('lon')}"
        
        print(f"✓ Coordinates saved: lat={saved['lat']}, lon={saved['lon']}")
        
        # Cleanup
        session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")


class TestAdminSidebar(TestAuth):
    """Test admin sidebar has correct nav items"""
    
    def test_admin_inquiries_list(self, session):
        """Verify admin inquiries endpoint works (used by sidebar)"""
        resp = session.get(f"{BASE_URL}/api/admin/inquiries")
        assert resp.status_code == 200, f"Admin inquiries failed: {resp.text}"
        
        data = resp.json()
        assert isinstance(data, list), "Should return list"
        print(f"✓ Admin inquiries: {len(data)} inquiries")
    
    def test_admin_stats(self, session):
        """Verify admin stats endpoint works (used by dashboard)"""
        resp = session.get(f"{BASE_URL}/api/admin/stats")
        assert resp.status_code == 200, f"Admin stats failed: {resp.text}"
        
        data = resp.json()
        assert "total_inquiries" in data
        assert "new_inquiries" in data
        assert "confirmed" in data
        assert "total_trucks" in data
        
        print(f"✓ Admin stats: {data['total_inquiries']} total, {data['confirmed']} confirmed")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data():
    """Cleanup TEST_ prefixed data after all tests"""
    yield
    
    # Cleanup after tests
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    
    login_resp = s.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@truckonroad.ch",
        "password": "TruckOnRoad2026!"
    })
    
    if login_resp.status_code == 200:
        # Get all inquiries and delete TEST_ ones
        inquiries_resp = s.get(f"{BASE_URL}/api/admin/inquiries")
        if inquiries_resp.status_code == 200:
            for inq in inquiries_resp.json():
                name = inq.get("name", "")
                if name.startswith("TEST_"):
                    s.delete(f"{BASE_URL}/api/admin/inquiries/{inq['id']}")
                    print(f"Cleaned up: {name}")
