"""
Legal documents (AGB, Datenschutz, Impressum) with versioning.
- Each document has type, title, sections (array of {heading, content})
- Every save creates a new entry in legal_versions for audit trail
- Public endpoint serves current version, admin can manage versions and revert
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from database import db
from auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
import uuid
import difflib

router = APIRouter()

LEGAL_TYPES = {"agb", "datenschutz", "impressum"}


class LegalSection(BaseModel):
    heading: str
    content: str


class LegalDocumentUpdate(BaseModel):
    title: str
    subtitle: Optional[str] = ""
    sections: List[LegalSection]
    change_notes: Optional[str] = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize_for_diff(doc: dict) -> str:
    """Flatten document into plain text for diff comparison."""
    lines = [f"# {doc.get('title', '')}", ""]
    if doc.get("subtitle"):
        lines.append(doc["subtitle"])
        lines.append("")
    for s in doc.get("sections", []):
        lines.append(f"## {s.get('heading', '')}")
        lines.append(s.get("content", ""))
        lines.append("")
    return "\n".join(lines)


def _compute_diff(old_doc: Optional[dict], new_doc: dict) -> dict:
    old_text = _serialize_for_diff(old_doc) if old_doc else ""
    new_text = _serialize_for_diff(new_doc)
    diff = list(difflib.unified_diff(
        old_text.splitlines(), new_text.splitlines(),
        fromfile="previous", tofile="current", lineterm="", n=2,
    ))
    added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    return {
        "added_lines": added,
        "removed_lines": removed,
        "diff_text": "\n".join(diff[:500]),  # limit size
    }


# --- PUBLIC ENDPOINTS ---
@router.get("/legal/{doc_type}")
async def get_legal_public(doc_type: str):
    if doc_type not in LEGAL_TYPES:
        raise HTTPException(status_code=404, detail="Legal type unknown")
    doc = await db.legal_documents.find_one({"type": doc_type}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "type": doc["type"],
        "title": doc.get("title", ""),
        "subtitle": doc.get("subtitle", ""),
        "sections": doc.get("sections", []),
        "version": doc.get("version", 1),
        "updated_at": doc.get("updated_at"),
    }


# --- ADMIN ENDPOINTS ---
@router.get("/admin/legal")
async def list_legal_admin(request: Request):
    await get_current_user(request)
    docs = await db.legal_documents.find({}, {"_id": 0}).to_list(20)
    return docs


@router.get("/admin/legal/{doc_type}")
async def get_legal_admin(doc_type: str, request: Request):
    await get_current_user(request)
    if doc_type not in LEGAL_TYPES:
        raise HTTPException(status_code=404, detail="Legal type unknown")
    doc = await db.legal_documents.find_one({"type": doc_type}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/admin/legal/{doc_type}")
async def update_legal_admin(doc_type: str, payload: LegalDocumentUpdate, request: Request):
    user = await get_current_user(request)
    if doc_type not in LEGAL_TYPES:
        raise HTTPException(status_code=404, detail="Legal type unknown")

    current = await db.legal_documents.find_one({"type": doc_type}, {"_id": 0})
    new_version = (current.get("version", 0) + 1) if current else 1

    new_doc = {
        "type": doc_type,
        "title": payload.title,
        "subtitle": payload.subtitle or "",
        "sections": [s.model_dump() for s in payload.sections],
        "version": new_version,
        "updated_at": _now_iso(),
        "updated_by_email": user.get("email", ""),
        "updated_by_name": user.get("name", "Admin"),
    }

    diff = _compute_diff(current, new_doc)

    # Save new version snapshot
    version_entry = {
        "id": str(uuid.uuid4()),
        "doc_type": doc_type,
        "version": new_version,
        "title": new_doc["title"],
        "subtitle": new_doc["subtitle"],
        "sections": new_doc["sections"],
        "change_notes": payload.change_notes or "",
        "admin_email": new_doc["updated_by_email"],
        "admin_name": new_doc["updated_by_name"],
        "created_at": new_doc["updated_at"],
        "diff_added": diff["added_lines"],
        "diff_removed": diff["removed_lines"],
        "diff_text": diff["diff_text"],
    }
    await db.legal_versions.insert_one(version_entry)

    # Upsert current document
    await db.legal_documents.update_one(
        {"type": doc_type}, {"$set": new_doc}, upsert=True
    )

    return {"ok": True, "version": new_version, "version_id": version_entry["id"]}


@router.get("/admin/legal/{doc_type}/versions")
async def list_legal_versions(doc_type: str, request: Request):
    await get_current_user(request)
    if doc_type not in LEGAL_TYPES:
        raise HTTPException(status_code=404, detail="Legal type unknown")
    versions = await db.legal_versions.find(
        {"doc_type": doc_type},
        {"_id": 0, "diff_text": 0, "sections": 0},
    ).sort("version", -1).to_list(200)
    return versions


@router.get("/admin/legal/{doc_type}/versions/{version_id}")
async def get_legal_version(doc_type: str, version_id: str, request: Request):
    await get_current_user(request)
    if doc_type not in LEGAL_TYPES:
        raise HTTPException(status_code=404, detail="Legal type unknown")
    v = await db.legal_versions.find_one(
        {"doc_type": doc_type, "id": version_id}, {"_id": 0}
    )
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    return v


@router.post("/admin/legal/{doc_type}/restore/{version_id}")
async def restore_legal_version(doc_type: str, version_id: str, request: Request):
    user = await get_current_user(request)
    if doc_type not in LEGAL_TYPES:
        raise HTTPException(status_code=404, detail="Legal type unknown")
    target = await db.legal_versions.find_one(
        {"doc_type": doc_type, "id": version_id}, {"_id": 0}
    )
    if not target:
        raise HTTPException(status_code=404, detail="Version not found")

    current = await db.legal_documents.find_one({"type": doc_type}, {"_id": 0})
    new_version = (current.get("version", 0) + 1) if current else 1

    new_doc = {
        "type": doc_type,
        "title": target["title"],
        "subtitle": target.get("subtitle", ""),
        "sections": target["sections"],
        "version": new_version,
        "updated_at": _now_iso(),
        "updated_by_email": user.get("email", ""),
        "updated_by_name": user.get("name", "Admin"),
    }

    diff = _compute_diff(current, new_doc)

    version_entry = {
        "id": str(uuid.uuid4()),
        "doc_type": doc_type,
        "version": new_version,
        "title": new_doc["title"],
        "subtitle": new_doc["subtitle"],
        "sections": new_doc["sections"],
        "change_notes": f"Wiederherstellung von Version {target['version']}",
        "admin_email": new_doc["updated_by_email"],
        "admin_name": new_doc["updated_by_name"],
        "created_at": new_doc["updated_at"],
        "diff_added": diff["added_lines"],
        "diff_removed": diff["removed_lines"],
        "diff_text": diff["diff_text"],
        "restored_from_version": target["version"],
        "restored_from_id": target["id"],
    }
    await db.legal_versions.insert_one(version_entry)

    await db.legal_documents.update_one(
        {"type": doc_type}, {"$set": new_doc}, upsert=True
    )

    return {"ok": True, "version": new_version, "restored_from_version": target["version"]}
