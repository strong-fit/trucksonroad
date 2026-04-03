"""
Test SEO endpoints and domain rename from truckonroad.ch to trucksonroad.ch
Tests: sitemap.xml, robots.txt, seo/structured-data, seo/events-schema, contact-info
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSitemapXML:
    """Sitemap.xml should contain trucksonroad.ch domain"""
    
    def test_sitemap_returns_xml(self):
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/xml" in response.headers.get("Content-Type", "")
        print("✓ Sitemap returns XML content type")
    
    def test_sitemap_contains_correct_domain(self):
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        # Should contain trucksonroad.ch
        assert "trucksonroad.ch" in content, "Sitemap should contain trucksonroad.ch domain"
        print("✓ Sitemap contains trucksonroad.ch")
        
        # Should NOT contain old domain truckonroad.ch
        assert "truckonroad.ch" not in content, "Sitemap should NOT contain old domain truckonroad.ch"
        print("✓ Sitemap does NOT contain old domain truckonroad.ch")
    
    def test_sitemap_has_required_urls(self):
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        content = response.text
        
        required_paths = ["/", "/fuer-veranstalter", "/private-events", "/kontakt", "/anfrage", "/faq"]
        for path in required_paths:
            assert f"https://trucksonroad.ch{path}" in content or f"https://trucksonroad.ch{path}<" in content, \
                f"Sitemap should contain {path}"
        print(f"✓ Sitemap contains all required paths: {required_paths}")


class TestRobotsTxt:
    """Robots.txt should reference trucksonroad.ch"""
    
    def test_robots_returns_text(self):
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/plain" in response.headers.get("Content-Type", "")
        print("✓ Robots.txt returns text/plain content type")
    
    def test_robots_sitemap_url_correct_domain(self):
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        content = response.text
        
        # Should contain sitemap with trucksonroad.ch
        assert "Sitemap: https://trucksonroad.ch" in content, \
            "Robots.txt should reference trucksonroad.ch in Sitemap URL"
        print("✓ Robots.txt Sitemap URL uses trucksonroad.ch")
        
        # Should NOT contain old domain
        assert "truckonroad.ch" not in content, \
            "Robots.txt should NOT contain old domain truckonroad.ch"
        print("✓ Robots.txt does NOT contain old domain truckonroad.ch")
    
    def test_robots_allows_ai_bots(self):
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        content = response.text
        
        ai_bots = ["GPTBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot", "Google-Extended"]
        for bot in ai_bots:
            assert bot in content, f"Robots.txt should mention {bot}"
        print(f"✓ Robots.txt allows AI bots: {ai_bots}")


class TestStructuredData:
    """GET /api/seo/structured-data should return url with trucksonroad.ch"""
    
    def test_structured_data_returns_json(self):
        response = requests.get(f"{BASE_URL}/api/seo/structured-data")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "@context" in data
        assert "@type" in data
        print("✓ Structured data returns valid JSON-LD")
    
    def test_structured_data_url_correct_domain(self):
        response = requests.get(f"{BASE_URL}/api/seo/structured-data")
        data = response.json()
        
        # Check url field
        assert data.get("url") == "https://trucksonroad.ch", \
            f"Expected url to be https://trucksonroad.ch, got {data.get('url')}"
        print("✓ Structured data url field is https://trucksonroad.ch")
        
        # Check email field
        email = data.get("email", "")
        assert "trucksonroad.ch" in email or email == "info@trucksonroad.ch", \
            f"Email should be info@trucksonroad.ch, got {email}"
        print(f"✓ Structured data email is {email}")
    
    def test_structured_data_no_old_domain(self):
        response = requests.get(f"{BASE_URL}/api/seo/structured-data")
        content = response.text
        
        assert "truckonroad.ch" not in content, \
            "Structured data should NOT contain old domain truckonroad.ch"
        print("✓ Structured data does NOT contain old domain truckonroad.ch")
    
    def test_structured_data_type_food_establishment(self):
        response = requests.get(f"{BASE_URL}/api/seo/structured-data")
        data = response.json()
        
        assert data.get("@type") == "FoodEstablishment", \
            f"Expected @type FoodEstablishment, got {data.get('@type')}"
        assert data.get("name") == "TrucksOnRoad", \
            f"Expected name TrucksOnRoad, got {data.get('name')}"
        print("✓ Structured data has correct @type and name")


class TestEventsSchema:
    """GET /api/seo/events-schema should return valid FoodEvent JSON-LD array"""
    
    def test_events_schema_returns_array(self):
        response = requests.get(f"{BASE_URL}/api/seo/events-schema")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Events schema returns array with {len(data)} events")
    
    def test_events_schema_structure(self):
        response = requests.get(f"{BASE_URL}/api/seo/events-schema")
        data = response.json()
        
        if len(data) > 0:
            event = data[0]
            assert event.get("@context") == "https://schema.org", "Event should have @context"
            assert event.get("@type") == "FoodEvent", f"Expected @type FoodEvent, got {event.get('@type')}"
            assert "name" in event, "Event should have name"
            assert "startDate" in event, "Event should have startDate"
            assert "location" in event, "Event should have location"
            assert "organizer" in event, "Event should have organizer"
            print("✓ Events schema has correct FoodEvent structure")
        else:
            print("✓ Events schema returns empty array (no upcoming confirmed events)")
    
    def test_events_schema_organizer_url(self):
        response = requests.get(f"{BASE_URL}/api/seo/events-schema")
        data = response.json()
        
        if len(data) > 0:
            event = data[0]
            organizer = event.get("organizer", {})
            assert organizer.get("url") == "https://trucksonroad.ch", \
                f"Organizer URL should be https://trucksonroad.ch, got {organizer.get('url')}"
            print("✓ Events schema organizer URL is trucksonroad.ch")
        else:
            print("✓ No events to check organizer URL (empty array)")
    
    def test_events_schema_no_old_domain(self):
        response = requests.get(f"{BASE_URL}/api/seo/events-schema")
        content = response.text
        
        assert "truckonroad.ch" not in content, \
            "Events schema should NOT contain old domain truckonroad.ch"
        print("✓ Events schema does NOT contain old domain truckonroad.ch")


class TestContactInfo:
    """GET /api/contact-info should return email with trucksonroad.ch"""
    
    def test_contact_info_returns_json(self):
        response = requests.get(f"{BASE_URL}/api/contact-info")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "email" in data
        assert "phone" in data
        print("✓ Contact info returns valid JSON")
    
    def test_contact_info_email_correct_domain(self):
        response = requests.get(f"{BASE_URL}/api/contact-info")
        data = response.json()
        
        email = data.get("email", "")
        assert email == "info@trucksonroad.ch", \
            f"Expected email info@trucksonroad.ch, got {email}"
        print(f"✓ Contact info email is {email}")
    
    def test_contact_info_no_old_domain(self):
        response = requests.get(f"{BASE_URL}/api/contact-info")
        content = response.text
        
        assert "truckonroad.ch" not in content, \
            "Contact info should NOT contain old domain truckonroad.ch"
        print("✓ Contact info does NOT contain old domain truckonroad.ch")


class TestHomepageSmoke:
    """Basic smoke test for homepage"""
    
    def test_homepage_loads(self):
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200, f"Homepage should return 200, got {response.status_code}"
        print("✓ Homepage loads successfully")
    
    def test_trucks_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/trucks")
        assert response.status_code == 200, f"Trucks endpoint should return 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Trucks should return a list"
        print(f"✓ Trucks endpoint returns {len(data)} trucks")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
