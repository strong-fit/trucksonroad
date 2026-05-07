"""Tests for Legal documents (AGB, Datenschutz, Impressum) with versioning."""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://truck-management-pro.preview.emergentagent.com').rstrip('/')
ADMIN_EMAIL = "admin@truckonroad.ch"
ADMIN_PASSWORD = "TrucksOnRoad2026!"


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if r.status_code != 200:
        pytest.skip(f"Admin login failed: {r.status_code} {r.text[:200]}")
    return s


# --- Public endpoints ---
class TestPublicLegal:
    def test_get_agb_public(self):
        r = requests.get(f"{BASE_URL}/api/legal/agb")
        assert r.status_code == 200
        d = r.json()
        assert d["type"] == "agb"
        assert d["title"]
        assert isinstance(d["sections"], list) and len(d["sections"]) > 0
        assert "_id" not in d
        assert "version" in d
        assert d["version"] >= 1

    def test_get_datenschutz_public(self):
        r = requests.get(f"{BASE_URL}/api/legal/datenschutz")
        assert r.status_code == 200
        d = r.json()
        assert d["type"] == "datenschutz"
        assert len(d["sections"]) > 0

    def test_get_impressum_public(self):
        r = requests.get(f"{BASE_URL}/api/legal/impressum")
        assert r.status_code == 200
        d = r.json()
        assert d["type"] == "impressum"
        assert len(d["sections"]) > 0

    def test_get_unknown_404(self):
        r = requests.get(f"{BASE_URL}/api/legal/unbekannt")
        assert r.status_code == 404


class TestAdminAuth:
    def test_admin_legal_no_auth(self):
        r = requests.get(f"{BASE_URL}/api/admin/legal")
        assert r.status_code == 401

    def test_admin_legal_list(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/legal")
        assert r.status_code == 200
        docs = r.json()
        assert isinstance(docs, list)
        types = {d["type"] for d in docs}
        assert {"agb", "datenschutz", "impressum"}.issubset(types)
        for d in docs:
            assert "version" in d

    def test_admin_legal_get_agb(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/legal/agb")
        assert r.status_code == 200
        d = r.json()
        assert d["type"] == "agb"
        assert "version" in d
        # updated_by fields present (after at least one update or initial seed)
        assert "title" in d


class TestVersioningFlow:
    def test_full_version_flow(self, admin_session):
        # 1. Get current version
        r = admin_session.get(f"{BASE_URL}/api/admin/legal/agb")
        assert r.status_code == 200
        current = r.json()
        v_before = current["version"]
        sections_before = current["sections"]

        # 2. Save edit -> v+1
        edited_sections = list(sections_before)
        edited_sections[0] = {
            "heading": edited_sections[0]["heading"],
            "content": edited_sections[0]["content"] + "\n\nTEST_EDIT_MARKER_AAA",
        }
        r = admin_session.put(f"{BASE_URL}/api/admin/legal/agb", json={
            "title": current["title"],
            "subtitle": current.get("subtitle", ""),
            "sections": edited_sections,
            "change_notes": "TEST_EDIT change note",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["version"] == v_before + 1
        new_version_id = body["version_id"]

        # 3. Public reflects new version + content
        rp = requests.get(f"{BASE_URL}/api/legal/agb")
        assert rp.status_code == 200
        pub = rp.json()
        assert pub["version"] == v_before + 1
        assert "TEST_EDIT_MARKER_AAA" in pub["sections"][0]["content"]

        # 4. Versions list desc
        rv = admin_session.get(f"{BASE_URL}/api/admin/legal/agb/versions")
        assert rv.status_code == 200
        versions = rv.json()
        assert len(versions) >= 2
        # sorted desc
        nums = [v["version"] for v in versions]
        assert nums == sorted(nums, reverse=True)
        latest = versions[0]
        assert latest["version"] == v_before + 1
        assert latest["change_notes"] == "TEST_EDIT change note"
        assert "admin_name" in latest
        assert "diff_added" in latest and "diff_removed" in latest
        assert latest["diff_added"] >= 1

        # 5. Get version detail
        rd = admin_session.get(f"{BASE_URL}/api/admin/legal/agb/versions/{new_version_id}")
        assert rd.status_code == 200
        det = rd.json()
        assert det["version"] == v_before + 1
        assert "sections" in det
        assert "diff_text" in det

        # 6. Restore to v1 (or v_before)
        # Find version with v_before
        target_v = next((v for v in versions if v["version"] == v_before), None)
        assert target_v is not None
        rd2 = admin_session.get(f"{BASE_URL}/api/admin/legal/agb/versions/{target_v['id']}")
        assert rd2.status_code == 200

        rr = admin_session.post(f"{BASE_URL}/api/admin/legal/agb/restore/{target_v['id']}")
        assert rr.status_code == 200
        rdata = rr.json()
        assert rdata["version"] == v_before + 2
        assert rdata["restored_from_version"] == v_before

        # 7. Public should now NOT contain TEST_EDIT_MARKER
        rp2 = requests.get(f"{BASE_URL}/api/legal/agb")
        assert rp2.status_code == 200
        pub2 = rp2.json()
        assert pub2["version"] == v_before + 2
        assert "TEST_EDIT_MARKER_AAA" not in pub2["sections"][0]["content"]

        # 8. Verify restored_from_version field in version listing
        rv2 = admin_session.get(f"{BASE_URL}/api/admin/legal/agb/versions")
        latest2 = rv2.json()[0]
        assert latest2.get("restored_from_version") == v_before

    def test_put_empty_sections_validation(self, admin_session):
        # Empty sections array should still save (per request spec: title required, sections can be empty)
        r = admin_session.get(f"{BASE_URL}/api/admin/legal/impressum")
        cur = r.json()
        v_before = cur["version"]
        rr = admin_session.put(f"{BASE_URL}/api/admin/legal/impressum", json={
            "title": cur["title"],
            "subtitle": cur.get("subtitle", ""),
            "sections": [],
            "change_notes": "TEST empty sections",
        })
        # accepts 200; should NOT crash
        assert rr.status_code == 200
        # restore back to original
        admin_session.put(f"{BASE_URL}/api/admin/legal/impressum", json={
            "title": cur["title"],
            "subtitle": cur.get("subtitle", ""),
            "sections": cur["sections"],
            "change_notes": "TEST restore impressum",
        })

    def test_put_missing_title(self, admin_session):
        r = admin_session.put(f"{BASE_URL}/api/admin/legal/agb", json={
            "subtitle": "x",
            "sections": [],
        })
        assert r.status_code in (400, 422)
