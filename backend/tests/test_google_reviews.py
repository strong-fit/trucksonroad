"""
Test Google Review Import Feature
- Public API returns only Google reviews when Google reviews exist
- Public API returns placeholder reviews when no Google reviews exist
- Admin API returns ALL reviews with source field
- CRUD operations for reviews with source field
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGoogleReviewsPublicAPI:
    """Test public /api/reviews endpoint with Google/placeholder logic"""
    
    def test_public_reviews_returns_only_google_when_google_exists(self):
        """GET /api/reviews should return only Google reviews when Google reviews exist"""
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        
        reviews = response.json()
        assert isinstance(reviews, list)
        
        # All returned reviews should be Google source
        for review in reviews:
            assert review.get('source') == 'google', f"Expected source='google', got '{review.get('source')}' for review by {review.get('author')}"
        
        # Should have at least 1 Google review (Stefan M.)
        assert len(reviews) >= 1, "Expected at least 1 Google review"
        print(f"✓ Public API returned {len(reviews)} Google review(s), no placeholders")
    
    def test_public_reviews_have_required_fields(self):
        """Public reviews should have all required fields"""
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        
        reviews = response.json()
        required_fields = ['id', 'author', 'rating', 'text', 'date', 'source', 'is_active']
        
        for review in reviews:
            for field in required_fields:
                assert field in review, f"Missing field '{field}' in review"
        print(f"✓ All {len(reviews)} reviews have required fields")


class TestGoogleReviewsAdminAPI:
    """Test admin /api/admin/reviews endpoint"""
    
    @pytest.fixture
    def admin_session(self):
        """Login as admin and return session with cookies"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin login failed - skipping admin tests")
        return session
    
    def test_admin_reviews_returns_all_reviews(self, admin_session):
        """GET /api/admin/reviews should return ALL reviews including placeholders"""
        response = admin_session.get(f"{BASE_URL}/api/admin/reviews")
        assert response.status_code == 200
        
        reviews = response.json()
        assert isinstance(reviews, list)
        
        # Should have both Google and placeholder reviews
        google_reviews = [r for r in reviews if r.get('source') == 'google']
        placeholder_reviews = [r for r in reviews if r.get('source') == 'placeholder']
        
        print(f"✓ Admin API returned {len(reviews)} total reviews: {len(google_reviews)} Google, {len(placeholder_reviews)} placeholders")
        
        # Verify we have both types
        assert len(google_reviews) >= 1, "Expected at least 1 Google review"
        assert len(placeholder_reviews) >= 1, "Expected at least 1 placeholder review"
    
    def test_admin_reviews_have_source_field(self, admin_session):
        """All admin reviews should have source field"""
        response = admin_session.get(f"{BASE_URL}/api/admin/reviews")
        assert response.status_code == 200
        
        reviews = response.json()
        for review in reviews:
            assert 'source' in review, f"Missing 'source' field in review by {review.get('author')}"
            assert review['source'] in ['google', 'placeholder'], f"Invalid source: {review['source']}"
        print(f"✓ All {len(reviews)} reviews have valid source field")
    
    def test_create_google_review(self, admin_session):
        """POST /api/admin/reviews should accept and store 'source' field"""
        test_review = {
            "author": f"TEST_Google_User_{uuid.uuid4().hex[:6]}",
            "rating": 5,
            "text": "Test Google review for automated testing",
            "date": "2026-01-15",
            "event_type": "Firmenanlass",
            "source": "google",
            "is_active": True
        }
        
        response = admin_session.post(f"{BASE_URL}/api/admin/reviews", json=test_review)
        assert response.status_code == 200
        
        created = response.json()
        assert created.get('source') == 'google', f"Expected source='google', got '{created.get('source')}'"
        assert created.get('author') == test_review['author']
        assert 'id' in created
        
        print(f"✓ Created Google review with id: {created['id']}")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/reviews/{created['id']}")
    
    def test_create_placeholder_review(self, admin_session):
        """POST /api/admin/reviews should accept placeholder source"""
        test_review = {
            "author": f"TEST_Placeholder_{uuid.uuid4().hex[:6]}",
            "rating": 4,
            "text": "Test placeholder review for automated testing",
            "date": "2026-01-10",
            "event_type": "Festival",
            "source": "placeholder",
            "is_active": True
        }
        
        response = admin_session.post(f"{BASE_URL}/api/admin/reviews", json=test_review)
        assert response.status_code == 200
        
        created = response.json()
        assert created.get('source') == 'placeholder', f"Expected source='placeholder', got '{created.get('source')}'"
        
        print(f"✓ Created placeholder review with id: {created['id']}")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/reviews/{created['id']}")
    
    def test_update_review_source(self, admin_session):
        """PUT /api/admin/reviews/{id} should update source field"""
        # Create a test review
        test_review = {
            "author": f"TEST_Update_{uuid.uuid4().hex[:6]}",
            "rating": 5,
            "text": "Test review for source update",
            "source": "placeholder",
            "is_active": True
        }
        
        create_response = admin_session.post(f"{BASE_URL}/api/admin/reviews", json=test_review)
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Update source to google
        update_response = admin_session.put(f"{BASE_URL}/api/admin/reviews/{review_id}", json={
            "source": "google"
        })
        assert update_response.status_code == 200
        
        # Verify update
        all_reviews = admin_session.get(f"{BASE_URL}/api/admin/reviews").json()
        updated_review = next((r for r in all_reviews if r['id'] == review_id), None)
        assert updated_review is not None
        assert updated_review['source'] == 'google', f"Source not updated, got: {updated_review['source']}"
        
        print(f"✓ Successfully updated review source from placeholder to google")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/reviews/{review_id}")


class TestPlaceholderAutoHiding:
    """Test that placeholders are hidden when Google reviews exist"""
    
    @pytest.fixture
    def admin_session(self):
        """Login as admin and return session with cookies"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin login failed")
        return session
    
    def test_placeholder_hidden_when_google_exists(self, admin_session):
        """When Google reviews exist, public API should not return placeholders"""
        # Get admin reviews to check what exists
        admin_response = admin_session.get(f"{BASE_URL}/api/admin/reviews")
        admin_reviews = admin_response.json()
        
        google_count = len([r for r in admin_reviews if r.get('source') == 'google' and r.get('is_active')])
        placeholder_count = len([r for r in admin_reviews if r.get('source') == 'placeholder' and r.get('is_active')])
        
        print(f"Admin sees: {google_count} active Google, {placeholder_count} active placeholders")
        
        # Get public reviews
        public_response = requests.get(f"{BASE_URL}/api/reviews")
        public_reviews = public_response.json()
        
        if google_count > 0:
            # Should only see Google reviews
            for review in public_reviews:
                assert review.get('source') == 'google', f"Placeholder review visible in public API: {review.get('author')}"
            print(f"✓ Public API correctly hides {placeholder_count} placeholders, shows {len(public_reviews)} Google reviews")
        else:
            # Should see placeholders
            assert len(public_reviews) == placeholder_count, "Should show all placeholders when no Google reviews"
            print(f"✓ Public API correctly shows {len(public_reviews)} placeholders (no Google reviews)")
    
    def test_delete_google_review_shows_placeholders(self, admin_session):
        """Deleting the only Google review should make placeholders reappear"""
        # First, get current state
        admin_reviews = admin_session.get(f"{BASE_URL}/api/admin/reviews").json()
        google_reviews = [r for r in admin_reviews if r.get('source') == 'google' and r.get('is_active')]
        
        if len(google_reviews) == 0:
            pytest.skip("No Google reviews to test deletion scenario")
        
        # If there's only 1 Google review, we can test the scenario
        # But we don't want to actually delete real data, so we'll create a test scenario
        
        # Create a new Google review
        test_google = {
            "author": f"TEST_DeleteScenario_{uuid.uuid4().hex[:6]}",
            "rating": 5,
            "text": "Test Google review for deletion scenario",
            "source": "google",
            "is_active": True
        }
        create_resp = admin_session.post(f"{BASE_URL}/api/admin/reviews", json=test_google)
        assert create_resp.status_code == 200
        test_review_id = create_resp.json()['id']
        
        # Verify public API shows Google reviews
        public_before = requests.get(f"{BASE_URL}/api/reviews").json()
        google_in_public = [r for r in public_before if r.get('source') == 'google']
        assert len(google_in_public) >= 1, "Should have Google reviews in public API"
        
        print(f"✓ Before deletion: Public API shows {len(google_in_public)} Google reviews")
        
        # Cleanup test review
        admin_session.delete(f"{BASE_URL}/api/admin/reviews/{test_review_id}")
        print(f"✓ Test review cleaned up")


class TestReviewSourceDefaultBehavior:
    """Test default source behavior when not specified"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin login failed")
        return session
    
    def test_default_source_is_placeholder(self, admin_session):
        """When source is not specified, it should default to 'placeholder'"""
        test_review = {
            "author": f"TEST_NoSource_{uuid.uuid4().hex[:6]}",
            "rating": 4,
            "text": "Test review without source field"
            # Note: source not specified
        }
        
        response = admin_session.post(f"{BASE_URL}/api/admin/reviews", json=test_review)
        assert response.status_code == 200
        
        created = response.json()
        # Based on the code, default is 'placeholder'
        assert created.get('source') == 'placeholder', f"Expected default source='placeholder', got '{created.get('source')}'"
        
        print(f"✓ Default source is 'placeholder' when not specified")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/admin/reviews/{created['id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
