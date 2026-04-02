"""
Test multi-language content for trucks and FAQs
Tests FR/IT translations for all trucks and FAQs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTrucksMultilingual:
    """Test trucks have FR/IT translations"""
    
    def test_burger_truck_has_french_fields(self):
        """Verify burger-truck has all French translation fields"""
        response = requests.get(f"{BASE_URL}/api/trucks/burger-truck")
        assert response.status_code == 200
        data = response.json()
        
        # Check French fields exist and are not empty
        assert data.get('name_fr'), "name_fr should exist"
        assert data.get('tagline_fr'), "tagline_fr should exist"
        assert data.get('description_fr'), "description_fr should exist"
        assert data.get('menu_fr'), "menu_fr should exist"
        assert data.get('suitable_for_fr'), "suitable_for_fr should exist"
        
        # Verify French content
        assert "invités" in data['tagline_fr'] or "jusqu" in data['tagline_fr'], "tagline_fr should be in French"
        assert "Notre" in data['description_fr'] or "conçu" in data['description_fr'], "description_fr should be in French"
        
    def test_burger_truck_has_italian_fields(self):
        """Verify burger-truck has all Italian translation fields"""
        response = requests.get(f"{BASE_URL}/api/trucks/burger-truck")
        assert response.status_code == 200
        data = response.json()
        
        # Check Italian fields exist and are not empty
        assert data.get('name_it'), "name_it should exist"
        assert data.get('tagline_it'), "tagline_it should exist"
        assert data.get('description_it'), "description_it should exist"
        assert data.get('menu_it'), "menu_it should exist"
        assert data.get('suitable_for_it'), "suitable_for_it should exist"
        
        # Verify Italian content
        assert "ospiti" in data['tagline_it'] or "fino" in data['tagline_it'], "tagline_it should be in Italian"
        assert "nostro" in data['description_it'] or "progettato" in data['description_it'], "description_it should be in Italian"
    
    def test_all_trucks_have_fr_it_fields(self):
        """Verify all 6 trucks have FR/IT translation fields"""
        response = requests.get(f"{BASE_URL}/api/trucks")
        assert response.status_code == 200
        trucks = response.json()
        
        assert len(trucks) == 6, f"Expected 6 trucks, got {len(trucks)}"
        
        for truck in trucks:
            slug = truck.get('slug', 'unknown')
            # Check French fields
            assert truck.get('name_fr'), f"{slug}: name_fr missing"
            assert truck.get('tagline_fr'), f"{slug}: tagline_fr missing"
            assert truck.get('description_fr'), f"{slug}: description_fr missing"
            assert truck.get('menu_fr'), f"{slug}: menu_fr missing"
            assert truck.get('suitable_for_fr'), f"{slug}: suitable_for_fr missing"
            
            # Check Italian fields
            assert truck.get('name_it'), f"{slug}: name_it missing"
            assert truck.get('tagline_it'), f"{slug}: tagline_it missing"
            assert truck.get('description_it'), f"{slug}: description_it missing"
            assert truck.get('menu_it'), f"{slug}: menu_it missing"
            assert truck.get('suitable_for_it'), f"{slug}: suitable_for_it missing"


class TestFAQsMultilingual:
    """Test FAQs have FR/IT translations"""
    
    def test_faqs_have_french_fields(self):
        """Verify all FAQs have French translation fields"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200
        faqs = response.json()
        
        assert len(faqs) == 8, f"Expected 8 FAQs, got {len(faqs)}"
        
        for i, faq in enumerate(faqs):
            assert faq.get('question_fr'), f"FAQ {i+1}: question_fr missing"
            assert faq.get('answer_fr'), f"FAQ {i+1}: answer_fr missing"
    
    def test_faqs_have_italian_fields(self):
        """Verify all FAQs have Italian translation fields"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200
        faqs = response.json()
        
        assert len(faqs) == 8, f"Expected 8 FAQs, got {len(faqs)}"
        
        for i, faq in enumerate(faqs):
            assert faq.get('question_it'), f"FAQ {i+1}: question_it missing"
            assert faq.get('answer_it'), f"FAQ {i+1}: answer_it missing"
    
    def test_faq_french_content_is_french(self):
        """Verify FAQ French content is actually in French"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200
        faqs = response.json()
        
        # Check first FAQ has French content
        first_faq = faqs[0]
        question_fr = first_faq.get('question_fr', '')
        answer_fr = first_faq.get('answer_fr', '')
        
        # French indicators
        french_words = ['de', 'la', 'le', 'les', 'un', 'une', 'nous', 'vous', 'pour', 'avec', 'dans', 'sur', 'est', 'sont', 'avance', 'réserver']
        has_french = any(word in question_fr.lower() or word in answer_fr.lower() for word in french_words)
        assert has_french, f"FAQ French content doesn't appear to be in French: {question_fr}"
    
    def test_faq_italian_content_is_italian(self):
        """Verify FAQ Italian content is actually in Italian"""
        response = requests.get(f"{BASE_URL}/api/faqs")
        assert response.status_code == 200
        faqs = response.json()
        
        # Check first FAQ has Italian content
        first_faq = faqs[0]
        question_it = first_faq.get('question_it', '')
        answer_it = first_faq.get('answer_it', '')
        
        # Italian indicators
        italian_words = ['di', 'il', 'la', 'le', 'un', 'una', 'noi', 'voi', 'per', 'con', 'in', 'su', 'è', 'sono', 'anticipo', 'prenotare']
        has_italian = any(word in question_it.lower() or word in answer_it.lower() for word in italian_words)
        assert has_italian, f"FAQ Italian content doesn't appear to be in Italian: {question_it}"


class TestExistingEndpoints:
    """Verify existing endpoints still work after multilingual update"""
    
    def test_auth_login_admin(self):
        """Test admin login still works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get('email') == "admin@truckonroad.ch"
        assert data.get('role') == "admin"
    
    def test_auth_login_customer(self):
        """Test customer login still works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test2@kunde.ch",
            "password": "Kunde2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get('email') == "test2@kunde.ch"
        assert data.get('role') == "customer"
    
    def test_admin_stats(self):
        """Test admin stats endpoint still works"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@truckonroad.ch",
            "password": "TruckOnRoad2026!"
        })
        cookies = login_response.cookies
        
        # Get stats
        response = requests.get(f"{BASE_URL}/api/admin/stats", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert 'total_inquiries' in data
        assert 'total_trucks' in data
        assert data['total_trucks'] == 6
    
    def test_customer_profile(self):
        """Test customer profile endpoint still works"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test2@kunde.ch",
            "password": "Kunde2026!"
        })
        cookies = login_response.cookies
        
        # Get profile
        response = requests.get(f"{BASE_URL}/api/customer/profile", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data.get('email') == "test2@kunde.ch"


class TestTruckDetailEndpoints:
    """Test individual truck detail endpoints"""
    
    def test_chicken_burger_truck_multilingual(self):
        """Test chicken-burger-truck has FR/IT fields"""
        response = requests.get(f"{BASE_URL}/api/trucks/chicken-burger-truck")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('tagline_fr') == "Croustillant · Épicé · Unique"
        assert data.get('tagline_it') == "Croccante · Piccante · Unico"
    
    def test_bowl_truck_multilingual(self):
        """Test bowl-truck has FR/IT fields"""
        response = requests.get(f"{BASE_URL}/api/trucks/bowl-truck")
        assert response.status_code == 200
        data = response.json()
        
        assert "Protéines" in data.get('tagline_fr', '')
        assert "Proteine" in data.get('tagline_it', '')
    
    def test_empanadas_truck_multilingual(self):
        """Test empanadas-truck has FR/IT fields"""
        response = requests.get(f"{BASE_URL}/api/trucks/empanadas-truck")
        assert response.status_code == 200
        data = response.json()
        
        assert "Végétarien" in data.get('tagline_fr', '')
        assert "Vegetariano" in data.get('tagline_it', '')
    
    def test_retro_trailer_multilingual(self):
        """Test retro-trailer has FR/IT fields"""
        response = requests.get(f"{BASE_URL}/api/trucks/retro-trailer")
        assert response.status_code == 200
        data = response.json()
        
        assert "Charme Vintage" in data.get('tagline_fr', '')
        assert "Fascino Vintage" in data.get('tagline_it', '')
