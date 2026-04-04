"""
Next.js Migration Regression Tests
Tests all routes and SSR functionality after CRA to Next.js App Router migration
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://hellpetrol-staging.preview.emergentagent.com').rstrip('/')


class TestPublicRoutes:
    """Test all public routes return 200"""
    
    @pytest.mark.parametrize("route", [
        "/",
        "/trucks/burger-truck",
        "/anfrage",
        "/faq",
        "/kontakt",
        "/ueber-uns",
        "/blog",
        "/agenda",
        "/private-events",
        "/fuer-veranstalter",
        "/veranstalter",
    ])
    def test_public_route_returns_200(self, route):
        response = requests.get(f"{BASE_URL}{route}", timeout=30)
        assert response.status_code == 200, f"Route {route} returned {response.status_code}"


class TestAdminRoutes:
    """Test all admin routes return 200"""
    
    @pytest.mark.parametrize("route", [
        "/admin/login",
        "/admin/dashboard",
        "/admin/anfragen",
        "/admin/trucks",
        "/admin/faqs",
        "/admin/mitarbeiter",
        "/admin/finanzen",
        "/admin/routen",
        "/admin/kalender",
        "/admin/reviews",
        "/admin/einstellungen",
        "/admin/export",
        "/admin/event-scout",
        "/admin/blog",
    ])
    def test_admin_route_returns_200(self, route):
        response = requests.get(f"{BASE_URL}{route}", timeout=30)
        assert response.status_code == 200, f"Route {route} returned {response.status_code}"


class TestCustomerPortalRoutes:
    """Test all customer portal routes return 200"""
    
    @pytest.mark.parametrize("route", [
        "/konto/login",
        "/konto/dashboard",
        "/konto/anfragen",
        "/konto/passwort-vergessen",
        "/konto/passwort-reset",
    ])
    def test_customer_route_returns_200(self, route):
        response = requests.get(f"{BASE_URL}{route}", timeout=30)
        assert response.status_code == 200, f"Route {route} returned {response.status_code}"


class TestBackendAPI:
    """Test backend API endpoints"""
    
    def test_trucks_api_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/trucks", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Trucks API should return a list"
    
    def test_faqs_api_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/faqs", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "FAQs API should return a list"
    
    def test_reviews_api_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/reviews", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Reviews API should return a list"
    
    def test_blog_api_returns_200(self):
        response = requests.get(f"{BASE_URL}/api/blog", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data, "Blog API should return posts"


class TestAdminAuth:
    """Test admin authentication flow"""
    
    def test_admin_login_success(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "TrucksOnRoad2026!"},
            timeout=30
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["email"] == "admin@truckonroad.ch"
        assert data["role"] == "admin"
    
    def test_admin_login_invalid_credentials(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "wrongpassword"},
            timeout=30
        )
        assert response.status_code == 401, "Invalid credentials should return 401"


class TestSSRContent:
    """Test Server-Side Rendering content"""
    
    def test_homepage_has_meta_description(self):
        response = requests.get(f"{BASE_URL}/", timeout=30)
        assert response.status_code == 200
        html = response.text
        assert 'name="description"' in html, "Meta description should be present"
        assert 'Foodtrucks' in html or 'Trucks' in html, "German content should be present"
    
    def test_homepage_has_og_tags(self):
        response = requests.get(f"{BASE_URL}/", timeout=30)
        html = response.text
        assert 'property="og:title"' in html, "OG title should be present"
        assert 'property="og:description"' in html, "OG description should be present"
    
    def test_homepage_has_twitter_card(self):
        response = requests.get(f"{BASE_URL}/", timeout=30)
        html = response.text
        assert 'name="twitter:card"' in html, "Twitter card should be present"
    
    def test_homepage_has_json_ld(self):
        response = requests.get(f"{BASE_URL}/", timeout=30)
        html = response.text
        assert 'application/ld+json' in html, "JSON-LD should be present"
        assert 'FoodEstablishment' in html, "FoodEstablishment schema should be present"
    
    def test_homepage_has_title(self):
        response = requests.get(f"{BASE_URL}/", timeout=30)
        html = response.text
        assert '<title>' in html, "Title tag should be present"
        assert 'TRUCKSonROAD' in html, "Brand name should be in title"
    
    def test_homepage_has_navbar(self):
        response = requests.get(f"{BASE_URL}/", timeout=30)
        html = response.text
        assert 'data-testid="main-navbar"' in html, "Navbar should be present in SSR HTML"
    
    def test_homepage_has_hero_section(self):
        response = requests.get(f"{BASE_URL}/", timeout=30)
        html = response.text
        assert 'data-testid="hero-section"' in html, "Hero section should be present in SSR HTML"


class TestTruckDetailPage:
    """Test truck detail page"""
    
    def test_burger_truck_page_loads(self):
        response = requests.get(f"{BASE_URL}/trucks/burger-truck", timeout=30)
        assert response.status_code == 200
        html = response.text
        # Should have some content
        assert len(html) > 1000, "Page should have substantial content"
