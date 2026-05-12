"""
DB Backup Service.

- Runs mongodump to a temp folder
- Packs into a .tar.gz inside BACKUP_DIR
- Rotates old archives (keeps last N)
- Returns metadata dict for each archive
"""
import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", "/app/backups"))
LOCAL_RETENTION = int(os.environ.get("BACKUP_LOCAL_RETENTION", "14"))


def _ensure_dir() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def _archive_path(timestamp: str) -> Path:
    return BACKUP_DIR / f"mongodump-{timestamp}.tar.gz"


def list_local_backups() -> List[Dict]:
    """Lists all .tar.gz backups in BACKUP_DIR (newest first)."""
    _ensure_dir()
    items: List[Dict] = []
    for p in sorted(BACKUP_DIR.glob("mongodump-*.tar.gz"), reverse=True):
        try:
            stat = p.stat()
            items.append(
                {
                    "filename": p.name,
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    "path": str(p),
                }
            )
        except OSError:
            continue
    return items


def rotate_local_backups(keep: int = LOCAL_RETENTION) -> List[str]:
    """Deletes oldest archives so that only `keep` remain. Returns deleted filenames."""
    backups = list_local_backups()
    deleted: List[str] = []
    for old in backups[keep:]:
        try:
            Path(old["path"]).unlink()
            deleted.append(old["filename"])
            logger.info(f"Rotated: deleted old backup {old['filename']}")
        except OSError as exc:
            logger.warning(f"Could not delete {old['filename']}: {exc}")
    return deleted


def delete_backup(filename: str) -> bool:
    """Deletes a specific backup file. Returns True on success."""
    safe = Path(filename).name  # prevent traversal
    target = BACKUP_DIR / safe
    if not target.exists() or not target.is_file():
        return False
    try:
        target.unlink()
        return True
    except OSError as exc:
        logger.error(f"Failed to delete {safe}: {exc}")
        return False


def run_mongodump(mongo_url: str, db_name: Optional[str] = None) -> Dict:
    """
    Runs mongodump, packs as tar.gz, rotates old backups.
    Returns metadata of the new archive.
    Raises RuntimeError on failure.
    """
    _ensure_dir()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_path = _archive_path(timestamp)

    with tempfile.TemporaryDirectory(prefix="mongodump-") as tmp:
        tmp_path = Path(tmp)
        cmd = ["mongodump", f"--uri={mongo_url}", f"--out={tmp_path}"]
        if db_name:
            cmd.append(f"--db={db_name}")
        logger.info(f"Running mongodump → {tmp_path}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            raise RuntimeError(f"mongodump failed (rc={proc.returncode}): {proc.stderr[:500]}")

        # Pack into tar.gz
        with tarfile.open(archive_path, "w:gz") as tar:
            for entry in tmp_path.iterdir():
                tar.add(entry, arcname=entry.name)

    stat = archive_path.stat()
    rotated = rotate_local_backups()
    return {
        "filename": archive_path.name,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "created_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "path": str(archive_path),
        "rotated_local": rotated,
    }
