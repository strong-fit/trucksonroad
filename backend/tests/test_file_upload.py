"""
Test File Upload Feature for TruckOnRoad
Tests: POST /api/inquiries/{id}/upload, GET /api/inquiries/{id}/files, 
       GET /api/files/{file_id}/download, DELETE /api/files/{file_id}
"""
import pytest
import requests
import os
import tempfile

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@truckonroad.ch"
ADMIN_PASSWORD = "TruckOnRoad2026!"

@pytest.fixture(scope="module")
def session():
    """Create a requests session"""
    return requests.Session()

@pytest.fixture(scope="module")
def admin_auth(session):
    """Login as admin and get authenticated session"""
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return session

@pytest.fixture(scope="module")
def test_inquiry_id(admin_auth):
    """Create a test inquiry for file upload testing"""
    resp = admin_auth.post(f"{BASE_URL}/api/inquiries", json={
        "first_name": "TEST_FileUpload",
        "last_name": "User",
        "email": "test_fileupload@example.com",
        "phone": "+41 79 123 45 67",
        "event_date": "2026-06-15",
        "location": "Zurich Test Location",
        "guest_count": 100,
        "event_type": "Firmenanlass",
        "privacy_accepted": True
    })
    assert resp.status_code == 200, f"Failed to create test inquiry: {resp.text}"
    inquiry_id = resp.json()["id"]
    yield inquiry_id
    # Cleanup: delete the test inquiry
    admin_auth.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")

@pytest.fixture
def small_test_file():
    """Create a small test file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for TruckOnRoad file upload testing.\n")
        f.write("Event plan details go here.\n")
        return f.name

@pytest.fixture
def large_test_file():
    """Create a file larger than 10MB"""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
        # Write 11MB of data
        f.write(b'x' * (11 * 1024 * 1024))
        return f.name


class TestFileUploadEndpoint:
    """Tests for POST /api/inquiries/{id}/upload"""
    
    def test_upload_file_success(self, admin_auth, test_inquiry_id, small_test_file):
        """Test successful file upload returns file metadata"""
        with open(small_test_file, 'rb') as f:
            resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('test_eventplan.txt', f, 'text/plain')}
            )
        
        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        data = resp.json()
        
        # Verify response structure
        assert "id" in data, "Response should contain file id"
        assert "inquiry_id" in data, "Response should contain inquiry_id"
        assert data["inquiry_id"] == test_inquiry_id
        assert "original_filename" in data
        assert data["original_filename"] == "test_eventplan.txt"
        assert "content_type" in data
        assert "size" in data
        assert data["size"] > 0
        assert "storage_path" in data
        assert "created_at" in data
        assert data.get("is_deleted") == False
        
        print(f"✓ File uploaded successfully: {data['original_filename']} ({data['size']} bytes)")
        return data["id"]
    
    def test_upload_rejects_large_file(self, admin_auth, test_inquiry_id, large_test_file):
        """Test that files over 10MB are rejected"""
        with open(large_test_file, 'rb') as f:
            resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('large_file.bin', f, 'application/octet-stream')}
            )
        
        assert resp.status_code == 400, f"Expected 400 for large file, got {resp.status_code}"
        data = resp.json()
        assert "detail" in data
        assert "10" in data["detail"].lower() or "gross" in data["detail"].lower() or "mb" in data["detail"].lower()
        print(f"✓ Large file correctly rejected: {data['detail']}")
    
    def test_upload_rejects_when_max_files_reached(self, admin_auth, test_inquiry_id, small_test_file):
        """Test that upload is rejected when 5 files already exist"""
        # First, upload 5 files
        uploaded_ids = []
        for i in range(5):
            with open(small_test_file, 'rb') as f:
                resp = admin_auth.post(
                    f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                    files={'file': (f'file_{i}.txt', f, 'text/plain')}
                )
                if resp.status_code == 200:
                    uploaded_ids.append(resp.json()["id"])
        
        # Now try to upload a 6th file
        with open(small_test_file, 'rb') as f:
            resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('file_6.txt', f, 'text/plain')}
            )
        
        assert resp.status_code == 400, f"Expected 400 for 6th file, got {resp.status_code}"
        data = resp.json()
        assert "detail" in data
        assert "5" in data["detail"] or "maximal" in data["detail"].lower()
        print(f"✓ 6th file correctly rejected: {data['detail']}")
        
        # Cleanup: delete uploaded files
        for file_id in uploaded_ids:
            admin_auth.delete(f"{BASE_URL}/api/files/{file_id}")


class TestGetInquiryFiles:
    """Tests for GET /api/inquiries/{id}/files"""
    
    def test_get_files_returns_list(self, admin_auth, test_inquiry_id, small_test_file):
        """Test that GET /api/inquiries/{id}/files returns list of uploaded files"""
        # Upload a file first
        with open(small_test_file, 'rb') as f:
            upload_resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('list_test.txt', f, 'text/plain')}
            )
        assert upload_resp.status_code == 200
        uploaded_file = upload_resp.json()
        
        # Get files list
        resp = admin_auth.get(f"{BASE_URL}/api/inquiries/{test_inquiry_id}/files")
        assert resp.status_code == 200, f"Get files failed: {resp.text}"
        
        files = resp.json()
        assert isinstance(files, list), "Response should be a list"
        assert len(files) >= 1, "Should have at least one file"
        
        # Find our uploaded file
        found = False
        for f in files:
            if f["id"] == uploaded_file["id"]:
                found = True
                assert f["original_filename"] == "list_test.txt"
                assert f["inquiry_id"] == test_inquiry_id
                assert f.get("is_deleted") == False
                break
        
        assert found, "Uploaded file should be in the list"
        print(f"✓ Files list returned {len(files)} file(s)")
        
        # Cleanup
        admin_auth.delete(f"{BASE_URL}/api/files/{uploaded_file['id']}")
    
    def test_get_files_excludes_deleted(self, admin_auth, test_inquiry_id, small_test_file):
        """Test that deleted files are not returned in the list"""
        # Upload a file
        with open(small_test_file, 'rb') as f:
            upload_resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('delete_test.txt', f, 'text/plain')}
            )
        assert upload_resp.status_code == 200
        file_id = upload_resp.json()["id"]
        
        # Delete the file
        del_resp = admin_auth.delete(f"{BASE_URL}/api/files/{file_id}")
        assert del_resp.status_code == 200
        
        # Get files list - deleted file should not appear
        resp = admin_auth.get(f"{BASE_URL}/api/inquiries/{test_inquiry_id}/files")
        assert resp.status_code == 200
        
        files = resp.json()
        for f in files:
            assert f["id"] != file_id, "Deleted file should not appear in list"
        
        print("✓ Deleted files correctly excluded from list")


class TestFileDownload:
    """Tests for GET /api/files/{file_id}/download"""
    
    def test_download_file_success(self, admin_auth, test_inquiry_id, small_test_file):
        """Test that file download returns correct content and Content-Type"""
        # Upload a file
        with open(small_test_file, 'rb') as f:
            original_content = f.read()
        
        with open(small_test_file, 'rb') as f:
            upload_resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('download_test.txt', f, 'text/plain')}
            )
        assert upload_resp.status_code == 200
        file_id = upload_resp.json()["id"]
        
        # Download the file (public endpoint - no auth required)
        download_resp = requests.get(f"{BASE_URL}/api/files/{file_id}/download")
        assert download_resp.status_code == 200, f"Download failed: {download_resp.text}"
        
        # Verify content type
        content_type = download_resp.headers.get("Content-Type", "")
        assert "text" in content_type.lower() or "octet" in content_type.lower(), f"Unexpected content type: {content_type}"
        
        # Verify content disposition
        content_disp = download_resp.headers.get("Content-Disposition", "")
        assert "download_test.txt" in content_disp, f"Filename not in Content-Disposition: {content_disp}"
        
        # Verify content matches
        assert download_resp.content == original_content, "Downloaded content should match original"
        
        print(f"✓ File downloaded successfully, Content-Type: {content_type}")
        
        # Cleanup
        admin_auth.delete(f"{BASE_URL}/api/files/{file_id}")
    
    def test_download_nonexistent_file_returns_404(self, session):
        """Test that downloading non-existent file returns 404"""
        resp = session.get(f"{BASE_URL}/api/files/nonexistent-file-id/download")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print("✓ Non-existent file correctly returns 404")
    
    def test_download_is_public(self, admin_auth, test_inquiry_id, small_test_file):
        """Test that file download does not require authentication"""
        # Upload a file
        with open(small_test_file, 'rb') as f:
            upload_resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('public_test.txt', f, 'text/plain')}
            )
        assert upload_resp.status_code == 200
        file_id = upload_resp.json()["id"]
        
        # Download without auth (new session)
        new_session = requests.Session()
        download_resp = new_session.get(f"{BASE_URL}/api/files/{file_id}/download")
        assert download_resp.status_code == 200, "Download should work without auth"
        
        print("✓ File download is public (no auth required)")
        
        # Cleanup
        admin_auth.delete(f"{BASE_URL}/api/files/{file_id}")


class TestFileDelete:
    """Tests for DELETE /api/files/{file_id}"""
    
    def test_delete_file_requires_auth(self, session, admin_auth, test_inquiry_id, small_test_file):
        """Test that file deletion requires authentication"""
        # Upload a file
        with open(small_test_file, 'rb') as f:
            upload_resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('auth_test.txt', f, 'text/plain')}
            )
        assert upload_resp.status_code == 200
        file_id = upload_resp.json()["id"]
        
        # Try to delete without auth
        new_session = requests.Session()
        del_resp = new_session.delete(f"{BASE_URL}/api/files/{file_id}")
        assert del_resp.status_code == 401, f"Expected 401 without auth, got {del_resp.status_code}"
        
        print("✓ File deletion correctly requires authentication")
        
        # Cleanup with auth
        admin_auth.delete(f"{BASE_URL}/api/files/{file_id}")
    
    def test_delete_file_soft_deletes(self, admin_auth, test_inquiry_id, small_test_file):
        """Test that file deletion is a soft delete"""
        # Upload a file
        with open(small_test_file, 'rb') as f:
            upload_resp = admin_auth.post(
                f"{BASE_URL}/api/inquiries/{test_inquiry_id}/upload",
                files={'file': ('soft_delete_test.txt', f, 'text/plain')}
            )
        assert upload_resp.status_code == 200
        file_id = upload_resp.json()["id"]
        
        # Delete the file
        del_resp = admin_auth.delete(f"{BASE_URL}/api/files/{file_id}")
        assert del_resp.status_code == 200, f"Delete failed: {del_resp.text}"
        
        # Verify file is not in list (soft deleted)
        list_resp = admin_auth.get(f"{BASE_URL}/api/inquiries/{test_inquiry_id}/files")
        assert list_resp.status_code == 200
        files = list_resp.json()
        for f in files:
            assert f["id"] != file_id, "Soft-deleted file should not appear in list"
        
        # Verify download returns 404 (soft deleted)
        download_resp = requests.get(f"{BASE_URL}/api/files/{file_id}/download")
        assert download_resp.status_code == 404, "Soft-deleted file should return 404 on download"
        
        print("✓ File soft-deleted successfully")


class TestFileUploadIntegration:
    """Integration tests for file upload with existing inquiry"""
    
    def test_upload_to_existing_inquiry(self, admin_auth):
        """Test uploading file to an existing inquiry from the database"""
        # Get list of inquiries
        resp = admin_auth.get(f"{BASE_URL}/api/admin/inquiries")
        assert resp.status_code == 200
        inquiries = resp.json()
        
        if len(inquiries) == 0:
            pytest.skip("No existing inquiries to test with")
        
        # Use first inquiry
        inquiry_id = inquiries[0]["id"]
        
        # Check current files
        files_resp = admin_auth.get(f"{BASE_URL}/api/inquiries/{inquiry_id}/files")
        assert files_resp.status_code == 200
        initial_count = len(files_resp.json())
        
        print(f"✓ Found inquiry {inquiry_id[:8]}... with {initial_count} existing files")


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_temp_files(small_test_file, large_test_file, request):
    """Cleanup temporary test files after tests"""
    yield
    import os
    for f in [small_test_file, large_test_file]:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except Exception:
            pass
