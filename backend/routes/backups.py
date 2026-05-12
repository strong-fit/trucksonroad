"""Admin endpoints for DB backups (local + Infomaniak Swiss Backup S3)."""
import os
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel

from auth import get_current_user
from database import db
from services import db_backup, cloud_backup

logger = logging.getLogger(__name__)
router = APIRouter()

CLOUD_SETTINGS_TYPE = "cloud_backup"
DEFAULT_CLOUD_CFG = {
    "type": CLOUD_SETTINGS_TYPE,
    "enabled": False,
    "endpoint": "",
    "access_key": "",
    "secret_key": "",
    "bucket": "",
    "prefix": "truck",
    "region": "us-east-1",
    "retention_days": 30,
}


class CloudConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    endpoint: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bucket: Optional[str] = None
    prefix: Optional[str] = None
    region: Optional[str] = None
    retention_days: Optional[int] = None


async def _get_cloud_cfg() -> dict:
    cfg = await db.settings.find_one({"type": CLOUD_SETTINGS_TYPE}, {"_id": 0})
    if not cfg:
        await db.settings.insert_one(DEFAULT_CLOUD_CFG.copy())
        return DEFAULT_CLOUD_CFG.copy()
    # Merge in defaults for missing keys
    merged = {**DEFAULT_CLOUD_CFG, **cfg}
    return merged


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 6:
        return "•" * len(value)
    return value[:2] + "•" * (len(value) - 6) + value[-4:]


@router.get("/admin/backups")
async def list_backups(request: Request):
    await get_current_user(request)
    items = db_backup.list_local_backups()
    return {"backups": items, "count": len(items), "retention_local": db_backup.LOCAL_RETENTION}


@router.post("/admin/backups")
async def create_backup(request: Request, background_tasks: BackgroundTasks):
    """Triggers a backup run (mongodump → tar.gz → optional cloud upload)."""
    await get_current_user(request)
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url:
        raise HTTPException(status_code=500, detail="MONGO_URL not configured")

    try:
        result = db_backup.run_mongodump(mongo_url, db_name)
    except Exception as exc:
        logger.exception("mongodump failed")
        raise HTTPException(status_code=500, detail=f"mongodump failed: {exc}")

    # Optional cloud upload (best effort, errors do not fail the local backup)
    cfg = await _get_cloud_cfg()
    cloud_result = None
    if cfg.get("enabled"):
        try:
            cloud_result = cloud_backup.upload_archive(cfg, result["path"])
            try:
                pruned = cloud_backup.prune_cloud_backups(cfg, cfg.get("retention_days", 30))
                cloud_result["pruned"] = pruned
            except Exception as prune_exc:
                logger.warning(f"Cloud prune failed: {prune_exc}")
                cloud_result["pruned_error"] = str(prune_exc)
        except Exception as exc:
            logger.error(f"Cloud upload failed: {exc}")
            cloud_result = {"ok": False, "error": str(exc)}

    return {"ok": True, "local": result, "cloud": cloud_result}


@router.delete("/admin/backups/{filename}")
async def remove_backup(filename: str, request: Request):
    await get_current_user(request)
    if not db_backup.delete_backup(filename):
        raise HTTPException(status_code=404, detail="Backup not found")
    return {"ok": True}


@router.get("/admin/backups/download/{filename}")
async def download_backup(filename: str, request: Request):
    await get_current_user(request)
    safe = Path(filename).name
    target = db_backup.BACKUP_DIR / safe
    if not target.exists():
        raise HTTPException(status_code=404, detail="Backup not found")
    return FileResponse(path=str(target), filename=safe, media_type="application/gzip")


# --- Cloud config endpoints ---
@router.get("/admin/backups/cloud/config")
async def get_cloud_config(request: Request):
    await get_current_user(request)
    cfg = await _get_cloud_cfg()
    return {
        "enabled": cfg.get("enabled", False),
        "endpoint": cfg.get("endpoint", ""),
        "access_key": cfg.get("access_key", ""),
        "secret_key_set": bool(cfg.get("secret_key")),
        "secret_key_masked": _mask(cfg.get("secret_key", "")),
        "bucket": cfg.get("bucket", ""),
        "prefix": cfg.get("prefix", "truck"),
        "region": cfg.get("region", "us-east-1"),
        "retention_days": cfg.get("retention_days", 30),
    }


@router.put("/admin/backups/cloud/config")
async def update_cloud_config(payload: CloudConfigUpdate, request: Request):
    await get_current_user(request)
    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    # Empty string secret_key means "leave unchanged"
    if "secret_key" in update_data and update_data["secret_key"] == "":
        update_data.pop("secret_key")
    if update_data:
        await db.settings.update_one(
            {"type": CLOUD_SETTINGS_TYPE},
            {"$set": update_data},
            upsert=True,
        )
    return {"ok": True}


@router.post("/admin/backups/cloud/test")
async def test_cloud_connection(request: Request):
    await get_current_user(request)
    cfg = await _get_cloud_cfg()
    return cloud_backup.test_connection(cfg)


@router.get("/admin/backups/cloud/list")
async def list_cloud_backups_endpoint(request: Request):
    await get_current_user(request)
    cfg = await _get_cloud_cfg()
    if not cfg.get("enabled"):
        return {"backups": [], "count": 0, "message": "Cloud-Backup ist deaktiviert"}
    try:
        items = cloud_backup.list_cloud_backups(cfg)
        return {"backups": items, "count": len(items)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cloud-Abruf fehlgeschlagen: {exc}")


@router.delete("/admin/backups/cloud/{key:path}")
async def delete_cloud_backup_endpoint(key: str, request: Request):
    await get_current_user(request)
    cfg = await _get_cloud_cfg()
    if not cloud_backup.delete_cloud_backup(cfg, key):
        raise HTTPException(status_code=404, detail="Cloud backup not found or delete failed")
    return {"ok": True}
