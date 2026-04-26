"""
Test suite for Passwordless Authentication Flow
Tests: send-code, verify-code, complete-profile endpoints
"""
import pytest
import requests
import os
import time
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

# Test email prefix for cleanup (lowercase since API lowercases emails)
TEST_EMAIL_PREFIX = "test_passwordless_"


@pytest.fixture(scope="module")
def mongo_client():
    """MongoDB client for direct DB access (to read verification codes)"""
    client = MongoClient(MONGO_URL)
    yield client[DB_NAME]
    client.close()


@pytest.fixture(scope="function")
def api_session():
    """Requests session with cookies - fresh for each test"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data(mongo_client):
    """Cleanup test data before and after tests"""
    # Cleanup before
    mongo_client.users.delete_many({"email": {"$regex": f"^{TEST_EMAIL_PREFIX}"}})
    mongo_client.verification_codes.delete_many({"email": {"$regex": f"^{TEST_EMAIL_PREFIX}"}})
    yield
    # Cleanup after
    mongo_client.users.delete_many({"email": {"$regex": f"^{TEST_EMAIL_PREFIX}"}})
    mongo_client.verification_codes.delete_many({"email": {"$regex": f"^{TEST_EMAIL_PREFIX}"}})


class TestSendCode:
    """Tests for POST /api/auth/send-code endpoint"""
    
    def test_send_code_success(self, api_session, mongo_client):
        """Test sending verification code to a valid email"""
        test_email = f"{TEST_EMAIL_PREFIX}user1_{int(time.time())}@example.com"
        
        response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={
            "email": test_email,
            "lang": "de"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        assert data["email"] == test_email.lower()  # API lowercases email
        
        # Verify code was stored in DB
        code_doc = mongo_client.verification_codes.find_one({"email": test_email.lower()})
        assert code_doc is not None, "Verification code not found in DB"
        assert len(code_doc["code"]) == 6, "Code should be 6 digits"
        assert code_doc["used"] == False
        print(f"✓ send-code success: code {code_doc['code']} stored for {test_email}")
    
    def test_send_code_invalid_email(self, api_session):
        """Test sending code to invalid email format"""
        response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={
            "email": "invalid-email",
            "lang": "de"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ send-code rejects invalid email format")
    
    def test_send_code_blocks_admin(self, api_session):
        """Test that admin emails are blocked from passwordless login"""
        admin_email = "admin@truckonroad.ch"
        
        response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={
            "email": admin_email,
            "lang": "de"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "Admin" in data.get("detail", ""), f"Expected admin block message, got: {data}"
        print("✓ send-code blocks admin emails")
    
    def test_send_code_rate_limit(self, api_session, mongo_client):
        """Test rate limiting (max 3 codes per 10 minutes)"""
        # Use unique email for rate limit test
        test_email = f"{TEST_EMAIL_PREFIX}ratelimit_{int(time.time())}@example.com"
        
        # Send 3 codes (should succeed)
        for i in range(3):
            response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={
                "email": test_email,
                "lang": "de"
            })
            assert response.status_code == 200, f"Request {i+1} failed: {response.text}"
        
        # 4th request should be rate limited
        response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={
            "email": test_email,
            "lang": "de"
        })
        
        assert response.status_code == 429, f"Expected 429 rate limit, got {response.status_code}"
        print("✓ send-code rate limits after 3 requests")


class TestVerifyCode:
    """Tests for POST /api/auth/verify-code endpoint"""
    
    def test_verify_code_wrong_code(self, api_session, mongo_client):
        """Test verification with wrong code"""
        test_email = f"{TEST_EMAIL_PREFIX}wrongcode_{int(time.time())}@example.com"
        
        # First send a code
        api_session.post(f"{BASE_URL}/api/auth/send-code", json={"email": test_email})
        
        # Try to verify with wrong code
        response = api_session.post(f"{BASE_URL}/api/auth/verify-code", json={
            "email": test_email,
            "code": "000000"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "Falscher Code" in data.get("detail", "") or "Code" in data.get("detail", "")
        print("✓ verify-code rejects wrong code")
    
    def test_verify_code_expired(self, api_session, mongo_client):
        """Test verification with expired code"""
        test_email = f"{TEST_EMAIL_PREFIX}expired_{int(time.time())}@example.com"
        
        # Insert an expired code directly into DB
        expired_time = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        mongo_client.verification_codes.insert_one({
            "email": test_email,
            "code": "123456",
            "created_at": expired_time,
            "expires_at": expired_time,  # Already expired
            "used": False,
            "attempts": 0
        })
        
        response = api_session.post(f"{BASE_URL}/api/auth/verify-code", json={
            "email": test_email,
            "code": "123456"
        })
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        # Accept either "abgelaufen" (expired) or "kein gueltiger code" (no valid code) message
        detail = data.get("detail", "").lower()
        assert "abgelaufen" in detail or "code" in detail, f"Expected expiry/code error, got: {data}"
        print("✓ verify-code rejects expired code")
    
    def test_verify_code_success_new_user(self, api_session, mongo_client):
        """Test successful verification for new user (is_new=true)"""
        test_email = f"{TEST_EMAIL_PREFIX}newuser_{int(time.time())}@example.com"
        
        # Send code
        send_response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={"email": test_email})
        assert send_response.status_code == 200, f"Send code failed: {send_response.text}"
        
        # Get the code from DB (email is lowercased)
        code_doc = mongo_client.verification_codes.find_one(
            {"email": test_email.lower(), "used": False},
            sort=[("created_at", -1)]
        )
        assert code_doc is not None, f"Code not found in DB for {test_email.lower()}"
        
        # Verify with correct code
        response = api_session.post(f"{BASE_URL}/api/auth/verify-code", json={
            "email": test_email,
            "code": code_doc["code"]
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["is_new"] == True, f"Expected is_new=True for new user, got {data}"
        assert data["profile_complete"] == False, f"Expected profile_complete=False, got {data}"
        assert data["email"] == test_email.lower()
        assert data["role"] == "customer"
        
        # Verify user was created in DB
        user = mongo_client.users.find_one({"email": test_email.lower()})
        assert user is not None, "User not created in DB"
        assert user["email_verified"] == True
        assert user["profile_complete"] == False
        print(f"✓ verify-code success for new user: is_new={data['is_new']}, profile_complete={data['profile_complete']}")
    
    def test_verify_code_success_existing_user(self, api_session, mongo_client):
        """Test successful verification for existing user with complete profile"""
        test_email = f"{TEST_EMAIL_PREFIX}existinguser_{int(time.time())}@example.com"
        
        # Create existing user with complete profile
        mongo_client.users.insert_one({
            "email": test_email.lower(),
            "password_hash": "",
            "name": "Test User",
            "first_name": "Test",
            "last_name": "User",
            "street": "Test Street 1",
            "plz": "8000",
            "city": "Zurich",
            "mobile": "+41791234567",
            "company": "",
            "role": "customer",
            "profile_complete": True,
            "email_verified": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Send code
        send_response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={"email": test_email})
        assert send_response.status_code == 200, f"Send code failed: {send_response.text}"
        
        # Get the code from DB
        code_doc = mongo_client.verification_codes.find_one(
            {"email": test_email.lower(), "used": False},
            sort=[("created_at", -1)]
        )
        assert code_doc is not None, f"Code not found in DB for {test_email.lower()}"
        
        # Verify with correct code
        response = api_session.post(f"{BASE_URL}/api/auth/verify-code", json={
            "email": test_email,
            "code": code_doc["code"]
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["is_new"] == False, f"Expected is_new=False for existing user, got {data}"
        assert data["profile_complete"] == True, f"Expected profile_complete=True, got {data}"
        print(f"✓ verify-code success for existing user: is_new={data['is_new']}, profile_complete={data['profile_complete']}")


class TestCompleteProfile:
    """Tests for POST /api/auth/complete-profile endpoint"""
    
    def test_complete_profile_success(self, api_session, mongo_client):
        """Test completing profile for new user"""
        test_email = f"{TEST_EMAIL_PREFIX}completeprofile_{int(time.time())}@example.com"
        
        # Create new user via passwordless flow
        send_response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={"email": test_email})
        assert send_response.status_code == 200, f"Send code failed: {send_response.text}"
        
        code_doc = mongo_client.verification_codes.find_one(
            {"email": test_email.lower(), "used": False},
            sort=[("created_at", -1)]
        )
        assert code_doc is not None, f"Code not found in DB for {test_email.lower()}"
        
        # Verify code (this sets auth cookies)
        verify_response = api_session.post(f"{BASE_URL}/api/auth/verify-code", json={
            "email": test_email,
            "code": code_doc["code"]
        })
        assert verify_response.status_code == 200, f"Verify code failed: {verify_response.text}"
        
        # Complete profile
        profile_data = {
            "first_name": "Max",
            "last_name": "Muster",
            "street": "Bahnhofstrasse 75",
            "plz": "8620",
            "city": "Wetzikon",
            "mobile": "+41 79 123 45 67",
            "company": "Test Firma AG"
        }
        
        response = api_session.post(f"{BASE_URL}/api/auth/complete-profile", json=profile_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "Profil" in data.get("message", "") or "name" in data
        
        # Verify profile was saved in DB
        user = mongo_client.users.find_one({"email": test_email.lower()})
        assert user["first_name"] == "Max"
        assert user["last_name"] == "Muster"
        assert user["street"] == "Bahnhofstrasse 75"
        assert user["plz"] == "8620"
        assert user["city"] == "Wetzikon"
        assert user["mobile"] == "+41 79 123 45 67"
        assert user["company"] == "Test Firma AG"
        assert user["profile_complete"] == True
        assert user["name"] == "Max Muster"
        print("✓ complete-profile saves all fields correctly")
    
    def test_complete_profile_without_auth(self, mongo_client):
        """Test that complete-profile requires authentication"""
        # New session without auth cookies
        new_session = requests.Session()
        new_session.headers.update({"Content-Type": "application/json"})
        
        response = new_session.post(f"{BASE_URL}/api/auth/complete-profile", json={
            "first_name": "Test",
            "last_name": "User",
            "street": "Test Street",
            "plz": "1234",
            "city": "Test City",
            "mobile": "+41791234567"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ complete-profile requires authentication")


class TestCustomerProfile:
    """Tests for GET /api/customer/profile endpoint"""
    
    def test_get_profile_returns_all_fields(self, api_session, mongo_client):
        """Test that profile endpoint returns all new fields"""
        test_email = f"{TEST_EMAIL_PREFIX}profilefields_{int(time.time())}@example.com"
        
        # Create user with all fields
        mongo_client.users.insert_one({
            "email": test_email.lower(),
            "password_hash": "",
            "name": "Profile Test",
            "first_name": "Profile",
            "last_name": "Test",
            "street": "Profile Street 123",
            "plz": "9999",
            "city": "Profile City",
            "mobile": "+41 79 999 99 99",
            "phone": "+41 79 999 99 99",
            "company": "Profile Company",
            "role": "customer",
            "profile_complete": True,
            "email_verified": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Login via passwordless
        send_response = api_session.post(f"{BASE_URL}/api/auth/send-code", json={"email": test_email})
        assert send_response.status_code == 200, f"Send code failed: {send_response.text}"
        
        code_doc = mongo_client.verification_codes.find_one(
            {"email": test_email.lower(), "used": False},
            sort=[("created_at", -1)]
        )
        assert code_doc is not None, f"Code not found in DB for {test_email.lower()}"
        
        verify_response = api_session.post(f"{BASE_URL}/api/auth/verify-code", json={
            "email": test_email,
            "code": code_doc["code"]
        })
        assert verify_response.status_code == 200, f"Verify code failed: {verify_response.text}"
        
        # Get profile
        response = api_session.get(f"{BASE_URL}/api/customer/profile")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify all fields are returned
        assert data["email"] == test_email.lower()
        assert data["first_name"] == "Profile"
        assert data["last_name"] == "Test"
        assert data["street"] == "Profile Street 123"
        assert data["plz"] == "9999"
        assert data["city"] == "Profile City"
        assert data["mobile"] == "+41 79 999 99 99"
        assert data["company"] == "Profile Company"
        assert data["profile_complete"] == True
        assert data["email_verified"] == True
        print("✓ GET /customer/profile returns all new fields")


class TestAdminLoginStillWorks:
    """Test that admin login with password still works"""
    
    def test_admin_password_login(self):
        """Test admin can still login with password"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TrucksOnRoad2026!"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["role"] == "admin"
        assert data["email"] == "admin@truckonroad.ch"
        print("✓ Admin password login still works")
        
        # Logout
        session.post(f"{BASE_URL}/api/auth/logout")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
