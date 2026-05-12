"""Backend tests for TRUCKSonROAD admin DB backup endpoints (local + Infomaniak S3)."""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://truck-management-pro.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@truckonroad.ch"
ADMIN_PASSWORD = "TrucksOnRoad2026!"


@pytest.fixture(scope="module")
def auth_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return s


# ---------- AUTH GUARD ----------
def test_list_backups_unauthorized():
    r = requests.get(f"{BASE_URL}/api/admin/backups", timeout=15)
    assert r.status_code in (401, 403), f"expected 401/403, got {r.status_code}"


# ---------- LIST + CONFIG ----------
def test_list_backups_ok(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/admin/backups", timeout=20)
    assert r.status_code == 200
    data = r.json()
    assert "backups" in data and "count" in data
    assert data["retention_local"] == 14
    assert isinstance(data["backups"], list)


def test_cloud_config_masks_secret(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/admin/backups/cloud/config", timeout=20)
    assert r.status_code == 200
    cfg = r.json()
    # secret_key must NEVER be present in response
    assert "secret_key" not in cfg, f"raw secret_key leaked: {cfg}"
    assert "secret_key_set" in cfg and isinstance(cfg["secret_key_set"], bool)
    assert "secret_key_masked" in cfg
    if cfg["secret_key_set"]:
        assert "•" in cfg["secret_key_masked"]
    # Expected Infomaniak seed values
    assert cfg["prefix"] in ("truck", "truck-test")
    assert cfg["bucket"] == "emergent-apps-backup"
    assert cfg["endpoint"].startswith("https://s3.swiss-backup")


def test_cloud_connection_test_ok(auth_session):
    r = auth_session.post(f"{BASE_URL}/api/admin/backups/cloud/test", timeout=30)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True, f"connection test not ok: {j}"
    assert "Verbindung OK" in j.get("message", "")


def test_cloud_list_endpoint(auth_session):
    r = auth_session.get(f"{BASE_URL}/api/admin/backups/cloud/list", timeout=30)
    assert r.status_code == 200
    j = r.json()
    assert "backups" in j and "count" in j


# ---------- PUT config: partial update, secret unchanged ----------
def test_put_config_partial_keeps_secret(auth_session):
    # snapshot
    before = auth_session.get(f"{BASE_URL}/api/admin/backups/cloud/config", timeout=20).json()
    before_masked = before["secret_key_masked"]
    before_secret_set = before["secret_key_set"]
    original_prefix = before["prefix"]
    original_retention = before["retention_days"]

    try:
        r = auth_session.put(
            f"{BASE_URL}/api/admin/backups/cloud/config",
            json={"prefix": "truck-test", "retention_days": 14},
            timeout=20,
        )
        assert r.status_code == 200
        after = auth_session.get(f"{BASE_URL}/api/admin/backups/cloud/config", timeout=20).json()
        assert after["prefix"] == "truck-test"
        assert after["retention_days"] == 14
        assert after["secret_key_set"] == before_secret_set
        assert after["secret_key_masked"] == before_masked
    finally:
        # restore
        auth_session.put(
            f"{BASE_URL}/api/admin/backups/cloud/config",
            json={"prefix": original_prefix, "retention_days": original_retention},
            timeout=20,
        )


# ---------- FULL CYCLE: create, verify local+cloud, delete cloud, delete local ----------
@pytest.fixture(scope="module")
def created_backup(auth_session):
    r = auth_session.post(f"{BASE_URL}/api/admin/backups", timeout=120)
    assert r.status_code == 200, f"create backup failed: {r.status_code} {r.text}"
    j = r.json()
    assert j["ok"] is True
    assert j["local"]["filename"].startswith("mongodump-")
    assert j["local"]["filename"].endswith(".tar.gz")
    assert j["local"]["size_bytes"] > 0
    return j


def test_create_backup_local_meta(created_backup):
    local = created_backup["local"]
    assert local["size_mb"] >= 0
    assert local["path"].startswith("/app/backups/")
    assert "created_at" in local


def test_create_backup_cloud_meta(created_backup):
    cloud = created_backup["cloud"]
    assert cloud is not None, "cloud upload result missing"
    assert cloud["ok"] is True, f"cloud upload failed: {cloud}"
    assert cloud["bucket"] == "emergent-apps-backup"
    assert cloud["key"].startswith("truck/mongodump-"), f"bad key prefix: {cloud['key']}"
    assert cloud["size_bytes"] > 0
    assert "uploaded_at" in cloud
    assert "pruned" in cloud


def test_backup_appears_in_local_list(auth_session, created_backup):
    filename = created_backup["local"]["filename"]
    r = auth_session.get(f"{BASE_URL}/api/admin/backups", timeout=20)
    files = [b["filename"] for b in r.json()["backups"]]
    assert filename in files


def test_backup_appears_in_cloud_list(auth_session, created_backup):
    key = created_backup["cloud"]["key"]
    # tiny delay for S3 consistency
    time.sleep(2)
    r = auth_session.get(f"{BASE_URL}/api/admin/backups/cloud/list", timeout=30)
    keys = [b["key"] for b in r.json()["backups"]]
    assert key in keys, f"key {key} not in cloud list. Found: {keys[:5]}"


def test_cleanup_cloud_and_local(auth_session, created_backup):
    """Cleanup: delete cloud backup created above + delete local archive."""
    cloud_key = created_backup["cloud"]["key"]
    local_name = created_backup["local"]["filename"]

    # Delete cloud
    r = auth_session.delete(f"{BASE_URL}/api/admin/backups/cloud/{cloud_key}", timeout=30)
    assert r.status_code == 200
    assert r.json().get("ok") is True
    time.sleep(1)
    # Verify gone
    r = auth_session.get(f"{BASE_URL}/api/admin/backups/cloud/list", timeout=30)
    assert cloud_key not in [b["key"] for b in r.json()["backups"]]

    # Delete local
    r = auth_session.delete(f"{BASE_URL}/api/admin/backups/{local_name}", timeout=20)
    assert r.status_code == 200
    r = auth_session.get(f"{BASE_URL}/api/admin/backups", timeout=20)
    assert local_name not in [b["filename"] for b in r.json()["backups"]]


def test_delete_nonexistent_local_returns_404(auth_session):
    r = auth_session.delete(f"{BASE_URL}/api/admin/backups/nonexistent-XYZ.tar.gz", timeout=20)
    assert r.status_code == 404
