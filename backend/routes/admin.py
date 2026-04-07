from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, UploadFile, File
from fastapi.responses import Response as FastAPIResponse
from datetime import datetime, timezone
from database import db
from auth import get_current_user
from models import InquiryCreate, InquiryStatusUpdate, CalendarBlockCreate, FAQCreate, EmployeeCreate
from services.email import (
    get_email_settings, get_email_t, send_email_background,
    build_confirmation_email, build_admin_notification_email, build_offer_email,
    build_status_notification_email, build_invoice_notification_email,
    build_file_upload_notification_email, build_event_reminder_email,
    build_event_application_email
)
from services.pdf import generate_offer_pdf, generate_export_pdf
from services.storage import put_object, get_object, APP_NAME
from services.event_scout import get_perplexity_key, call_perplexity_search, run_event_scan, PERPLEXITY_API_URL
import uuid
import io
import os
import csv as csv_module
import json as json_mod
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES_PER_INQUIRY = 5
BASE_LOCATION = {"lat": 47.3231, "lon": 8.7994, "name": "Wetzikon"}


# --- INQUIRIES (Public + Admin) ---
@router.post("/inquiries")
async def create_inquiry(inquiry: InquiryCreate, request: Request, background_tasks: BackgroundTasks):
    doc = inquiry.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["status"] = "new"
    doc["internal_notes"] = ""
    doc["invoice_status"] = "none"
    doc["invoice_amount"] = 0
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        user = await get_current_user(request)
        doc["customer_id"] = str(user["_id"])
    except Exception:
        doc["customer_id"] = ""
    settings = await get_email_settings()
    if settings.get("auto_confirmation"):
        doc["status"] = "confirmed"
    await db.inquiries.insert_one(doc)
    lang = doc.get("lang", "de")
    t = get_email_t(lang)
    if doc.get("email"):
        background_tasks.add_task(send_email_background, doc["email"], f"{t['subject_inquiry']} – TrucksOnRoad", build_confirmation_email(doc, lang))
    if settings.get("email_notifications") and settings.get("notification_email"):
        background_tasks.add_task(send_email_background, settings["notification_email"], f"Neue Anfrage: {doc.get('first_name', '')} {doc.get('last_name', '')}", build_admin_notification_email(doc))
    return {"message": "Anfrage erfolgreich gesendet", "id": doc["id"]}


# --- FILE UPLOAD ---
@router.post("/inquiries/{inquiry_id}/upload")
async def upload_inquiry_file(inquiry_id: str, request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Datei zu gross (max. 10 MB)")
    existing = await db.files.count_documents({"inquiry_id": inquiry_id, "is_deleted": False})
    if existing >= MAX_FILES_PER_INQUIRY:
        raise HTTPException(status_code=400, detail=f"Maximal {MAX_FILES_PER_INQUIRY} Dateien pro Anfrage")
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
    storage_path = f"{APP_NAME}/inquiries/{inquiry_id}/{uuid.uuid4()}.{ext}"
    result = put_object(storage_path, data, file.content_type or "application/octet-stream")
    file_doc = {
        "id": str(uuid.uuid4()),
        "inquiry_id": inquiry_id,
        "storage_path": result["path"],
        "original_filename": file.filename,
        "content_type": file.content_type or "application/octet-stream",
        "size": result.get("size", len(data)),
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.files.insert_one(file_doc)
    file_doc.pop("_id", None)
    try:
        user = await get_current_user(request)
        if user.get("role") == "admin":
            inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
            if inquiry and inquiry.get("email"):
                il = inquiry.get("lang", "de")
                it = get_email_t(il)
                html = build_file_upload_notification_email(inquiry, file.filename, il)
                background_tasks.add_task(send_email_background, inquiry["email"], f"{it['new_file']} – TrucksOnRoad", html)
    except Exception:
        pass
    return file_doc


@router.get("/inquiries/{inquiry_id}/files")
async def get_inquiry_files(inquiry_id: str):
    files = await db.files.find({"inquiry_id": inquiry_id, "is_deleted": False}, {"_id": 0}).to_list(20)
    return files


@router.get("/files/{file_id}/download")
async def download_file(file_id: str):
    record = await db.files.find_one({"id": file_id, "is_deleted": False})
    if not record:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")
    data, ct = get_object(record["storage_path"])
    return FastAPIResponse(
        content=data,
        media_type=record.get("content_type", ct),
        headers={"Content-Disposition": f'inline; filename="{record.get("original_filename", "download")}"'}
    )


@router.delete("/files/{file_id}")
async def delete_file(file_id: str, request: Request):
    await get_current_user(request)
    await db.files.update_one({"id": file_id}, {"$set": {"is_deleted": True}})
    return {"message": "Deleted"}


# --- ADMIN INQUIRIES ---
@router.get("/admin/inquiries")
async def admin_get_inquiries(request: Request):
    await get_current_user(request)
    return await db.inquiries.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)


@router.get("/admin/inquiries/{inquiry_id}")
async def admin_get_inquiry(inquiry_id: str, request: Request):
    await get_current_user(request)
    doc = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return doc


@router.put("/admin/inquiries/{inquiry_id}")
async def admin_update_inquiry(inquiry_id: str, update: InquiryStatusUpdate, request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    updates = {"status": update.status, "internal_notes": update.internal_notes, "updated_at": datetime.now(timezone.utc).isoformat()}
    if hasattr(update, 'assigned_employees') and update.assigned_employees is not None:
        updates["assigned_employees"] = update.assigned_employees
    result = await db.inquiries.update_one({"id": inquiry_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    if update.status == "offer_sent":
        confirm_token = str(uuid.uuid4())
        await db.inquiries.update_one({"id": inquiry_id}, {"$set": {"confirm_token": confirm_token}})
        inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
        if inquiry and inquiry.get("email"):
            il = inquiry.get("lang", "de")
            it = get_email_t(il)
            base_url = os.environ.get("FRONTEND_URL", "https://trucksonroad.ch")
            confirm_url = f"{base_url}/offerte-bestaetigen?id={inquiry_id}&token={confirm_token}"
            offer_html = build_offer_email(inquiry, il, confirm_url=confirm_url)
            background_tasks.add_task(send_email_background, inquiry["email"], f"{it['subject_offer']} – TrucksOnRoad", offer_html)
    elif update.status in ("in_review", "confirmed", "completed", "cancelled"):
        inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
        if inquiry and inquiry.get("email"):
            il = inquiry.get("lang", "de")
            it = get_email_t(il)
            status_html = build_status_notification_email(inquiry, update.status, il)
            subject_key = f"subject_{update.status}" if update.status != "in_review" else "subject_status"
            subject = f"{it.get(subject_key, it['subject_status'])} – TrucksOnRoad"
            background_tasks.add_task(send_email_background, inquiry["email"], subject, status_html)
    return {"message": "Updated"}


@router.put("/admin/inquiries/{inquiry_id}/lang")
async def admin_update_inquiry_lang(inquiry_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    new_lang = body.get("lang", "de")
    if new_lang not in ("de", "en", "fr", "it"):
        raise HTTPException(status_code=400, detail="Invalid language")
    result = await db.inquiries.update_one({"id": inquiry_id}, {"$set": {"lang": new_lang}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Language updated"}


@router.delete("/admin/inquiries/{inquiry_id}")
async def admin_delete_inquiry(inquiry_id: str, request: Request):
    await get_current_user(request)
    result = await db.inquiries.delete_one({"id": inquiry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}


@router.put("/admin/inquiries/{inquiry_id}/invoice")
async def admin_update_invoice(inquiry_id: str, request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    body = await request.json()
    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if "invoice_status" in body:
        updates["invoice_status"] = body["invoice_status"]
    if "invoice_amount" in body:
        updates["invoice_amount"] = body["invoice_amount"]
    result = await db.inquiries.update_one({"id": inquiry_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    if "invoice_status" in body and body["invoice_status"] not in ("none", ""):
        inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
        if inquiry and inquiry.get("email"):
            il = inquiry.get("lang", "de")
            it = get_email_t(il)
            inv_html = build_invoice_notification_email(inquiry, body["invoice_status"], body.get("invoice_amount", inquiry.get("invoice_amount", 0)), il)
            subject_key = f"subject_inv_{body['invoice_status']}"
            subject = f"{it.get(subject_key, it['invoice_word'])} – TrucksOnRoad"
            background_tasks.add_task(send_email_background, inquiry["email"], subject, inv_html)
    return {"message": "Invoice updated"}


@router.delete("/admin/inquiries/{inquiry_id}/invoice")
async def admin_delete_invoice(inquiry_id: str, request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(403, "Nur Admins")
    result = await db.inquiries.update_one({"id": inquiry_id}, {"$set": {
        "invoice_status": "none", "invoice_amount": 0, "updated_at": datetime.now(timezone.utc).isoformat()
    }})
    if result.matched_count == 0:
        raise HTTPException(404, "Not found")
    return {"message": "Rechnung gelöscht"}




@router.put("/admin/inquiries/{inquiry_id}/finance")
async def admin_update_finance(inquiry_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    allowed = ["revenue", "personnel_cost", "material_cost", "travel_cost", "other_cost", "finance_notes"]
    updates = {k: body[k] for k in allowed if k in body}
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.inquiries.update_one({"id": inquiry_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Finance updated"}


@router.put("/admin/inquiries/{inquiry_id}/coords")
async def admin_update_coords(inquiry_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    updates = {"lat": body.get("lat"), "lon": body.get("lon"), "updated_at": datetime.now(timezone.utc).isoformat()}
    result = await db.inquiries.update_one({"id": inquiry_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Coordinates updated"}


@router.get("/admin/inquiries/{inquiry_id}/offer-pdf")
async def admin_offer_pdf(inquiry_id: str, request: Request):
    await get_current_user(request)
    inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
    if not inquiry:
        raise HTTPException(status_code=404, detail="Not found")
    pdf_bytes = generate_offer_pdf(inquiry, inquiry.get("lang", "de"))
    il = inquiry.get("lang", "de")
    it = get_email_t(il)
    name = f"{inquiry.get('first_name', '')}_{inquiry.get('last_name', '')}".strip("_") or "Anfrage"
    return FastAPIResponse(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={it['pdf_offer']}_{name}.pdf"})


# --- ADMIN CALENDAR ---
@router.get("/admin/calendar")
async def admin_get_calendar(request: Request):
    await get_current_user(request)
    return await db.calendar_blocks.find({}, {"_id": 0}).to_list(10000)


@router.post("/admin/calendar")
async def admin_create_block(block: CalendarBlockCreate, request: Request):
    await get_current_user(request)
    doc = block.model_dump()
    existing = await db.calendar_blocks.find_one({"truck_slug": doc["truck_slug"], "date": doc["date"]})
    if existing:
        await db.calendar_blocks.update_one(
            {"truck_slug": doc["truck_slug"], "date": doc["date"]},
            {"$set": {"status": doc["status"], "notes": doc.get("notes", "")}}
        )
        return {"message": "Updated"}
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.calendar_blocks.insert_one(doc)
    return {"message": "Created", "id": doc["id"]}


@router.delete("/admin/calendar/{block_id}")
async def admin_delete_block(block_id: str, request: Request):
    await get_current_user(request)
    result = await db.calendar_blocks.delete_one({"id": block_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}


# --- ADMIN FAQS ---
@router.get("/admin/faqs")
async def admin_get_faqs(request: Request):
    await get_current_user(request)
    return await db.faqs.find({}, {"_id": 0}).sort("order", 1).to_list(100)


@router.post("/admin/faqs")
async def admin_create_faq(faq: FAQCreate, request: Request):
    await get_current_user(request)
    doc = faq.model_dump()
    doc["id"] = str(uuid.uuid4())
    await db.faqs.insert_one(doc)
    return {"message": "Created", "id": doc["id"]}


@router.put("/admin/faqs/{faq_id}")
async def admin_update_faq(faq_id: str, faq: FAQCreate, request: Request):
    await get_current_user(request)
    result = await db.faqs.update_one({"id": faq_id}, {"$set": faq.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}


@router.delete("/admin/faqs/{faq_id}")
async def admin_delete_faq(faq_id: str, request: Request):
    await get_current_user(request)
    result = await db.faqs.delete_one({"id": faq_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}


# --- ADMIN TRUCKS ---
@router.get("/admin/trucks")
async def admin_get_trucks(request: Request):
    await get_current_user(request)
    return await db.trucks.find({}, {"_id": 0}).sort("order", 1).to_list(100)


@router.post("/admin/trucks")
async def admin_create_truck(request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(403, "Nur Admins")
    body = await request.json()
    name = body.get("name_de", "").strip()
    slug = body.get("slug", "").strip()
    if not name or not slug:
        raise HTTPException(400, "Name und Slug erforderlich")
    existing = await db.trucks.find_one({"slug": slug})
    if existing:
        raise HTTPException(400, "Truck mit diesem Slug existiert bereits")
    count = await db.trucks.count_documents({})
    truck = {
        "slug": slug, "name_de": name, "name_en": name, "name_fr": name, "name_it": name,
        "tagline_de": "", "tagline_en": "", "tagline_fr": "", "tagline_it": "",
        "desc_de": "", "desc_en": "", "desc_fr": "", "desc_it": "",
        "image": "", "gallery": [], "video_url": "",
        "menu_de": [], "menu_en": [], "menu_fr": [], "menu_it": [],
        "tag": "", "order": count + 1,
        "story_de": "", "story_en": "", "story_fr": "", "story_it": "",
        "stat_events": "", "stat_specialty": "", "stat_rating": "",
        "quote_text_de": "", "quote_author": "",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.trucks.insert_one(truck)
    truck.pop("_id", None)
    return truck



@router.put("/admin/trucks/{slug}")
async def admin_update_truck(slug: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("slug", None)
    result = await db.trucks.update_one({"slug": slug}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}


@router.post("/admin/trucks/{slug}/gallery")
async def upload_truck_gallery_image(slug: str, request: Request, file: UploadFile = File(...)):
    await get_current_user(request)
    truck = await db.trucks.find_one({"slug": slug}, {"_id": 0})
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    data = await file.read()
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    storage_path = f"{APP_NAME}/trucks/{slug}/{uuid.uuid4()}.{ext}"
    result = put_object(storage_path, data, file.content_type or "image/jpeg")
    url = result.get("url", "")
    await db.trucks.update_one({"slug": slug}, {"$push": {"gallery": url}})
    return {"url": url}


@router.delete("/admin/trucks/{slug}/gallery")
async def delete_truck_gallery_image(slug: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    url = body.get("url", "")
    await db.trucks.update_one({"slug": slug}, {"$pull": {"gallery": url}})
    return {"message": "Removed"}


# --- ADMIN STATS ---
@router.get("/admin/stats")
async def admin_stats(request: Request):
    await get_current_user(request)
    total = await db.inquiries.count_documents({})
    new_count = await db.inquiries.count_documents({"status": "new"})
    confirmed = await db.inquiries.count_documents({"status": "confirmed"})
    trucks = await db.trucks.count_documents({"is_active": True})
    return {"total_inquiries": total, "new_inquiries": new_count, "confirmed": confirmed, "total_trucks": trucks}


# --- ADMIN SETTINGS ---
@router.get("/admin/settings")
async def admin_get_settings(request: Request):
    await get_current_user(request)
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    defaults = {
        "type": "general", "company_name": "TrucksOnRoad",
        "company_address": "Bahnhofstrasse 75, 8620 Wetzikon",
        "company_phone": "+41 79 696 98 99", "company_email": "info@trucksonroad.ch",
        "whatsapp_number": "+41796969899",
        "social_google_business": "", "social_instagram": "", "social_facebook": "",
        "social_tiktok": "", "social_linkedin": "",
        "google_verification": "",
        "event_reminder_days": 3,
        "auto_confirmation": False,
        "email_notifications": False, "notification_email": "",
        "smtp_host": "smtp.gmail.com", "smtp_port": 587,
        "smtp_email": "", "smtp_password": "",
        "perplexity_api_key": ""
    }
    if s:
        defaults.update(s)
    return defaults


@router.put("/admin/settings")
async def admin_update_settings(request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body["type"] = "general"
    await db.settings.update_one({"type": "general"}, {"$set": body}, upsert=True)
    return {"message": "Updated"}


@router.post("/admin/settings/test-email")
async def admin_test_email(request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    body = await request.json()
    to = body.get("to", "")
    if not to:
        raise HTTPException(status_code=400, detail="E-Mail-Adresse fehlt")
    background_tasks.add_task(send_email_background, to, "TrucksOnRoad Test-E-Mail", "<h2>Test erfolgreich!</h2><p>Die E-Mail-Konfiguration funktioniert korrekt.</p>")
    return {"message": "Test-E-Mail wird gesendet"}


# --- ADMIN EMPLOYEES ---
@router.get("/admin/employees")
async def admin_get_employees(request: Request):
    await get_current_user(request)
    return await db.employees.find({}, {"_id": 0}).sort("name", 1).to_list(500)


@router.post("/admin/employees")
async def admin_create_employee(emp: EmployeeCreate, request: Request):
    await get_current_user(request)
    doc = emp.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.employees.insert_one(doc)
    return {"message": "Created", "id": doc["id"]}


@router.put("/admin/employees/{emp_id}")
async def admin_update_employee(emp_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("id", None)
    result = await db.employees.update_one({"id": emp_id}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}


@router.delete("/admin/employees/{emp_id}")
async def admin_delete_employee(emp_id: str, request: Request):
    await get_current_user(request)
    result = await db.employees.delete_one({"id": emp_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}


# --- ADMIN REVIEWS ---
@router.get("/admin/reviews")
async def admin_get_reviews(request: Request):
    await get_current_user(request)
    reviews = await db.reviews.find({}, {"_id": 0}).sort("date", -1).to_list(200)
    return reviews


@router.post("/admin/reviews")
async def admin_create_review(request: Request):
    await get_current_user(request)
    body = await request.json()
    review = {
        "id": str(uuid.uuid4()),
        "author": body.get("author", ""),
        "rating": max(1, min(5, int(body.get("rating", 5)))),
        "text": body.get("text", ""),
        "date": body.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "event_type": body.get("event_type", ""),
        "source": body.get("source", "placeholder"),
        "is_active": body.get("is_active", True),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.reviews.insert_one(review)
    review.pop("_id", None)
    return review


@router.put("/admin/reviews/{review_id}")
async def admin_update_review(review_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("id", None)
    if "rating" in body:
        body["rating"] = max(1, min(5, int(body["rating"])))
    await db.reviews.update_one({"id": review_id}, {"$set": body})
    return {"message": "Updated"}


@router.delete("/admin/reviews/{review_id}")
async def admin_delete_review(review_id: str, request: Request):
    await get_current_user(request)
    await db.reviews.delete_one({"id": review_id})
    return {"message": "Deleted"}


# --- ADMIN EMAIL PREVIEW ---
@router.get("/admin/email-preview")
async def admin_email_preview(request: Request, lang: str = "de"):
    await get_current_user(request)
    sample = {
        "first_name": "Max", "last_name": "Mustermann",
        "email": "max@beispiel.ch", "phone": "+41 79 123 45 67",
        "event_date": "15.06.2026", "location": "Zürich, Sechseläutenplatz",
        "guest_count": 200, "event_type": "Firmenanlass",
        "selected_trucks": ["Burger Truck", "Bowl Truck"], "budget": "CHF 5'000 – 10'000",
        "lang": lang,
    }
    return {
        "confirmation": build_confirmation_email(sample, lang),
        "notification": build_admin_notification_email(sample),
        "status_confirmed": build_status_notification_email(sample, "confirmed", lang),
        "status_completed": build_status_notification_email(sample, "completed", lang),
        "invoice_sent": build_invoice_notification_email(sample, "sent", 4500, lang),
        "invoice_paid": build_invoice_notification_email(sample, "paid", 4500, lang),
        "file_upload": build_file_upload_notification_email(sample, "Event-Plan_2026.pdf", lang),
        "event_reminder": build_event_reminder_email(sample, 3, lang),
    }


# --- ADMIN FINANCE OVERVIEW ---
@router.get("/admin/finance/overview")
async def admin_finance_overview(request: Request):
    await get_current_user(request)
    inquiries = await db.inquiries.find({}, {"_id": 0}).to_list(10000)
    total_revenue = 0
    total_costs = 0
    by_month = {}
    by_truck = {}
    events_with_finance = 0
    for inq in inquiries:
        rev = float(inq.get("revenue", 0) or 0)
        p_cost = float(inq.get("personnel_cost", 0) or 0)
        m_cost = float(inq.get("material_cost", 0) or 0)
        t_cost = float(inq.get("travel_cost", 0) or 0)
        o_cost = float(inq.get("other_cost", 0) or 0)
        costs = p_cost + m_cost + t_cost + o_cost
        if rev > 0 or costs > 0:
            events_with_finance += 1
        total_revenue += rev
        total_costs += costs
        date_str = inq.get("event_date", "")
        if date_str and date_str != "-":
            month_key = date_str[:7]
            if month_key not in by_month:
                by_month[month_key] = {"revenue": 0, "costs": 0, "count": 0}
            by_month[month_key]["revenue"] += rev
            by_month[month_key]["costs"] += costs
            by_month[month_key]["count"] += 1
        for truck in inq.get("selected_trucks", []):
            if truck not in by_truck:
                by_truck[truck] = {"revenue": 0, "costs": 0, "count": 0}
            share = 1 / max(len(inq.get("selected_trucks", [])), 1)
            by_truck[truck]["revenue"] += rev * share
            by_truck[truck]["costs"] += costs * share
            by_truck[truck]["count"] += 1
    return {
        "total_revenue": round(total_revenue, 2),
        "total_costs": round(total_costs, 2),
        "total_profit": round(total_revenue - total_costs, 2),
        "events_with_finance": events_with_finance,
        "by_month": dict(sorted(by_month.items())),
        "by_truck": by_truck,
    }


# --- ADMIN ROUTING ---
@router.get("/admin/geocode")
async def admin_geocode(address: str, request: Request):
    await get_current_user(request)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1, "countrycodes": "ch"},
            headers={"User-Agent": "TrucksOnRoad/1.0"},
            timeout=10,
        )
        results = resp.json()
        if not results:
            return {"found": False}
        r = results[0]
        return {"found": True, "lat": float(r["lat"]), "lon": float(r["lon"]), "display_name": r["display_name"]}


@router.get("/admin/route")
async def admin_route(from_lat: float, from_lon: float, to_lat: float, to_lon: float, request: Request):
    await get_current_user(request)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://router.project-osrm.org/route/v1/driving/{from_lon},{from_lat};{to_lon},{to_lat}",
            params={"overview": "full", "geometries": "geojson"},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return {"found": False}
        route = data["routes"][0]
        return {
            "found": True,
            "distance_km": round(route["distance"] / 1000, 1),
            "duration_min": round(route["duration"] / 60),
            "geometry": route["geometry"],
        }


@router.get("/admin/route/optimize")
async def admin_route_optimize(request: Request):
    await get_current_user(request)
    params = dict(request.query_params)
    coords_str = params.get("coords", "")
    if not coords_str:
        return {"found": False, "error": "No coordinates"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://router.project-osrm.org/trip/v1/driving/{coords_str}",
            params={"overview": "full", "geometries": "geojson", "roundtrip": "true", "source": "first"},
            timeout=15,
        )
        data = resp.json()
        if data.get("code") != "Ok" or not data.get("trips"):
            return {"found": False}
        trip = data["trips"][0]
        waypoints = data.get("waypoints", [])
        return {
            "found": True,
            "distance_km": round(trip["distance"] / 1000, 1),
            "duration_min": round(trip["duration"] / 60),
            "geometry": trip["geometry"],
            "waypoint_order": [w.get("waypoint_index", i) for i, w in enumerate(waypoints)],
        }


@router.get("/admin/events-map")
async def admin_events_map(request: Request):
    await get_current_user(request)
    inquiries = await db.inquiries.find(
        {"status": {"$in": ["confirmed", "offer_sent", "in_review"]}},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    events = []
    for inq in inquiries:
        events.append({
            "id": inq.get("id"),
            "name": f"{inq.get('first_name', '')} {inq.get('last_name', '')}".strip() or inq.get("name", ""),
            "event_date": inq.get("event_date", ""),
            "location": inq.get("location", ""),
            "lat": inq.get("lat"),
            "lon": inq.get("lon"),
            "status": inq.get("status"),
            "selected_trucks": inq.get("selected_trucks", []),
            "guest_count": inq.get("guest_count"),
        })
    return {"events": events, "base": BASE_LOCATION}


@router.post("/admin/send-reminders")
async def admin_trigger_reminders(request: Request):
    from services.event_scout import send_event_reminders
    await get_current_user(request)
    await send_event_reminders()
    return {"message": "Erinnerungen geprüft und gesendet"}


# --- ADMIN EXPORT ---
@router.get("/admin/export/{data_type}")
async def admin_export(data_type: str, format: str = "csv", request: Request = None):
    await get_current_user(request)
    if data_type == "inquiries":
        docs = await db.inquiries.find({}, {"_id": 0}).sort("created_at", -1).to_list(10000)
        fields = ["id", "first_name", "last_name", "email", "phone", "event_date", "location", "guest_count", "event_type", "status", "budget", "assigned_employees", "internal_notes", "created_at"]
    elif data_type == "calendar":
        docs = await db.calendar_blocks.find({}, {"_id": 0}).sort("date", 1).to_list(10000)
        fields = ["id", "truck_slug", "date", "status", "notes", "created_at"]
    elif data_type == "employees":
        docs = await db.employees.find({}, {"_id": 0}).sort("name", 1).to_list(500)
        fields = ["id", "name", "phone", "role", "notes", "is_active", "created_at"]
    elif data_type == "faqs":
        docs = await db.faqs.find({}, {"_id": 0}).sort("order", 1).to_list(100)
        fields = ["id", "question_de", "answer_de", "question_en", "answer_en", "order"]
    elif data_type == "trucks":
        docs = await db.trucks.find({}, {"_id": 0}).sort("order", 1).to_list(100)
        fields = ["slug", "name_de", "name_en", "capacity", "space_required", "tag", "is_active"]
    else:
        raise HTTPException(status_code=400, detail="Invalid data type")
    if format == "csv":
        output = io.StringIO()
        writer = csv_module.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for doc in docs:
            row = {}
            for f in fields:
                val = doc.get(f, "")
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                row[f] = val
            writer.writerow(row)
        return FastAPIResponse(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={data_type}_export.csv"})
    else:
        pdf_bytes = generate_export_pdf(data_type, docs, fields)
        return FastAPIResponse(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={data_type}_export.pdf"})


# --- EVENT SCOUT ---
@router.post("/admin/event-scout/search")
async def event_scout_search(request: Request):
    await get_current_user(request)
    body = await request.json()
    query = body.get("query", "")
    region = body.get("region", "Schweiz")
    if not query:
        raise HTTPException(status_code=400, detail="Suchbegriff fehlt")
    api_key = await get_perplexity_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Perplexity API-Key nicht konfiguriert. Bitte in Einstellungen hinterlegen.")

    settings = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
    sources = settings.get("scout_sources", [])
    source_context = ""
    if sources:
        source_context = "Durchsuche auch diese bekannten Event-Webseiten: " + ", ".join(sources)

    system_prompt = f"""Du bist ein Experte fuer Event-Recherche in der SCHWEIZ. 
Suche nach relevanten Events, Festivals, Weihnachtsmaerkten, Strassenfesten, Firmenfeiern und Maerkten in der Region {region}, SCHWEIZ.
{source_context}
WICHTIG: Nur Events in der SCHWEIZ. Keine Events aus anderen Laendern.
Antworte IMMER im folgenden JSON-Format (Array von Events):
[
  {{
    "name": "Event-Name",
    "date": "Datum oder Zeitraum (z.B. 15.-18. Dezember 2026)",
    "location": "Stadt/Ort",
    "type": "festival|weihnachtsmarkt|markt|firmenevent|strassenfest|andere",
    "description": "Kurzbeschreibung (1-2 Saetze)",
    "organizer_email": "E-Mail des Veranstalters falls verfuegbar, sonst leer",
    "website": "URL zur Event-Website falls verfuegbar"
  }}
]
Liefere so viele relevante Events wie moeglich (mindestens 5-10). Gib NUR den JSON-Array zurueck, keine zusaetzliche Erklaerung."""

    try:
        async with httpx.AsyncClient(timeout=60) as http_client:
            resp = await http_client.post(
                PERPLEXITY_API_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Finde aktuelle und kommende Events fuer: {query} in {region} 2025/2026"}
                    ],
                    "temperature": 0.3
                }
            )
            if resp.status_code == 401:
                raise HTTPException(status_code=400, detail="Perplexity API-Key ungueltig.")
            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "[]")
            citations = data.get("citations", [])
            try:
                clean = content.strip()
                if clean.startswith("```"):
                    clean = clean.split("\n", 1)[-1]
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    clean = clean.strip()
                events = json_mod.loads(clean)
            except (json_mod.JSONDecodeError, Exception):
                events = []
                logger.warning(f"Event scout parse error. Raw: {content[:500]}")
            return {"events": events, "citations": citations, "raw": content}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Perplexity API Fehler: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Event scout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/event-scout/events")
async def get_scouted_events(request: Request):
    await get_current_user(request)
    events = await db.scouted_events.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return events


@router.post("/admin/event-scout/events")
async def save_scouted_event(request: Request):
    await get_current_user(request)
    body = await request.json()
    doc = {
        "id": str(uuid.uuid4()),
        "name": body.get("name", ""),
        "date": body.get("date", ""),
        "location": body.get("location", ""),
        "type": body.get("type", "andere"),
        "description": body.get("description", ""),
        "organizer_email": body.get("organizer_email", ""),
        "website": body.get("website", ""),
        "status": "new",
        "notes": "",
        "source": body.get("source", "perplexity"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.scouted_events.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.put("/admin/event-scout/events/{event_id}")
async def update_scouted_event(event_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("id", None)
    await db.scouted_events.update_one({"id": event_id}, {"$set": body})
    return {"message": "Updated"}


@router.delete("/admin/event-scout/events/{event_id}")
async def delete_scouted_event(event_id: str, request: Request):
    await get_current_user(request)
    await db.scouted_events.delete_one({"id": event_id})
    return {"message": "Deleted"}


@router.post("/admin/event-scout/events/{event_id}/apply")
async def send_event_application(event_id: str, request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    event = await db.scouted_events.find_one({"id": event_id}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event nicht gefunden")
    body = await request.json()
    to_email = body.get("email", event.get("organizer_email", ""))
    custom_message = body.get("message", "")
    if not to_email:
        raise HTTPException(status_code=400, detail="Keine E-Mail-Adresse angegeben")
    settings = await get_email_settings()
    html = build_event_application_email(event, custom_message, settings)
    company = settings.get("company_name", "TrucksOnRoad")
    background_tasks.add_task(send_email_background, to_email, f"Bewerbung Foodtruck - {event.get('name', 'Event')} | {company}", html)
    await db.scouted_events.update_one({"id": event_id}, {"$set": {"status": "contacted", "organizer_email": to_email}})
    return {"message": "Bewerbung wird gesendet"}


# --- EVENT SCOUT SOURCES ---
@router.get("/admin/event-scout/sources")
async def get_scout_sources(request: Request):
    await get_current_user(request)
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return {
        "sources": (s or {}).get("scout_sources", []),
        "keywords": (s or {}).get("scout_keywords", ["Festival", "Weihnachtsmarkt", "Strassenfest", "Food Festival", "Markt"]),
        "scan_enabled": (s or {}).get("scout_auto_scan", False),
        "last_scan": (s or {}).get("scout_last_scan", None),
        "last_scan_count": (s or {}).get("scout_last_scan_count", 0),
    }


@router.put("/admin/event-scout/sources")
async def update_scout_sources(request: Request):
    await get_current_user(request)
    body = await request.json()
    update_fields = {}
    if "sources" in body:
        update_fields["scout_sources"] = [s.strip() for s in body["sources"] if s.strip()]
    if "keywords" in body:
        update_fields["scout_keywords"] = [k.strip() for k in body["keywords"] if k.strip()]
    if "scan_enabled" in body:
        update_fields["scout_auto_scan"] = bool(body["scan_enabled"])
    await db.settings.update_one({"type": "general"}, {"$set": update_fields}, upsert=True)
    return {"message": "Updated"}


@router.post("/admin/event-scout/scan-now")
async def trigger_manual_scan(request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    background_tasks.add_task(run_event_scan)
    return {"message": "Scan gestartet"}



@router.delete("/admin/reset/inquiries")
async def reset_all_inquiries(request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(403, "Nur Admins")
    result = await db.inquiries.delete_many({})
    await db.finance.delete_many({})
    return {"deleted_inquiries": result.deleted_count}


@router.delete("/admin/reset/customers")
async def reset_all_customers(request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(403, "Nur Admins")
    result = await db.users.delete_many({"role": {"$ne": "admin"}})
    return {"deleted_customers": result.deleted_count}
