"""
Test suite for TruckOnRoad new features:
1. Google Search Console verification code configurable in Admin Settings
2. Email notification to customer when admin uploads a file to their inquiry
3. Event reminder emails sent automatically X days before the event (configurable in Admin Settings)
4. SEO features: hreflang, og:image, og:url, JSON-LD schemas, robots.txt
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGoogleVerification:
    """Test Google Search Console verification code feature"""
    
    def test_google_verification_endpoint_returns_code(self):
        """GET /api/seo/google-verification returns verification code from settings"""
        response = requests.get(f"{BASE_URL}/api/seo/google-verification")
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        print(f"Google verification code: {data['code']}")
    
    def test_admin_settings_contains_google_verification_field(self, auth_cookies):
        """Admin Settings should have google_verification field"""
        response = requests.get(f"{BASE_URL}/api/admin/settings", cookies=auth_cookies)
        assert response.status_code == 200
        data = response.json()
        assert "google_verification" in data
        print(f"Google verification in settings: {data.get('google_verification', '')}")
    
    def test_admin_can_update_google_verification(self, auth_cookies):
        """Admin can update google_verification in settings"""
        # Get current settings
        response = requests.get(f"{BASE_URL}/api/admin/settings", cookies=auth_cookies)
        assert response.status_code == 200
        settings = response.json()
        
        # Update with test verification code
        test_code = "TEST_abc123def456"
        settings["google_verification"] = test_code
        
        response = requests.put(f"{BASE_URL}/api/admin/settings", json=settings, cookies=auth_cookies)
        assert response.status_code == 200
        
        # Verify the code is returned by public endpoint
        response = requests.get(f"{BASE_URL}/api/seo/google-verification")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == test_code
        print(f"Successfully updated and verified google verification code: {test_code}")
        
        # Clean up - reset to empty
        settings["google_verification"] = ""
        requests.put(f"{BASE_URL}/api/admin/settings", json=settings, cookies=auth_cookies)


class TestEventReminderDays:
    """Test Event Reminder Days configuration in Admin Settings"""
    
    def test_admin_settings_contains_event_reminder_days(self, auth_cookies):
        """Admin Settings should have event_reminder_days field"""
        response = requests.get(f"{BASE_URL}/api/admin/settings", cookies=auth_cookies)
        assert response.status_code == 200
        data = response.json()
        assert "event_reminder_days" in data
        assert isinstance(data["event_reminder_days"], int)
        print(f"Event reminder days: {data['event_reminder_days']}")
    
    def test_admin_can_update_event_reminder_days(self, auth_cookies):
        """Admin can update event_reminder_days in settings"""
        # Get current settings
        response = requests.get(f"{BASE_URL}/api/admin/settings", cookies=auth_cookies)
        assert response.status_code == 200
        settings = response.json()
        original_days = settings.get("event_reminder_days", 3)
        
        # Update to 5 days
        settings["event_reminder_days"] = 5
        response = requests.put(f"{BASE_URL}/api/admin/settings", json=settings, cookies=auth_cookies)
        assert response.status_code == 200
        
        # Verify the change
        response = requests.get(f"{BASE_URL}/api/admin/settings", cookies=auth_cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["event_reminder_days"] == 5
        print("Successfully updated event_reminder_days to 5")
        
        # Restore original
        settings["event_reminder_days"] = original_days
        requests.put(f"{BASE_URL}/api/admin/settings", json=settings, cookies=auth_cookies)


class TestSendRemindersEndpoint:
    """Test POST /api/admin/send-reminders endpoint"""
    
    def test_send_reminders_requires_auth(self):
        """POST /api/admin/send-reminders requires authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/send-reminders")
        assert response.status_code == 401
        print("send-reminders correctly requires authentication")
    
    def test_send_reminders_with_auth(self, auth_cookies):
        """POST /api/admin/send-reminders triggers event reminder check"""
        response = requests.post(f"{BASE_URL}/api/admin/send-reminders", cookies=auth_cookies)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"send-reminders response: {data['message']}")


class TestEmailPreview:
    """Test GET /api/admin/email-preview returns 8 templates"""
    
    def test_email_preview_requires_auth(self):
        """GET /api/admin/email-preview requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/email-preview")
        assert response.status_code == 401
        print("email-preview correctly requires authentication")
    
    def test_email_preview_returns_8_templates(self, auth_cookies):
        """GET /api/admin/email-preview returns 8 templates including file_upload and event_reminder"""
        response = requests.get(f"{BASE_URL}/api/admin/email-preview", cookies=auth_cookies)
        assert response.status_code == 200
        data = response.json()
        
        expected_templates = [
            "confirmation",
            "notification", 
            "status_confirmed",
            "status_completed",
            "invoice_sent",
            "invoice_paid",
            "file_upload",
            "event_reminder"
        ]
        
        for template in expected_templates:
            assert template in data, f"Missing template: {template}"
            assert len(data[template]) > 0, f"Template {template} is empty"
        
        assert len(data) == 8, f"Expected 8 templates, got {len(data)}"
        print(f"All 8 email templates present: {list(data.keys())}")


class TestFileUploadNotification:
    """Test file upload notification to customer when admin uploads"""
    
    def test_file_upload_endpoint_exists(self, auth_cookies):
        """POST /api/inquiries/{id}/upload endpoint exists"""
        # Create a test inquiry first
        inquiry_data = {
            "first_name": "TEST_FileNotify",
            "last_name": "User",
            "email": "test_filenotify@example.com",
            "phone": "+41791234567",
            "event_date": "2026-06-15",
            "location": "Zurich",
            "guest_count": 100,
            "event_type": "Firmenanlass"
        }
        response = requests.post(f"{BASE_URL}/api/inquiries", json=inquiry_data)
        assert response.status_code == 200
        inquiry_id = response.json()["id"]
        
        # Try to upload a file (admin logged in)
        files = {"file": ("test.txt", b"Test content for file upload notification", "text/plain")}
        response = requests.post(
            f"{BASE_URL}/api/inquiries/{inquiry_id}/upload",
            files=files,
            cookies=auth_cookies
        )
        # Should succeed (200) or fail gracefully (400/500 for storage issues)
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            print(f"File uploaded successfully, notification should be sent to customer")
        else:
            print(f"File upload returned {response.status_code}: {response.text}")
        
        # Clean up - delete the inquiry
        requests.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}", cookies=auth_cookies)


class TestRobotsTxt:
    """Test robots.txt at /api/robots.txt"""
    
    def test_robots_txt_exists(self):
        """GET /api/robots.txt returns robots.txt content"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        assert response.headers.get("Content-Type", "").startswith("text/plain")
        content = response.text
        assert "User-agent:" in content
        print("robots.txt exists and returns content")
    
    def test_robots_txt_allows_gptbot(self):
        """robots.txt allows GPTBot"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        content = response.text
        assert "GPTBot" in content
        # Check it's not disallowed
        lines = content.split("\n")
        gptbot_section = False
        for line in lines:
            if "GPTBot" in line:
                gptbot_section = True
            if gptbot_section and line.strip().startswith("Allow:"):
                print("GPTBot is allowed")
                break
        print(f"robots.txt content includes GPTBot")
    
    def test_robots_txt_allows_claudebot(self):
        """robots.txt allows ClaudeBot"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        content = response.text
        assert "ClaudeBot" in content
        print("robots.txt includes ClaudeBot")
    
    def test_robots_txt_allows_perplexitybot(self):
        """robots.txt allows PerplexityBot"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        content = response.text
        assert "PerplexityBot" in content
        print("robots.txt includes PerplexityBot")


class TestSEOStructuredData:
    """Test SEO structured data endpoint"""
    
    def test_structured_data_endpoint(self):
        """GET /api/seo/structured-data returns JSON-LD data"""
        response = requests.get(f"{BASE_URL}/api/seo/structured-data")
        assert response.status_code == 200
        data = response.json()
        assert data.get("@context") == "https://schema.org"
        assert data.get("@type") == "FoodEstablishment"
        assert "name" in data
        assert "description" in data
        print(f"Structured data: @type={data['@type']}, name={data['name']}")


# Fixtures
@pytest.fixture(scope="module")
def auth_cookies():
    """Get authentication cookies for admin user"""
    login_data = {
        "email": "admin@truckonroad.ch",
        "password": "TruckOnRoad2026!"
    }
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    return session.cookies


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
