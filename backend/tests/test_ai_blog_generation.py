"""
AI Blog Generation Tests - TrucksOnRoad
Tests for AI-powered automatic blog generation using GPT-5.2
Features: Manual generation, auto-toggle, multilingual posts (DE/FR/IT/EN)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAIBlogGenerationEndpoints:
    """Tests for AI blog generation admin endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin authentication failed")
    
    def test_auto_status_endpoint(self):
        """GET /api/admin/blog/auto-status should return enabled/interval_hours settings"""
        response = self.session.get(f"{BASE_URL}/api/admin/blog/auto-status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "enabled" in data, "Response should contain 'enabled' field"
        assert "interval_hours" in data, "Response should contain 'interval_hours' field"
        assert isinstance(data["enabled"], bool), "enabled should be boolean"
        assert isinstance(data["interval_hours"], int), "interval_hours should be integer"
        print(f"✓ GET /api/admin/blog/auto-status: enabled={data['enabled']}, interval={data['interval_hours']}h")
    
    def test_auto_status_requires_auth(self):
        """GET /api/admin/blog/auto-status should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/blog/auto-status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/admin/blog/auto-status returns 401 without auth")
    
    def test_auto_toggle_enable(self):
        """POST /api/admin/blog/auto-toggle should enable auto-posting"""
        response = self.session.post(f"{BASE_URL}/api/admin/blog/auto-toggle", json={
            "enabled": True,
            "interval_hours": 12
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["enabled"] == True, "enabled should be True"
        assert data["interval_hours"] == 12, "interval_hours should be 12"
        print("✓ POST /api/admin/blog/auto-toggle enabled auto-posting (12h interval)")
        
        # Verify persistence
        status_response = self.session.get(f"{BASE_URL}/api/admin/blog/auto-status")
        status = status_response.json()
        assert status["enabled"] == True, "Auto-posting should be enabled"
        assert status["interval_hours"] == 12, "Interval should be 12h"
    
    def test_auto_toggle_disable(self):
        """POST /api/admin/blog/auto-toggle should disable auto-posting"""
        response = self.session.post(f"{BASE_URL}/api/admin/blog/auto-toggle", json={
            "enabled": False,
            "interval_hours": 24
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["enabled"] == False, "enabled should be False"
        print("✓ POST /api/admin/blog/auto-toggle disabled auto-posting")
    
    def test_auto_toggle_requires_auth(self):
        """POST /api/admin/blog/auto-toggle should require authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/blog/auto-toggle", json={
            "enabled": True,
            "interval_hours": 24
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/admin/blog/auto-toggle returns 401 without auth")
    
    def test_auto_toggle_interval_options(self):
        """POST /api/admin/blog/auto-toggle should accept various interval values"""
        intervals = [6, 12, 24, 48, 72]
        for interval in intervals:
            response = self.session.post(f"{BASE_URL}/api/admin/blog/auto-toggle", json={
                "enabled": True,
                "interval_hours": interval
            })
            assert response.status_code == 200
            data = response.json()
            assert data["interval_hours"] == interval, f"Interval should be {interval}"
        
        # Reset to disabled
        self.session.post(f"{BASE_URL}/api/admin/blog/auto-toggle", json={
            "enabled": False,
            "interval_hours": 24
        })
        print(f"✓ Auto-toggle accepts intervals: {intervals}")


class TestAIBlogGeneration:
    """Tests for AI blog post generation (GPT-5.2)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin authentication failed")
    
    def test_generate_endpoint_requires_auth(self):
        """POST /api/admin/blog/generate should require authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/blog/generate")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/admin/blog/generate returns 401 without auth")
    
    def test_generate_ai_blog_post(self):
        """POST /api/admin/blog/generate should create a new AI-generated blog post"""
        # This test takes ~10-20 seconds due to GPT-5.2 API call
        response = self.session.post(f"{BASE_URL}/api/admin/blog/generate", timeout=60)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        post = response.json()
        
        # Verify AI-generated post structure
        assert "id" in post, "Post should have id"
        assert "slug" in post, "Post should have slug"
        assert post.get("ai_generated") == True, "Post should have ai_generated=true"
        assert post.get("is_published") == True, "AI post should be auto-published"
        assert post.get("author") == "TrucksOnRoad KI", "Author should be 'TrucksOnRoad KI'"
        
        # Verify multilingual content (DE/FR/IT/EN)
        assert post.get("title_de"), "Post should have German title"
        assert post.get("title_en"), "Post should have English title"
        assert post.get("title_fr"), "Post should have French title"
        assert post.get("title_it"), "Post should have Italian title"
        
        assert post.get("excerpt_de"), "Post should have German excerpt"
        assert post.get("excerpt_en"), "Post should have English excerpt"
        assert post.get("excerpt_fr"), "Post should have French excerpt"
        assert post.get("excerpt_it"), "Post should have Italian excerpt"
        
        assert post.get("content_de"), "Post should have German content"
        assert post.get("content_en"), "Post should have English content"
        assert post.get("content_fr"), "Post should have French content"
        assert post.get("content_it"), "Post should have Italian content"
        
        # Verify category and tags
        assert post.get("category") in ["guide", "locations", "tipps", "events", "regionen", "rezepte", "news"], \
            f"Category should be valid, got {post.get('category')}"
        assert isinstance(post.get("tags"), list), "Tags should be a list"
        
        print(f"✓ POST /api/admin/blog/generate created AI post: '{post['title_de'][:50]}...'")
        print(f"  - Slug: {post['slug']}")
        print(f"  - Category: {post['category']}")
        print(f"  - Tags: {post['tags'][:3]}...")
        
        # Store for cleanup
        self.generated_post_id = post["id"]
        
        # Verify post appears in public blog list
        blog_response = requests.get(f"{BASE_URL}/api/blog")
        posts = blog_response.json()["posts"]
        found = any(p["id"] == post["id"] for p in posts)
        assert found, "AI-generated post should appear in public blog list"
        print("✓ AI-generated post appears in GET /api/blog")
        
        # Cleanup - delete the generated post
        delete_response = self.session.delete(f"{BASE_URL}/api/admin/blog/{post['id']}")
        assert delete_response.status_code == 200, "Should be able to delete AI-generated post"
        print(f"✓ Cleanup: Deleted AI-generated post {post['id']}")


class TestExistingAIGeneratedPosts:
    """Tests for existing AI-generated posts in the system"""
    
    def test_ai_posts_have_ai_generated_flag(self):
        """AI-generated posts should have ai_generated=true"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin authentication failed")
        
        # Get all posts from admin endpoint
        response = session.get(f"{BASE_URL}/api/admin/blog")
        posts = response.json()
        
        ai_posts = [p for p in posts if p.get("ai_generated") == True]
        print(f"✓ Found {len(ai_posts)} AI-generated posts out of {len(posts)} total")
        
        for post in ai_posts:
            assert post.get("author") == "TrucksOnRoad KI", f"AI post author should be 'TrucksOnRoad KI'"
            assert post.get("is_published") == True, "AI posts should be published"
            print(f"  - {post['slug']}: {post['title_de'][:40]}...")
    
    def test_homepage_blog_preview_limit(self):
        """GET /api/blog?limit=3 should return up to 3 latest posts for homepage"""
        response = requests.get(f"{BASE_URL}/api/blog?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        posts = data["posts"]
        assert len(posts) <= 3, f"Should return max 3 posts, got {len(posts)}"
        
        # Verify posts are sorted by created_at descending (latest first)
        if len(posts) >= 2:
            for i in range(len(posts) - 1):
                assert posts[i]["created_at"] >= posts[i+1]["created_at"], \
                    "Posts should be sorted by created_at descending"
        
        print(f"✓ GET /api/blog?limit=3 returned {len(posts)} posts (sorted by date)")
        for post in posts:
            ai_badge = " [KI]" if post.get("ai_generated") else ""
            print(f"  - {post['slug']}{ai_badge}")


class TestAdminDeleteAIPost:
    """Tests for deleting AI-generated posts"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin authentication failed")
    
    def test_can_delete_ai_generated_post(self):
        """Admin should be able to delete AI-generated posts"""
        # Get all posts
        response = self.session.get(f"{BASE_URL}/api/admin/blog")
        posts = response.json()
        
        ai_posts = [p for p in posts if p.get("ai_generated") == True]
        if not ai_posts:
            pytest.skip("No AI-generated posts to test deletion")
        
        # We won't actually delete existing posts, just verify the endpoint works
        # by creating a test post with ai_generated flag and deleting it
        test_post = {
            "slug": "test-ai-delete-pytest",
            "title_de": "TEST AI Delete Post",
            "title_en": "TEST AI Delete Post EN",
            "category": "news",
            "is_published": True,
            "ai_generated": True,
            "author": "TrucksOnRoad KI"
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/admin/blog", json=test_post)
        if create_response.status_code != 200:
            pytest.skip("Could not create test post")
        
        post_id = create_response.json()["id"]
        
        # Delete the post
        delete_response = self.session.delete(f"{BASE_URL}/api/admin/blog/{post_id}")
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        
        # Verify deletion
        all_posts = self.session.get(f"{BASE_URL}/api/admin/blog").json()
        deleted = next((p for p in all_posts if p["id"] == post_id), None)
        assert deleted is None, "Deleted post should not exist"
        
        print("✓ Admin can delete AI-generated posts")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
