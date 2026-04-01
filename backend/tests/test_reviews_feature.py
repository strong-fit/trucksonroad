"""
Test suite for Reviews/Bewertungen feature (Batch 8)
Tests:
- GET /api/reviews (public active reviews)
- GET /api/admin/reviews (all reviews including inactive, requires auth)
- POST /api/admin/reviews (create review, requires auth)
- PUT /api/admin/reviews/{id} (update review, requires auth)
- DELETE /api/admin/reviews/{id} (delete review, requires auth)
- GET /api/seo/structured-data (includes aggregateRating)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@truckonroad.ch"
ADMIN_PASSWORD = "TruckOnRoad2026!"


class TestPublicReviewsAPI:
    """Test public reviews endpoint (no auth required)"""
    
    def test_get_public_reviews_returns_200(self):
        """GET /api/reviews should return 200 and list of active reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ GET /api/reviews returned {len(data)} active reviews")
        
        # Verify all returned reviews are active
        for review in data:
            assert review.get('is_active', True) == True, "Public endpoint should only return active reviews"
            assert 'author' in review, "Review should have author field"
            assert 'rating' in review, "Review should have rating field"
            assert 'text' in review, "Review should have text field"
        
        return data


class TestSEOStructuredData:
    """Test SEO structured data endpoint with aggregateRating"""
    
    def test_structured_data_returns_200(self):
        """GET /api/seo/structured-data should return 200"""
        response = requests.get(f"{BASE_URL}/api/seo/structured-data")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get('@context') == 'https://schema.org', "Should have schema.org context"
        assert data.get('@type') == 'FoodEstablishment', "Should be FoodEstablishment type"
        print("✓ GET /api/seo/structured-data returned valid JSON-LD")
        return data
    
    def test_structured_data_has_aggregate_rating(self):
        """Structured data should include aggregateRating if reviews exist"""
        response = requests.get(f"{BASE_URL}/api/seo/structured-data")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check if reviews exist first
        reviews_response = requests.get(f"{BASE_URL}/api/reviews")
        reviews = reviews_response.json()
        
        if len(reviews) > 0:
            assert 'aggregateRating' in data, "Should have aggregateRating when reviews exist"
            agg = data['aggregateRating']
            assert agg.get('@type') == 'AggregateRating', "aggregateRating should have correct type"
            assert 'ratingValue' in agg, "aggregateRating should have ratingValue"
            assert 'reviewCount' in agg, "aggregateRating should have reviewCount"
            assert agg.get('bestRating') == 5, "bestRating should be 5"
            assert agg.get('worstRating') == 1, "worstRating should be 1"
            
            # Verify rating is within valid range
            rating_value = agg['ratingValue']
            assert 1 <= rating_value <= 5, f"ratingValue {rating_value} should be between 1 and 5"
            
            print(f"✓ aggregateRating present: {rating_value}/5 from {agg['reviewCount']} reviews")
        else:
            print("⚠ No reviews exist, aggregateRating may not be present")


class TestAdminReviewsCRUD:
    """Test admin reviews CRUD operations (requires auth)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with authentication"""
        self.session = requests.Session()
        # Login to get auth cookies
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip(f"Authentication failed: {login_response.status_code}")
        print(f"✓ Authenticated as {ADMIN_EMAIL}")
    
    def test_admin_get_all_reviews(self):
        """GET /api/admin/reviews should return all reviews including inactive"""
        response = self.session.get(f"{BASE_URL}/api/admin/reviews")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ GET /api/admin/reviews returned {len(data)} total reviews")
        return data
    
    def test_admin_create_review(self):
        """POST /api/admin/reviews should create a new review"""
        new_review = {
            "author": "TEST_Pytest Company",
            "rating": 5,
            "text": "Excellent service from TruckOnRoad! The food was amazing.",
            "date": "2026-01-15",
            "event_type": "Firmenanlass",
            "is_active": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/admin/reviews", json=new_review)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'id' in data, "Response should contain review id"
        assert data['author'] == new_review['author'], "Author should match"
        assert data['rating'] == new_review['rating'], "Rating should match"
        assert data['text'] == new_review['text'], "Text should match"
        
        print(f"✓ Created review with id: {data['id']}")
        return data
    
    def test_admin_update_review(self):
        """PUT /api/admin/reviews/{id} should update a review"""
        # First create a review to update
        create_response = self.session.post(f"{BASE_URL}/api/admin/reviews", json={
            "author": "TEST_Update Company",
            "rating": 4,
            "text": "Good service",
            "date": "2026-01-15",
            "event_type": "Festival",
            "is_active": True
        })
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Update the review
        update_data = {
            "rating": 5,
            "text": "Updated: Excellent service!",
            "is_active": False
        }
        
        update_response = self.session.put(f"{BASE_URL}/api/admin/reviews/{review_id}", json=update_data)
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}"
        
        # Verify update by fetching all reviews
        get_response = self.session.get(f"{BASE_URL}/api/admin/reviews")
        reviews = get_response.json()
        updated_review = next((r for r in reviews if r['id'] == review_id), None)
        
        assert updated_review is not None, "Updated review should exist"
        assert updated_review['rating'] == 5, "Rating should be updated to 5"
        assert updated_review['is_active'] == False, "is_active should be updated to False"
        
        print(f"✓ Updated review {review_id}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/reviews/{review_id}")
        return review_id
    
    def test_admin_delete_review(self):
        """DELETE /api/admin/reviews/{id} should delete a review"""
        # First create a review to delete
        create_response = self.session.post(f"{BASE_URL}/api/admin/reviews", json={
            "author": "TEST_Delete Company",
            "rating": 3,
            "text": "To be deleted",
            "date": "2026-01-15",
            "event_type": "Privatanlass",
            "is_active": True
        })
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Delete the review
        delete_response = self.session.delete(f"{BASE_URL}/api/admin/reviews/{review_id}")
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        
        # Verify deletion
        get_response = self.session.get(f"{BASE_URL}/api/admin/reviews")
        reviews = get_response.json()
        deleted_review = next((r for r in reviews if r['id'] == review_id), None)
        
        assert deleted_review is None, "Deleted review should not exist"
        print(f"✓ Deleted review {review_id}")
    
    def test_toggle_review_active_status(self):
        """Toggle is_active via PUT should update visibility"""
        # Create an active review
        create_response = self.session.post(f"{BASE_URL}/api/admin/reviews", json={
            "author": "TEST_Toggle Company",
            "rating": 5,
            "text": "Toggle test review",
            "date": "2026-01-15",
            "event_type": "Hochzeit",
            "is_active": True
        })
        assert create_response.status_code == 200
        review_id = create_response.json()['id']
        
        # Verify it appears in public reviews
        public_response = requests.get(f"{BASE_URL}/api/reviews")
        public_reviews = public_response.json()
        found_in_public = any(r['id'] == review_id for r in public_reviews)
        assert found_in_public, "Active review should appear in public endpoint"
        
        # Toggle to inactive
        toggle_response = self.session.put(f"{BASE_URL}/api/admin/reviews/{review_id}", json={"is_active": False})
        assert toggle_response.status_code == 200
        
        # Verify it no longer appears in public reviews
        public_response2 = requests.get(f"{BASE_URL}/api/reviews")
        public_reviews2 = public_response2.json()
        found_in_public2 = any(r['id'] == review_id for r in public_reviews2)
        assert not found_in_public2, "Inactive review should NOT appear in public endpoint"
        
        print(f"✓ Toggle active/inactive works correctly for review {review_id}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/reviews/{review_id}")
    
    def test_rating_validation(self):
        """Rating should be clamped between 1 and 5"""
        # Test rating > 5
        response1 = self.session.post(f"{BASE_URL}/api/admin/reviews", json={
            "author": "TEST_Rating High",
            "rating": 10,
            "text": "Rating too high",
            "is_active": True
        })
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1['rating'] == 5, "Rating > 5 should be clamped to 5"
        self.session.delete(f"{BASE_URL}/api/admin/reviews/{data1['id']}")
        
        # Test rating < 1
        response2 = self.session.post(f"{BASE_URL}/api/admin/reviews", json={
            "author": "TEST_Rating Low",
            "rating": 0,
            "text": "Rating too low",
            "is_active": True
        })
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2['rating'] == 1, "Rating < 1 should be clamped to 1"
        self.session.delete(f"{BASE_URL}/api/admin/reviews/{data2['id']}")
        
        print("✓ Rating validation (clamping 1-5) works correctly")


class TestAdminReviewsAuth:
    """Test that admin endpoints require authentication"""
    
    def test_admin_reviews_requires_auth(self):
        """GET /api/admin/reviews should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/reviews")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/admin/reviews requires authentication")
    
    def test_create_review_requires_auth(self):
        """POST /api/admin/reviews should return 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/admin/reviews", json={
            "author": "Unauthorized",
            "rating": 5,
            "text": "Should fail"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/admin/reviews requires authentication")
    
    def test_update_review_requires_auth(self):
        """PUT /api/admin/reviews/{id} should return 401 without auth"""
        response = requests.put(f"{BASE_URL}/api/admin/reviews/fake-id", json={"rating": 1})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ PUT /api/admin/reviews requires authentication")
    
    def test_delete_review_requires_auth(self):
        """DELETE /api/admin/reviews/{id} should return 401 without auth"""
        response = requests.delete(f"{BASE_URL}/api/admin/reviews/fake-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ DELETE /api/admin/reviews requires authentication")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_reviews(self):
        """Remove all TEST_ prefixed reviews"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code != 200:
            pytest.skip("Authentication failed for cleanup")
        
        # Get all reviews
        response = session.get(f"{BASE_URL}/api/admin/reviews")
        reviews = response.json()
        
        # Delete TEST_ prefixed reviews
        deleted_count = 0
        for review in reviews:
            if review.get('author', '').startswith('TEST_'):
                session.delete(f"{BASE_URL}/api/admin/reviews/{review['id']}")
                deleted_count += 1
        
        print(f"✓ Cleaned up {deleted_count} test reviews")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
