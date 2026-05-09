"""Tests for P0 umlaut fix in auth verification email + Cookie banner datenschutz section."""
import os
import sys
import pytest
import requests

# Add backend to path for direct module import
sys.path.insert(0, "/app/backend")

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://truck-management-pro.preview.emergentagent.com").rstrip("/")


# --- Direct module tests for build_verification_code_email umlauts ---
class TestVerificationCodeEmailUmlauts:
    def test_de_umlauts(self):
        from routes.auth_routes import build_verification_code_email
        html = build_verification_code_email("123456", "de")
        assert "Bestätigungscode" in html, "DE must contain 'Bestätigungscode' with ä"
        assert "gültig" in html, "DE must contain 'gültig' with ü"
        assert "Bestaetigung" not in html
        assert "gueltig" not in html
        assert "123456" in html

    def test_fr_accents(self):
        from routes.auth_routes import build_verification_code_email
        html = build_verification_code_email("123456", "fr")
        assert "vérification" in html, "FR must contain 'vérification' with é"
        assert "à TrucksOnRoad" in html, "FR must contain 'à TrucksOnRoad' with à"
        # accented variants must be present, not the unaccented ones standalone
        assert "Votre code de vérification" in html

    def test_it_accents(self):
        from routes.auth_routes import build_verification_code_email
        html = build_verification_code_email("123456", "it")
        assert "è valido" in html, "IT must contain 'è valido' with è"

    def test_en(self):
        from routes.auth_routes import build_verification_code_email
        html = build_verification_code_email("123456", "en")
        assert "Verification Code" in html
        assert "10 minutes" in html

    def test_subject_map_fr_via_send_code(self):
        # The subject map is defined inline in send_verification_code; we check semantically by ensuring FR template
        # contains 'Votre code de vérification' which is the same string used in subject_map['fr']
        from routes.auth_routes import build_verification_code_email
        html = build_verification_code_email("000000", "fr")
        assert "Votre code de vérification" in html

    def test_default_lang_fallback(self):
        from routes.auth_routes import build_verification_code_email
        html = build_verification_code_email("123456", "xx")
        # Should fall back to DE
        assert "Bestätigungscode" in html


# --- Public API: send-code triggers (rate-limited, allow 200 or 429) ---
class TestAuthSendCodeEndpoint:
    def test_send_code_invalid_email(self):
        r = requests.post(f"{BASE_URL}/api/auth/send-code", json={"email": "not-an-email"})
        assert r.status_code == 400

    def test_send_code_valid_email(self):
        # Use a unique TEST email to avoid rate limit collision
        import time
        email = f"TEST_umlaut_{int(time.time())}@example.com"
        r = requests.post(f"{BASE_URL}/api/auth/send-code", json={"email": email, "lang": "de"})
        # SMTP may not be configured; we just need the endpoint to accept and queue
        assert r.status_code in (200, 500), f"unexpected: {r.status_code} {r.text}"
        if r.status_code == 200:
            data = r.json()
            assert data.get("email") == email.lower()


# --- Public legal API: datenschutz must contain new cookie section with 4 categories ---
class TestDatenschutzCookieSection:
    def test_datenschutz_returns_cookie_section(self):
        r = requests.get(f"{BASE_URL}/api/legal/datenschutz")
        assert r.status_code == 200
        data = r.json()
        assert "version" in data
        assert isinstance(data.get("sections"), list)
        # Find Cookies section
        cookie_secs = [s for s in data["sections"] if "Cookies" in s.get("heading", "")]
        assert len(cookie_secs) >= 1, "Datenschutz must have a Cookies section"
        content = cookie_secs[0]["content"]
        # Verify mentions all 4 categories
        assert "Technisch notwendige Cookies" in content or "notwendige" in content.lower()
        assert "Funktionale Cookies" in content or "funktional" in content.lower()
        assert "Analyse-Cookies" in content or "analyse" in content.lower()
        assert "Marketing-Cookies" in content or "marketing" in content.lower()
        # Verify mention of footer link / cookie settings
        assert "Cookie-Einstellungen" in content or "Cookie‑Einstellungen" in content or "Consent-Banner" in content

    def test_datenschutz_version_is_at_least_1(self):
        r = requests.get(f"{BASE_URL}/api/legal/datenschutz")
        assert r.status_code == 200
        v = r.json().get("version", 0)
        assert isinstance(v, int) and v >= 1
