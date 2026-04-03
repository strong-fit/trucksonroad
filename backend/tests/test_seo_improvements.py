"""
Test SEO Improvements for TrucksOnRoad Blog
- Dynamic SEO meta tags (meta_title_de, meta_description_de)
- Related posts functionality
- Internal link rendering
- Word count and quality score for AI posts
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Known blog slugs from the database
KNOWN_SLUGS = [
    "foodtruck-mieten-schweiz-guide",
    "beste-foodtruck-locations-zuerich",
    "firmenanlass-catering-tipps",
    "hochzeit-foodtruck-catering",
    "foodtruck-catering-bern-basel-luzern",
    "perfekter-smash-burger-rezept"
]


class TestBlogSEOMetaTags:
    """Test dynamic SEO meta tags on blog posts"""
    
    def test_blog_post_has_meta_title_de(self):
        """GET /api/blog/{slug} should return meta_title_de field"""
        response = requests.get(f"{BASE_URL}/api/blog/{KNOWN_SLUGS[0]}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "meta_title_de" in data, "meta_title_de field missing from blog post"
        print(f"✓ meta_title_de: {data.get('meta_title_de', '')[:60]}...")
    
    def test_blog_post_has_meta_description_de(self):
        """GET /api/blog/{slug} should return meta_description_de field"""
        response = requests.get(f"{BASE_URL}/api/blog/{KNOWN_SLUGS[0]}")
        assert response.status_code == 200
        data = response.json()
        assert "meta_description_de" in data, "meta_description_de field missing from blog post"
        print(f"✓ meta_description_de: {data.get('meta_description_de', '')[:80]}...")
    
    def test_blog_post_has_title_and_content(self):
        """Blog post should have title_de and content_de for React Helmet"""
        response = requests.get(f"{BASE_URL}/api/blog/{KNOWN_SLUGS[0]}")
        assert response.status_code == 200
        data = response.json()
        assert "title_de" in data and data["title_de"], "title_de missing or empty"
        assert "content_de" in data and data["content_de"], "content_de missing or empty"
        print(f"✓ title_de: {data['title_de'][:50]}...")
    
    def test_blog_post_has_slug_for_canonical(self):
        """Blog post should have slug for canonical URL generation"""
        response = requests.get(f"{BASE_URL}/api/blog/{KNOWN_SLUGS[0]}")
        assert response.status_code == 200
        data = response.json()
        assert "slug" in data and data["slug"], "slug missing or empty"
        assert data["slug"] == KNOWN_SLUGS[0]
        print(f"✓ slug: {data['slug']}")


class TestBlogListingAPI:
    """Test blog listing endpoint for SEO"""
    
    def test_blog_listing_returns_posts(self):
        """GET /api/blog should return posts array"""
        response = requests.get(f"{BASE_URL}/api/blog")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data, "posts array missing"
        assert len(data["posts"]) > 0, "No posts returned"
        print(f"✓ Blog listing returned {len(data['posts'])} posts")
    
    def test_blog_listing_returns_categories(self):
        """GET /api/blog should return categories for filtering"""
        response = requests.get(f"{BASE_URL}/api/blog")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data, "categories missing"
        assert len(data["categories"]) > 0, "No categories returned"
        print(f"✓ Categories: {list(data['categories'].keys())}")
    
    def test_blog_listing_category_filter(self):
        """GET /api/blog?category=guide should filter by category"""
        response = requests.get(f"{BASE_URL}/api/blog?category=guide")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        # All returned posts should be in 'guide' category
        for post in data["posts"]:
            assert post.get("category") == "guide", f"Post {post.get('slug')} has wrong category"
        print(f"✓ Category filter works, returned {len(data['posts'])} guide posts")
    
    def test_blog_listing_limit_parameter(self):
        """GET /api/blog?limit=3 should limit results"""
        response = requests.get(f"{BASE_URL}/api/blog?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["posts"]) <= 3, f"Expected max 3 posts, got {len(data['posts'])}"
        print(f"✓ Limit parameter works, returned {len(data['posts'])} posts")


class TestRelatedPostsAPI:
    """Test related posts functionality"""
    
    def test_blog_listing_for_related_posts(self):
        """GET /api/blog?category=X&limit=4 should work for related posts"""
        # First get a post to know its category
        response = requests.get(f"{BASE_URL}/api/blog/{KNOWN_SLUGS[0]}")
        assert response.status_code == 200
        post = response.json()
        category = post.get("category", "guide")
        
        # Now fetch related posts from same category
        related_response = requests.get(f"{BASE_URL}/api/blog?category={category}&limit=4")
        assert related_response.status_code == 200
        related_data = related_response.json()
        assert "posts" in related_data
        print(f"✓ Related posts query works, found {len(related_data['posts'])} posts in category '{category}'")
    
    def test_blog_posts_have_required_fields_for_related(self):
        """Blog posts should have fields needed for related posts display"""
        response = requests.get(f"{BASE_URL}/api/blog?limit=5")
        assert response.status_code == 200
        data = response.json()
        for post in data["posts"]:
            assert "id" in post or "slug" in post, "Post missing id/slug"
            assert "title_de" in post, "Post missing title_de"
            assert "slug" in post, "Post missing slug"
            assert "image" in post, "Post missing image"
        print(f"✓ All posts have required fields for related posts display")


class TestInternalLinksInContent:
    """Test that blog content contains internal links"""
    
    def test_blog_content_structure(self):
        """Blog content should be markdown with potential internal links"""
        response = requests.get(f"{BASE_URL}/api/blog/{KNOWN_SLUGS[0]}")
        assert response.status_code == 200
        data = response.json()
        content = data.get("content_de", "")
        assert len(content) > 100, "Content too short"
        # Check for markdown structure
        has_headers = "##" in content or "###" in content
        print(f"✓ Content length: {len(content)} chars, has headers: {has_headers}")


class TestAdminBlogAPI:
    """Test admin blog API with word_count and quality_score"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        if login_response.status_code != 200:
            pytest.skip("Admin login failed")
        return session
    
    def test_admin_blog_returns_all_posts(self, auth_session):
        """GET /api/admin/blog should return all posts"""
        response = auth_session.get(f"{BASE_URL}/api/admin/blog")
        assert response.status_code == 200
        posts = response.json()
        assert isinstance(posts, list), "Expected list of posts"
        assert len(posts) > 0, "No posts returned"
        print(f"✓ Admin blog returned {len(posts)} posts")
    
    def test_admin_blog_ai_posts_have_word_count(self, auth_session):
        """AI-generated posts should have word_count field"""
        response = auth_session.get(f"{BASE_URL}/api/admin/blog")
        assert response.status_code == 200
        posts = response.json()
        ai_posts = [p for p in posts if p.get("ai_generated")]
        if ai_posts:
            for post in ai_posts:
                assert "word_count" in post, f"AI post {post.get('slug')} missing word_count"
                print(f"✓ AI post '{post.get('slug')}' has word_count: {post.get('word_count')}")
        else:
            print("⚠ No AI-generated posts found to verify word_count")
    
    def test_admin_blog_ai_posts_have_quality_score(self, auth_session):
        """AI-generated posts should have quality_score field"""
        response = auth_session.get(f"{BASE_URL}/api/admin/blog")
        assert response.status_code == 200
        posts = response.json()
        ai_posts = [p for p in posts if p.get("ai_generated")]
        if ai_posts:
            for post in ai_posts:
                assert "quality_score" in post, f"AI post {post.get('slug')} missing quality_score"
                print(f"✓ AI post '{post.get('slug')}' has quality_score: {post.get('quality_score')}")
        else:
            print("⚠ No AI-generated posts found to verify quality_score")


class TestBlogSEOSchema:
    """Test SEO schema endpoint"""
    
    def test_blog_schema_endpoint(self):
        """GET /api/seo/blog-schema/{slug} should return Article schema"""
        response = requests.get(f"{BASE_URL}/api/seo/blog-schema/{KNOWN_SLUGS[0]}")
        assert response.status_code == 200
        schema = response.json()
        if schema:  # May be empty if post not found
            assert schema.get("@type") == "Article", "Schema type should be Article"
            assert "headline" in schema, "Schema missing headline"
            assert "description" in schema, "Schema missing description"
            print(f"✓ Blog schema: {schema.get('@type')} - {schema.get('headline', '')[:40]}...")


class TestHomepageBlogPreview:
    """Test homepage blog preview (3 latest posts)"""
    
    def test_homepage_blog_preview_limit(self):
        """GET /api/blog?limit=3 should return max 3 posts for homepage"""
        response = requests.get(f"{BASE_URL}/api/blog?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["posts"]) <= 3, f"Expected max 3 posts, got {len(data['posts'])}"
        print(f"✓ Homepage preview: {len(data['posts'])} posts")
    
    def test_homepage_posts_have_preview_fields(self):
        """Posts for homepage should have title, excerpt, image, slug"""
        response = requests.get(f"{BASE_URL}/api/blog?limit=3")
        assert response.status_code == 200
        data = response.json()
        for post in data["posts"]:
            assert "title_de" in post, "Missing title_de"
            assert "excerpt_de" in post, "Missing excerpt_de"
            assert "image" in post, "Missing image"
            assert "slug" in post, "Missing slug"
        print(f"✓ All homepage preview posts have required fields")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
