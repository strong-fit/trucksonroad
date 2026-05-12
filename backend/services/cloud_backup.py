"""
Cloud Backup Service – uploads .tar.gz archives to an S3-compatible endpoint
(default: Infomaniak Swiss Backup S3).

Configuration is read from MongoDB settings (`type: "cloud_backup"`).
Cloud-side retention is enforced via age-based pruning.
"""
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

DEFAULT_PREFIX = "truck"  # app-specific separation inside the shared bucket


def _build_client(cfg: Dict):
    if not cfg.get("endpoint") or not cfg.get("access_key") or not cfg.get("secret_key") or not cfg.get("bucket"):
        raise ValueError("Cloud backup not fully configured (endpoint/access_key/secret_key/bucket required)")
    return boto3.client(
        "s3",
        endpoint_url=cfg["endpoint"],
        aws_access_key_id=cfg["access_key"],
        aws_secret_access_key=cfg["secret_key"],
        region_name=cfg.get("region") or "us-east-1",
        config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
    )


def _object_key(prefix: str, filename: str) -> str:
    return f"{prefix.strip('/')}/{filename}"


def test_connection(cfg: Dict) -> Dict:
    """Pings the S3 endpoint by listing objects (max 1). Returns {ok, message}."""
    try:
        client = _build_client(cfg)
        bucket = cfg["bucket"]
        prefix = (cfg.get("prefix") or DEFAULT_PREFIX).strip("/") + "/"
        resp = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
        count = resp.get("KeyCount", 0)
        return {"ok": True, "message": f"Verbindung OK · Bucket '{bucket}' erreichbar · {count} Objekt(e) unter Prefix '{prefix}'"}
    except (BotoCoreError, ClientError, ValueError) as exc:
        return {"ok": False, "message": f"Verbindung fehlgeschlagen: {exc}"}


def upload_archive(cfg: Dict, archive_path: str, filename: Optional[str] = None) -> Dict:
    """Uploads a local file to S3. Returns metadata."""
    client = _build_client(cfg)
    bucket = cfg["bucket"]
    prefix = (cfg.get("prefix") or DEFAULT_PREFIX).strip("/")
    name = filename or Path(archive_path).name
    key = _object_key(prefix, name)

    client.upload_file(
        Filename=archive_path,
        Bucket=bucket,
        Key=key,
        ExtraArgs={"ContentType": "application/gzip"},
    )
    size = Path(archive_path).stat().st_size
    logger.info(f"Cloud upload OK: s3://{bucket}/{key} ({size} bytes)")
    return {
        "ok": True,
        "key": key,
        "bucket": bucket,
        "size_bytes": size,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }


def list_cloud_backups(cfg: Dict, limit: int = 100) -> List[Dict]:
    """Lists archives in the bucket+prefix. Newest first."""
    client = _build_client(cfg)
    bucket = cfg["bucket"]
    prefix = (cfg.get("prefix") or DEFAULT_PREFIX).strip("/") + "/"
    paginator = client.get_paginator("list_objects_v2")
    items: List[Dict] = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []) or []:
            items.append(
                {
                    "key": obj["Key"],
                    "filename": obj["Key"].rsplit("/", 1)[-1],
                    "size_bytes": obj["Size"],
                    "size_mb": round(obj["Size"] / (1024 * 1024), 2),
                    "last_modified": obj["LastModified"].astimezone(timezone.utc).isoformat(),
                }
            )
    items.sort(key=lambda x: x["last_modified"], reverse=True)
    return items[:limit]


def prune_cloud_backups(cfg: Dict, retention_days: int) -> List[str]:
    """Deletes cloud archives older than retention_days. Returns deleted keys."""
    if retention_days <= 0:
        return []
    client = _build_client(cfg)
    bucket = cfg["bucket"]
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    deleted: List[str] = []
    for item in list_cloud_backups(cfg, limit=10000):
        try:
            ts = datetime.fromisoformat(item["last_modified"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts < cutoff:
            try:
                client.delete_object(Bucket=bucket, Key=item["key"])
                deleted.append(item["key"])
                logger.info(f"Cloud prune: deleted {item['key']}")
            except (BotoCoreError, ClientError) as exc:
                logger.warning(f"Failed to delete cloud object {item['key']}: {exc}")
    return deleted


def delete_cloud_backup(cfg: Dict, key: str) -> bool:
    try:
        client = _build_client(cfg)
        client.delete_object(Bucket=cfg["bucket"], Key=key)
        return True
    except (BotoCoreError, ClientError, ValueError) as exc:
        logger.error(f"Cloud delete failed for {key}: {exc}")
        return False
