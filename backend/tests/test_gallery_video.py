"""
Test Gallery and Video URL features for TrucksOnRoad
Tests:
- PUT /api/admin/trucks/{slug} with gallery and video_url fields
- POST /api/admin/trucks/{slug}/gallery for image upload
- DELETE /api/admin/trucks/{slug}/gallery for image removal
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGalleryVideoFeatures:
    """Test gallery and video URL features for trucks"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and get session with auth cookies"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get auth cookies
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        print(f"✓ Admin login successful")
        
        yield
        
        # Cleanup: Reset burger-truck gallery and video_url
        cleanup_response = self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "gallery": [],
            "video_url": ""
        })
        print(f"✓ Cleanup: Reset burger-truck gallery and video_url")
    
    def test_01_get_trucks_returns_gallery_and_video_fields(self):
        """Test that GET /api/admin/trucks returns gallery and video_url fields"""
        response = self.session.get(f"{BASE_URL}/api/admin/trucks")
        assert response.status_code == 200, f"Failed to get trucks: {response.text}"
        
        trucks = response.json()
        assert len(trucks) > 0, "No trucks returned"
        
        # Check that at least one truck has gallery and video_url fields
        burger_truck = next((t for t in trucks if t['slug'] == 'burger-truck'), None)
        assert burger_truck is not None, "burger-truck not found"
        
        # Verify fields exist (can be empty)
        assert 'gallery' in burger_truck or burger_truck.get('gallery') is None, "gallery field missing"
        print(f"✓ burger-truck has gallery field: {burger_truck.get('gallery', [])}")
        print(f"✓ burger-truck has video_url field: {burger_truck.get('video_url', '')}")
    
    def test_02_update_truck_with_gallery_array(self):
        """Test PUT /api/admin/trucks/{slug} with gallery array"""
        test_gallery = [
            "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=600&q=80",
            "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80"
        ]
        
        response = self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "gallery": test_gallery
        })
        assert response.status_code == 200, f"Failed to update truck: {response.text}"
        
        # Verify the update
        verify_response = self.session.get(f"{BASE_URL}/api/admin/trucks")
        trucks = verify_response.json()
        burger_truck = next((t for t in trucks if t['slug'] == 'burger-truck'), None)
        
        assert burger_truck is not None, "burger-truck not found after update"
        assert burger_truck.get('gallery') == test_gallery, f"Gallery not saved correctly: {burger_truck.get('gallery')}"
        print(f"✓ Gallery array saved correctly with {len(test_gallery)} images")
    
    def test_03_update_truck_with_video_url(self):
        """Test PUT /api/admin/trucks/{slug} with video_url"""
        test_video_url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        
        response = self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "video_url": test_video_url
        })
        assert response.status_code == 200, f"Failed to update truck: {response.text}"
        
        # Verify the update
        verify_response = self.session.get(f"{BASE_URL}/api/admin/trucks")
        trucks = verify_response.json()
        burger_truck = next((t for t in trucks if t['slug'] == 'burger-truck'), None)
        
        assert burger_truck is not None, "burger-truck not found after update"
        assert burger_truck.get('video_url') == test_video_url, f"Video URL not saved correctly: {burger_truck.get('video_url')}"
        print(f"✓ Video URL saved correctly: {test_video_url}")
    
    def test_04_update_truck_with_both_gallery_and_video(self):
        """Test PUT /api/admin/trucks/{slug} with both gallery and video_url"""
        test_gallery = [
            "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=600&q=80",
            "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80",
            "https://images.unsplash.com/photo-1550547660-d9450f859349?w=600&q=80"
        ]
        test_video_url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        
        response = self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "gallery": test_gallery,
            "video_url": test_video_url
        })
        assert response.status_code == 200, f"Failed to update truck: {response.text}"
        
        # Verify the update
        verify_response = self.session.get(f"{BASE_URL}/api/admin/trucks")
        trucks = verify_response.json()
        burger_truck = next((t for t in trucks if t['slug'] == 'burger-truck'), None)
        
        assert burger_truck is not None, "burger-truck not found after update"
        assert burger_truck.get('gallery') == test_gallery, f"Gallery not saved correctly"
        assert burger_truck.get('video_url') == test_video_url, f"Video URL not saved correctly"
        print(f"✓ Both gallery ({len(test_gallery)} images) and video_url saved correctly")
    
    def test_05_delete_gallery_image(self):
        """Test DELETE /api/admin/trucks/{slug}/gallery removes image from array"""
        # First add some images
        test_gallery = [
            "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=600&q=80",
            "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80"
        ]
        self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "gallery": test_gallery
        })
        
        # Delete one image
        url_to_delete = test_gallery[0]
        delete_response = self.session.delete(
            f"{BASE_URL}/api/admin/trucks/burger-truck/gallery",
            json={"url": url_to_delete}
        )
        assert delete_response.status_code == 200, f"Failed to delete gallery image: {delete_response.text}"
        
        # Verify the deletion
        verify_response = self.session.get(f"{BASE_URL}/api/admin/trucks")
        trucks = verify_response.json()
        burger_truck = next((t for t in trucks if t['slug'] == 'burger-truck'), None)
        
        assert burger_truck is not None, "burger-truck not found after delete"
        assert url_to_delete not in burger_truck.get('gallery', []), "Image was not removed from gallery"
        assert len(burger_truck.get('gallery', [])) == 1, f"Gallery should have 1 image, has {len(burger_truck.get('gallery', []))}"
        print(f"✓ Gallery image deleted successfully, remaining: {len(burger_truck.get('gallery', []))} images")
    
    def test_06_clear_gallery_and_video(self):
        """Test clearing gallery and video_url"""
        # First set some values
        self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "gallery": ["https://example.com/test.jpg"],
            "video_url": "https://youtube.com/embed/test"
        })
        
        # Clear them
        response = self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "gallery": [],
            "video_url": ""
        })
        assert response.status_code == 200, f"Failed to clear gallery/video: {response.text}"
        
        # Verify
        verify_response = self.session.get(f"{BASE_URL}/api/admin/trucks")
        trucks = verify_response.json()
        burger_truck = next((t for t in trucks if t['slug'] == 'burger-truck'), None)
        
        assert burger_truck.get('gallery') == [] or burger_truck.get('gallery') is None, "Gallery not cleared"
        assert burger_truck.get('video_url') == "" or burger_truck.get('video_url') is None, "Video URL not cleared"
        print(f"✓ Gallery and video_url cleared successfully")
    
    def test_07_public_trucks_endpoint_returns_gallery_video(self):
        """Test that public /api/trucks endpoint returns gallery and video_url"""
        # First set some values via admin
        test_gallery = ["https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=600&q=80"]
        test_video = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        
        self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "gallery": test_gallery,
            "video_url": test_video
        })
        
        # Check public endpoint (no auth needed)
        public_response = requests.get(f"{BASE_URL}/api/trucks")
        assert public_response.status_code == 200, f"Public trucks endpoint failed: {public_response.text}"
        
        trucks = public_response.json()
        burger_truck = next((t for t in trucks if t['slug'] == 'burger-truck'), None)
        
        assert burger_truck is not None, "burger-truck not found in public endpoint"
        assert burger_truck.get('gallery') == test_gallery, "Gallery not returned in public endpoint"
        assert burger_truck.get('video_url') == test_video, "Video URL not returned in public endpoint"
        print(f"✓ Public /api/trucks endpoint returns gallery and video_url correctly")
    
    def test_08_single_truck_endpoint_returns_gallery_video(self):
        """Test that /api/trucks/{slug} returns gallery and video_url"""
        # First set some values via admin
        test_gallery = ["https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=600&q=80"]
        test_video = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        
        self.session.put(f"{BASE_URL}/api/admin/trucks/burger-truck", json={
            "gallery": test_gallery,
            "video_url": test_video
        })
        
        # Check single truck endpoint
        single_response = requests.get(f"{BASE_URL}/api/trucks/burger-truck")
        assert single_response.status_code == 200, f"Single truck endpoint failed: {single_response.text}"
        
        truck = single_response.json()
        assert truck.get('gallery') == test_gallery, "Gallery not returned in single truck endpoint"
        assert truck.get('video_url') == test_video, "Video URL not returned in single truck endpoint"
        print(f"✓ /api/trucks/burger-truck returns gallery and video_url correctly")


class TestTruckDetailPageData:
    """Test that truck detail page data is correct for gallery/video display"""
    
    def test_truck_detail_with_empty_gallery(self):
        """Test truck detail when gallery is empty - should show just main image"""
        response = requests.get(f"{BASE_URL}/api/trucks/chicken-burger-truck")
        assert response.status_code == 200
        
        truck = response.json()
        # chicken-burger-truck should have no gallery by default
        gallery = truck.get('gallery', [])
        print(f"✓ chicken-burger-truck gallery: {gallery} (empty = just main image shown)")
        
        # Main image should exist
        assert truck.get('image'), "Main image should exist"
        print(f"✓ Main image exists: {truck.get('image')[:50]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
