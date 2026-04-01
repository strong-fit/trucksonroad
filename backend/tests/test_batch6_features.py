"""
Test Batch 6 Features:
- Employee CRUD (create, read, update, delete)
- Export endpoints (CSV/PDF for inquiries, employees, calendar, trucks, faqs)
- Offer PDF generation
- Instagram gallery API
- Admin sidebar navigation (8 items)
- Employee assignment to inquiries
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication for admin endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return session
    
    def test_login_success(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@truckonroad.ch"
        assert data["role"] == "admin"
        print("✓ Admin login successful")


class TestEmployeeCRUD:
    """Employee management CRUD tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_create_employee(self, auth_session):
        """Test creating a new employee"""
        response = auth_session.post(f"{BASE_URL}/api/admin/employees", json={
            "name": "TEST_Max Mustermann",
            "phone": "+41 79 123 45 67",
            "role": "Koch",
            "notes": "Test employee",
            "is_active": True
        })
        assert response.status_code == 200, f"Create failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["message"] == "Created"
        print(f"✓ Employee created with ID: {data['id']}")
        return data["id"]
    
    def test_get_employees(self, auth_session):
        """Test getting all employees"""
        response = auth_session.get(f"{BASE_URL}/api/admin/employees")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} employees")
    
    def test_update_employee(self, auth_session):
        """Test updating an employee"""
        # First create an employee
        create_resp = auth_session.post(f"{BASE_URL}/api/admin/employees", json={
            "name": "TEST_Update Employee",
            "phone": "+41 79 111 22 33",
            "role": "Service"
        })
        assert create_resp.status_code == 200
        emp_id = create_resp.json()["id"]
        
        # Update the employee
        update_resp = auth_session.put(f"{BASE_URL}/api/admin/employees/{emp_id}", json={
            "name": "TEST_Updated Name",
            "phone": "+41 79 999 88 77",
            "role": "Fahrer",
            "is_active": False
        })
        assert update_resp.status_code == 200
        assert update_resp.json()["message"] == "Updated"
        
        # Verify update
        get_resp = auth_session.get(f"{BASE_URL}/api/admin/employees")
        employees = get_resp.json()
        updated_emp = next((e for e in employees if e["id"] == emp_id), None)
        assert updated_emp is not None
        assert updated_emp["name"] == "TEST_Updated Name"
        assert updated_emp["role"] == "Fahrer"
        print(f"✓ Employee {emp_id} updated successfully")
        
        # Cleanup
        auth_session.delete(f"{BASE_URL}/api/admin/employees/{emp_id}")
    
    def test_delete_employee(self, auth_session):
        """Test deleting an employee"""
        # Create employee to delete
        create_resp = auth_session.post(f"{BASE_URL}/api/admin/employees", json={
            "name": "TEST_Delete Employee",
            "phone": "+41 79 000 00 00",
            "role": "Test"
        })
        assert create_resp.status_code == 200
        emp_id = create_resp.json()["id"]
        
        # Delete the employee
        delete_resp = auth_session.delete(f"{BASE_URL}/api/admin/employees/{emp_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json()["message"] == "Deleted"
        
        # Verify deletion
        get_resp = auth_session.get(f"{BASE_URL}/api/admin/employees")
        employees = get_resp.json()
        deleted_emp = next((e for e in employees if e["id"] == emp_id), None)
        assert deleted_emp is None
        print(f"✓ Employee {emp_id} deleted successfully")


class TestExportEndpoints:
    """Export CSV/PDF endpoints tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_export_inquiries_csv(self, auth_session):
        """Test exporting inquiries as CSV"""
        response = auth_session.get(f"{BASE_URL}/api/admin/export/inquiries?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "attachment" in response.headers.get("content-disposition", "")
        assert "inquiries_export.csv" in response.headers.get("content-disposition", "")
        print("✓ Inquiries CSV export successful")
    
    def test_export_inquiries_pdf(self, auth_session):
        """Test exporting inquiries as PDF"""
        response = auth_session.get(f"{BASE_URL}/api/admin/export/inquiries?format=pdf")
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("content-type", "")
        assert response.content[:4] == b'%PDF'  # PDF magic bytes
        print("✓ Inquiries PDF export successful")
    
    def test_export_employees_csv(self, auth_session):
        """Test exporting employees as CSV"""
        response = auth_session.get(f"{BASE_URL}/api/admin/export/employees?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        print("✓ Employees CSV export successful")
    
    def test_export_employees_pdf(self, auth_session):
        """Test exporting employees as PDF"""
        response = auth_session.get(f"{BASE_URL}/api/admin/export/employees?format=pdf")
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("content-type", "")
        assert response.content[:4] == b'%PDF'
        print("✓ Employees PDF export successful")
    
    def test_export_calendar_csv(self, auth_session):
        """Test exporting calendar as CSV"""
        response = auth_session.get(f"{BASE_URL}/api/admin/export/calendar?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        print("✓ Calendar CSV export successful")
    
    def test_export_trucks_csv(self, auth_session):
        """Test exporting trucks as CSV"""
        response = auth_session.get(f"{BASE_URL}/api/admin/export/trucks?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        print("✓ Trucks CSV export successful")
    
    def test_export_faqs_csv(self, auth_session):
        """Test exporting FAQs as CSV"""
        response = auth_session.get(f"{BASE_URL}/api/admin/export/faqs?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        print("✓ FAQs CSV export successful")
    
    def test_export_invalid_type(self, auth_session):
        """Test exporting invalid data type"""
        response = auth_session.get(f"{BASE_URL}/api/admin/export/invalid?format=csv")
        assert response.status_code == 400
        print("✓ Invalid export type returns 400")


class TestOfferPDF:
    """Offer PDF generation tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_offer_pdf_generation(self, auth_session):
        """Test generating offer PDF for an inquiry"""
        # First create an inquiry
        inquiry_resp = requests.post(f"{BASE_URL}/api/inquiries", json={
            "first_name": "TEST_PDF",
            "last_name": "Generator",
            "email": "test@example.com",
            "phone": "+41 79 123 45 67",
            "event_date": "2026-06-15",
            "location": "Zürich",
            "guest_count": 100,
            "event_type": "Firmenanlass",
            "selected_trucks": ["Burger Truck", "Bowl Truck"]
        })
        assert inquiry_resp.status_code == 200
        inquiry_id = inquiry_resp.json()["id"]
        
        # Generate offer PDF
        pdf_resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}/offer-pdf")
        assert pdf_resp.status_code == 200
        assert "application/pdf" in pdf_resp.headers.get("content-type", "")
        assert pdf_resp.content[:4] == b'%PDF'
        assert "Angebot_TEST_PDF_Generator.pdf" in pdf_resp.headers.get("content-disposition", "")
        print(f"✓ Offer PDF generated for inquiry {inquiry_id}")
        
        # Cleanup
        auth_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
    
    def test_offer_pdf_not_found(self, auth_session):
        """Test offer PDF for non-existent inquiry"""
        response = auth_session.get(f"{BASE_URL}/api/admin/inquiries/nonexistent-id/offer-pdf")
        assert response.status_code == 404
        print("✓ Non-existent inquiry returns 404")


class TestStatusChangeOfferEmail:
    """Test that status change to 'offer_sent' triggers email"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_status_change_to_offer_sent(self, auth_session):
        """Test changing status to offer_sent"""
        # Create inquiry
        inquiry_resp = requests.post(f"{BASE_URL}/api/inquiries", json={
            "first_name": "TEST_Offer",
            "last_name": "Email",
            "email": "test-offer@example.com",
            "phone": "+41 79 111 22 33",
            "event_date": "2026-07-20",
            "location": "Bern",
            "guest_count": 150,
            "event_type": "Festival"
        })
        assert inquiry_resp.status_code == 200
        inquiry_id = inquiry_resp.json()["id"]
        
        # Change status to offer_sent
        update_resp = auth_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}", json={
            "status": "offer_sent",
            "internal_notes": "Test offer sent"
        })
        assert update_resp.status_code == 200
        assert update_resp.json()["message"] == "Updated"
        print(f"✓ Status changed to offer_sent for inquiry {inquiry_id}")
        # Note: Email sending is logged in backend (SMTP not configured)
        
        # Cleanup
        auth_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")


class TestEmployeeAssignment:
    """Test employee assignment to inquiries"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_assign_employees_to_inquiry(self, auth_session):
        """Test assigning employees to an inquiry"""
        # Create employee
        emp_resp = auth_session.post(f"{BASE_URL}/api/admin/employees", json={
            "name": "TEST_Assignment Employee",
            "role": "Koch"
        })
        assert emp_resp.status_code == 200
        emp_id = emp_resp.json()["id"]
        
        # Create inquiry
        inquiry_resp = requests.post(f"{BASE_URL}/api/inquiries", json={
            "first_name": "TEST_Assignment",
            "last_name": "Test",
            "email": "assign@example.com",
            "phone": "+41 79 222 33 44",
            "event_date": "2026-08-10",
            "location": "Basel",
            "guest_count": 80,
            "event_type": "Private Event"
        })
        assert inquiry_resp.status_code == 200
        inquiry_id = inquiry_resp.json()["id"]
        
        # Assign employee to inquiry
        assign_resp = auth_session.put(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}", json={
            "status": "in_review",
            "internal_notes": "Assigned employee",
            "assigned_employees": ["TEST_Assignment Employee"]
        })
        assert assign_resp.status_code == 200
        
        # Verify assignment
        get_resp = auth_session.get(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        assert get_resp.status_code == 200
        inquiry_data = get_resp.json()
        assert "assigned_employees" in inquiry_data
        assert "TEST_Assignment Employee" in inquiry_data["assigned_employees"]
        print(f"✓ Employee assigned to inquiry {inquiry_id}")
        
        # Cleanup
        auth_session.delete(f"{BASE_URL}/api/admin/inquiries/{inquiry_id}")
        auth_session.delete(f"{BASE_URL}/api/admin/employees/{emp_id}")


class TestInstagramGallery:
    """Instagram gallery API tests"""
    
    def test_instagram_gallery_public(self):
        """Test public Instagram gallery endpoint"""
        response = requests.get(f"{BASE_URL}/api/instagram-gallery")
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "images" in data
        assert isinstance(data["images"], list)
        print(f"✓ Instagram gallery API returns username: '{data['username']}', images: {len(data['images'])}")
    
    def test_instagram_settings_update(self):
        """Test updating Instagram settings"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert login_resp.status_code == 200
        
        # Get current settings
        settings_resp = session.get(f"{BASE_URL}/api/admin/settings")
        assert settings_resp.status_code == 200
        settings = settings_resp.json()
        
        # Update Instagram settings
        settings["instagram_username"] = "truckonroad_test"
        settings["instagram_images"] = [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg"
        ]
        
        update_resp = session.put(f"{BASE_URL}/api/admin/settings", json=settings)
        assert update_resp.status_code == 200
        
        # Verify via public endpoint
        gallery_resp = requests.get(f"{BASE_URL}/api/instagram-gallery")
        assert gallery_resp.status_code == 200
        gallery_data = gallery_resp.json()
        assert gallery_data["username"] == "truckonroad_test"
        assert len(gallery_data["images"]) == 2
        print("✓ Instagram settings updated and verified")
        
        # Reset settings
        settings["instagram_username"] = ""
        settings["instagram_images"] = []
        session.put(f"{BASE_URL}/api/admin/settings", json=settings)


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_cleanup_test_employees(self, auth_session):
        """Clean up TEST_ prefixed employees"""
        response = auth_session.get(f"{BASE_URL}/api/admin/employees")
        if response.status_code == 200:
            employees = response.json()
            for emp in employees:
                if emp.get("name", "").startswith("TEST_"):
                    auth_session.delete(f"{BASE_URL}/api/admin/employees/{emp['id']}")
                    print(f"  Cleaned up employee: {emp['name']}")
        print("✓ Test employees cleaned up")
    
    def test_cleanup_test_inquiries(self, auth_session):
        """Clean up TEST_ prefixed inquiries"""
        response = auth_session.get(f"{BASE_URL}/api/admin/inquiries")
        if response.status_code == 200:
            inquiries = response.json()
            for inq in inquiries:
                if inq.get("first_name", "").startswith("TEST_"):
                    auth_session.delete(f"{BASE_URL}/api/admin/inquiries/{inq['id']}")
                    print(f"  Cleaned up inquiry: {inq['first_name']}")
        print("✓ Test inquiries cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
