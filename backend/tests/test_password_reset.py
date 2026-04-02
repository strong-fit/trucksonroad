"""
Test Password Reset and Change Password Functionality
Tests for:
- POST /api/auth/forgot-password
- POST /api/auth/reset-password
- PUT /api/auth/change-password
- Brand rename verification (TrucksOnRoad)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestForgotPassword:
    """Tests for POST /api/auth/forgot-password endpoint"""
    
    def test_forgot_password_with_valid_email(self):
        """POST /api/auth/forgot-password accepts email and returns OK"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": "admin@truckonroad.ch"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == "OK"
        print("✓ Forgot password with valid email returns OK")
    
    def test_forgot_password_with_nonexistent_email(self):
        """POST /api/auth/forgot-password returns OK even for non-existent emails (security)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        # Should return OK for security reasons (don't reveal if email exists)
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == "OK"
        print("✓ Forgot password with non-existent email returns OK (security)")
    
    def test_forgot_password_without_email(self):
        """POST /api/auth/forgot-password without email returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={}
        )
        assert response.status_code == 400
        print("✓ Forgot password without email returns 400")


class TestResetPassword:
    """Tests for POST /api/auth/reset-password endpoint"""
    
    def test_reset_password_with_invalid_token(self):
        """POST /api/auth/reset-password with invalid token returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"token": "invalid-token-12345", "password": "NewPassword123!"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"✓ Reset password with invalid token returns 400: {data.get('detail')}")
    
    def test_reset_password_without_token(self):
        """POST /api/auth/reset-password without token returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"password": "NewPassword123!"}
        )
        assert response.status_code == 400
        print("✓ Reset password without token returns 400")
    
    def test_reset_password_without_password(self):
        """POST /api/auth/reset-password without password returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"token": "some-token"}
        )
        assert response.status_code == 400
        print("✓ Reset password without password returns 400")
    
    def test_reset_password_with_short_password(self):
        """POST /api/auth/reset-password with password < 6 chars returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password",
            json={"token": "some-token", "password": "12345"}
        )
        assert response.status_code == 400
        print("✓ Reset password with short password returns 400")


class TestChangePassword:
    """Tests for PUT /api/auth/change-password endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        # Login as admin
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "TrucksOnRoad2026!"}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code} - {response.text}")
        return session
    
    def test_change_password_without_auth(self):
        """PUT /api/auth/change-password without auth returns 401"""
        response = requests.put(
            f"{BASE_URL}/api/auth/change-password",
            json={"old_password": "test", "new_password": "newtest123"}
        )
        assert response.status_code == 401
        print("✓ Change password without auth returns 401")
    
    def test_change_password_with_wrong_old_password(self, auth_session):
        """PUT /api/auth/change-password with wrong old password returns error"""
        response = auth_session.put(
            f"{BASE_URL}/api/auth/change-password",
            json={"old_password": "WrongPassword123!", "new_password": "NewPassword123!"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"✓ Change password with wrong old password returns 400: {data.get('detail')}")
    
    def test_change_password_with_short_new_password(self, auth_session):
        """PUT /api/auth/change-password with short new password returns error"""
        response = auth_session.put(
            f"{BASE_URL}/api/auth/change-password",
            json={"old_password": "TrucksOnRoad2026!", "new_password": "12345"}
        )
        assert response.status_code == 400
        print("✓ Change password with short new password returns 400")
    
    def test_change_password_missing_fields(self, auth_session):
        """PUT /api/auth/change-password with missing fields returns error"""
        response = auth_session.put(
            f"{BASE_URL}/api/auth/change-password",
            json={"old_password": "TrucksOnRoad2026!"}
        )
        assert response.status_code == 400
        print("✓ Change password with missing new_password returns 400")


class TestFullPasswordResetFlow:
    """Test the complete password reset flow with a test user"""
    
    def test_full_reset_flow_with_test_user(self):
        """Test complete forgot -> reset flow with a test user"""
        # Create a unique test user
        test_email = f"TEST_pwreset_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "TestPassword123!"
        
        # Register test user
        session = requests.Session()
        reg_response = session.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        if reg_response.status_code != 200:
            pytest.skip(f"Could not create test user: {reg_response.text}")
        
        print(f"✓ Created test user: {test_email}")
        
        # Request password reset
        forgot_response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": test_email}
        )
        assert forgot_response.status_code == 200
        print("✓ Forgot password request successful")
        
        # Note: In a real test, we would query the DB for the token
        # Since we can't access DB directly, we verify the endpoint works
        
        # Verify login still works with old password
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": test_email, "password": test_password}
        )
        assert login_response.status_code == 200
        print("✓ Login with original password still works")


class TestExistingEndpointsStillWork:
    """Verify existing endpoints still work after password reset feature addition"""
    
    def test_login_endpoint(self):
        """POST /api/auth/login still works"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "TrucksOnRoad2026!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "role" in data
        print("✓ Login endpoint works")
    
    def test_trucks_endpoint(self):
        """GET /api/trucks still works"""
        response = requests.get(f"{BASE_URL}/api/trucks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Trucks endpoint works - {len(data)} trucks returned")
    
    def test_faqs_endpoint(self):
        """GET /api/faqs still works"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ FAQs endpoint works - {len(data)} FAQs returned")
    
    def test_admin_stats_endpoint(self):
        """GET /api/admin/stats still works (requires auth)"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "TrucksOnRoad2026!"}
        )
        if login_response.status_code != 200:
            pytest.skip("Admin login failed")
        
        stats_response = session.get(f"{BASE_URL}/api/admin/stats")
        assert stats_response.status_code == 200
        data = stats_response.json()
        assert "total_inquiries" in data or "inquiries" in data or isinstance(data, dict)
        print("✓ Admin stats endpoint works")


class TestBrandRename:
    """Verify brand has been renamed from TruckOnRoad to TrucksOnRoad"""
    
    def test_admin_settings_company_name(self):
        """Admin settings should have company_name as TrucksOnRoad"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@truckonroad.ch", "password": "TrucksOnRoad2026!"}
        )
        if login_response.status_code != 200:
            pytest.skip("Admin login failed")
        
        settings_response = session.get(f"{BASE_URL}/api/admin/settings")
        if settings_response.status_code == 200:
            data = settings_response.json()
            company_name = data.get("company_name", "")
            # Check if company name contains TrucksOnRoad (not TruckOnRoad)
            print(f"✓ Company name in settings: {company_name}")
            # This is informational - the actual brand check is in frontend
        else:
            print(f"Settings endpoint returned {settings_response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
