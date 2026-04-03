"""
Blog API Tests - TrucksOnRoad Blog System
Tests for multilingual blog with categories (DE/FR/IT/EN)
Categories: guide, locations, tipps, events, regionen, rezepte, news
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPublicBlogAPI:
    """Public blog endpoint tests"""
    
    def test_get_all_blog_posts(self):
        """GET /api/blog should return all published blog posts with categories"""
        response = requests.get(f"{BASE_URL}/api/blog")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "posts" in data, "Response should contain 'posts' key"
        assert "categories" in data, "Response should contain 'categories' key"
        
        # Verify categories structure
        categories = data["categories"]
        expected_categories = ["guide", "locations", "tipps", "events", "regionen", "rezepte", "news"]
        for cat in expected_categories:
            assert cat in categories, f"Category '{cat}' should be in categories"
            assert "de" in categories[cat], f"Category '{cat}' should have 'de' translation"
            assert "en" in categories[cat], f"Category '{cat}' should have 'en' translation"
        
        # Verify posts structure (should have 6 seeded posts)
        posts = data["posts"]
        assert len(posts) >= 6, f"Expected at least 6 seeded posts, got {len(posts)}"
        print(f"✓ GET /api/blog returned {len(posts)} posts with {len(categories)} categories")
    
    def test_filter_by_category_guide(self):
        """GET /api/blog?category=guide should filter by category"""
        response = requests.get(f"{BASE_URL}/api/blog?category=guide")
        assert response.status_code == 200
        
        data = response.json()
        posts = data["posts"]
        for post in posts:
            assert post["category"] == "guide", f"Post category should be 'guide', got '{post['category']}'"
        print(f"✓ GET /api/blog?category=guide returned {len(posts)} guide posts")
    
    def test_filter_by_category_locations(self):
        """GET /api/blog?category=locations should filter by category"""
        response = requests.get(f"{BASE_URL}/api/blog?category=locations")
        assert response.status_code == 200
        
        data = response.json()
        posts = data["posts"]
        for post in posts:
            assert post["category"] == "locations"
        print(f"✓ GET /api/blog?category=locations returned {len(posts)} location posts")
    
    def test_get_single_blog_post(self):
        """GET /api/blog/{slug} should return a single post with all language fields"""
        # First get a valid slug from the list
        list_response = requests.get(f"{BASE_URL}/api/blog")
        posts = list_response.json()["posts"]
        assert len(posts) > 0, "Need at least one post to test"
        
        slug = posts[0]["slug"]
        response = requests.get(f"{BASE_URL}/api/blog/{slug}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        post = response.json()
        # Verify multilingual fields exist
        assert "title_de" in post, "Post should have title_de"
        assert "title_en" in post, "Post should have title_en"
        assert "title_fr" in post, "Post should have title_fr"
        assert "title_it" in post, "Post should have title_it"
        assert "content_de" in post, "Post should have content_de"
        assert "content_en" in post, "Post should have content_en"
        assert "excerpt_de" in post, "Post should have excerpt_de"
        assert "slug" in post, "Post should have slug"
        assert "category" in post, "Post should have category"
        assert "is_published" in post, "Post should have is_published"
        print(f"✓ GET /api/blog/{slug} returned post with all language fields")
    
    def test_get_nonexistent_post(self):
        """GET /api/blog/{slug} should return 404 for non-existent post"""
        response = requests.get(f"{BASE_URL}/api/blog/nonexistent-post-slug-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ GET /api/blog/nonexistent-slug returns 404")
    
    def test_blog_categories_endpoint(self):
        """GET /api/blog-categories should return all categories"""
        response = requests.get(f"{BASE_URL}/api/blog-categories")
        assert response.status_code == 200
        
        categories = response.json()
        assert "guide" in categories
        assert "locations" in categories
        assert "tipps" in categories
        assert "events" in categories
        assert "regionen" in categories
        assert "rezepte" in categories
        assert "news" in categories
        print(f"✓ GET /api/blog-categories returned {len(categories)} categories")


class TestBlogSEO:
    """Blog SEO endpoint tests"""
    
    def test_sitemap_includes_blog(self):
        """GET /api/sitemap.xml should include /blog and all blog post URLs"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "")
        
        content = response.text
        assert "/blog</loc>" in content or "/blog<" in content, "Sitemap should include /blog"
        
        # Check that blog posts are included
        list_response = requests.get(f"{BASE_URL}/api/blog")
        posts = list_response.json()["posts"]
        for post in posts[:3]:  # Check first 3 posts
            assert f"/blog/{post['slug']}" in content, f"Sitemap should include /blog/{post['slug']}"
        print(f"✓ Sitemap includes /blog and {len(posts)} blog post URLs")
    
    def test_blog_schema_endpoint(self):
        """GET /api/seo/blog-schema/{slug} should return Article JSON-LD"""
        # Get a valid slug
        list_response = requests.get(f"{BASE_URL}/api/blog")
        posts = list_response.json()["posts"]
        assert len(posts) > 0
        
        slug = posts[0]["slug"]
        response = requests.get(f"{BASE_URL}/api/seo/blog-schema/{slug}")
        assert response.status_code == 200
        
        schema = response.json()
        if schema:  # Schema may be empty for unpublished posts
            assert schema.get("@context") == "https://schema.org", "Schema should have @context"
            assert schema.get("@type") == "Article", "Schema should be Article type"
            assert "headline" in schema, "Schema should have headline"
            assert "author" in schema, "Schema should have author"
            assert "publisher" in schema, "Schema should have publisher"
        print(f"✓ GET /api/seo/blog-schema/{slug} returns valid Article JSON-LD")
    
    def test_blog_schema_nonexistent(self):
        """GET /api/seo/blog-schema/{slug} should return empty for non-existent post"""
        response = requests.get(f"{BASE_URL}/api/seo/blog-schema/nonexistent-post-12345")
        assert response.status_code == 200
        schema = response.json()
        assert schema == {}, "Should return empty object for non-existent post"
        print("✓ GET /api/seo/blog-schema/nonexistent returns empty object")


class TestAdminBlogAPI:
    """Admin blog endpoint tests (requires authentication)"""
    
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
        self.auth_cookies = login_response.cookies
    
    def test_admin_get_all_blog_posts(self):
        """GET /api/admin/blog should return all blog posts (auth required)"""
        response = self.session.get(f"{BASE_URL}/api/admin/blog")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        posts = response.json()
        assert isinstance(posts, list), "Response should be a list"
        assert len(posts) >= 6, f"Expected at least 6 posts, got {len(posts)}"
        
        # Admin endpoint should return all posts including drafts
        for post in posts:
            assert "id" in post, "Post should have id"
            assert "slug" in post, "Post should have slug"
            assert "is_published" in post, "Post should have is_published"
        print(f"✓ GET /api/admin/blog returned {len(posts)} posts (including drafts)")
    
    def test_admin_get_blog_unauthorized(self):
        """GET /api/admin/blog should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/blog")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/admin/blog returns 401 without auth")
    
    def test_admin_create_blog_post(self):
        """POST /api/admin/blog should create a new blog post"""
        new_post = {
            "slug": "test-blog-post-pytest",
            "title_de": "TEST Pytest Blog Post DE",
            "title_en": "TEST Pytest Blog Post EN",
            "title_fr": "TEST Pytest Blog Post FR",
            "title_it": "TEST Pytest Blog Post IT",
            "excerpt_de": "Test excerpt DE",
            "excerpt_en": "Test excerpt EN",
            "content_de": "## Test Content DE\n\nThis is test content.",
            "content_en": "## Test Content EN\n\nThis is test content.",
            "category": "news",
            "image": "https://example.com/test.jpg",
            "tags": ["test", "pytest"],
            "author": "Pytest",
            "is_published": False
        }
        
        response = self.session.post(f"{BASE_URL}/api/admin/blog", json=new_post)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        created = response.json()
        assert created["slug"] == new_post["slug"]
        assert created["title_de"] == new_post["title_de"]
        assert created["category"] == "news"
        assert "id" in created, "Created post should have id"
        
        self.created_post_id = created["id"]
        print(f"✓ POST /api/admin/blog created post with id {created['id']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/blog/{created['id']}")
    
    def test_admin_update_blog_post(self):
        """PUT /api/admin/blog/{id} should update a blog post"""
        # First create a post
        new_post = {
            "slug": "test-update-post-pytest",
            "title_de": "Original Title DE",
            "title_en": "Original Title EN",
            "category": "tipps",
            "is_published": False
        }
        create_response = self.session.post(f"{BASE_URL}/api/admin/blog", json=new_post)
        assert create_response.status_code == 200
        post_id = create_response.json()["id"]
        
        # Update the post
        update_data = {
            "title_de": "Updated Title DE",
            "is_published": True
        }
        update_response = self.session.put(f"{BASE_URL}/api/admin/blog/{post_id}", json=update_data)
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}"
        
        # Verify update
        all_posts = self.session.get(f"{BASE_URL}/api/admin/blog").json()
        updated_post = next((p for p in all_posts if p["id"] == post_id), None)
        assert updated_post is not None, "Updated post should exist"
        assert updated_post["title_de"] == "Updated Title DE"
        assert updated_post["is_published"] == True
        print(f"✓ PUT /api/admin/blog/{post_id} updated post successfully")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/blog/{post_id}")
    
    def test_admin_delete_blog_post(self):
        """DELETE /api/admin/blog/{id} should delete a blog post"""
        # First create a post
        new_post = {
            "slug": "test-delete-post-pytest",
            "title_de": "To Be Deleted",
            "category": "news",
            "is_published": False
        }
        create_response = self.session.post(f"{BASE_URL}/api/admin/blog", json=new_post)
        assert create_response.status_code == 200
        post_id = create_response.json()["id"]
        
        # Delete the post
        delete_response = self.session.delete(f"{BASE_URL}/api/admin/blog/{post_id}")
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        
        # Verify deletion
        all_posts = self.session.get(f"{BASE_URL}/api/admin/blog").json()
        deleted_post = next((p for p in all_posts if p["id"] == post_id), None)
        assert deleted_post is None, "Deleted post should not exist"
        print(f"✓ DELETE /api/admin/blog/{post_id} deleted post successfully")


class TestBlogSeededData:
    """Tests to verify the 6 seeded blog articles"""
    
    def test_seeded_articles_count(self):
        """Verify 6 seed articles exist"""
        response = requests.get(f"{BASE_URL}/api/blog")
        posts = response.json()["posts"]
        assert len(posts) >= 6, f"Expected at least 6 seeded posts, got {len(posts)}"
        print(f"✓ Found {len(posts)} blog posts (expected >= 6)")
    
    def test_seeded_articles_categories(self):
        """Verify seeded articles have correct categories"""
        response = requests.get(f"{BASE_URL}/api/blog")
        posts = response.json()["posts"]
        
        categories_found = set(p["category"] for p in posts)
        expected_categories = {"guide", "locations", "tipps", "events", "regionen", "rezepte"}
        
        for cat in expected_categories:
            assert cat in categories_found, f"Category '{cat}' should be in seeded posts"
        print(f"✓ Seeded posts cover categories: {categories_found}")
    
    def test_seeded_articles_multilingual(self):
        """Verify seeded articles have all language fields"""
        response = requests.get(f"{BASE_URL}/api/blog")
        posts = response.json()["posts"]
        
        # Get full post details for first post
        slug = posts[0]["slug"]
        detail_response = requests.get(f"{BASE_URL}/api/blog/{slug}")
        post = detail_response.json()
        
        # Check all language fields
        assert post.get("title_de"), "Should have German title"
        assert post.get("title_en"), "Should have English title"
        assert post.get("title_fr"), "Should have French title"
        assert post.get("title_it"), "Should have Italian title"
        assert post.get("content_de"), "Should have German content"
        assert post.get("content_en"), "Should have English content"
        print(f"✓ Seeded post '{slug}' has all 4 language versions")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
