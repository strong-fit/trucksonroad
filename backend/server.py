from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, BackgroundTasks, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from bson import ObjectId
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.responses import Response as FastAPIResponse
from fpdf import FPDF
import io
import httpx
import requests

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_ALGORITHM = "HS256"

def get_jwt_secret():
    return os.environ["JWT_SECRET"]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    return jwt.encode({"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(hours=2), "type": "access"}, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    return jwt.encode({"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}, get_jwt_secret(), algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

app = FastAPI()
api_router = APIRouter(prefix="/api")

# --- Models ---
class LoginRequest(BaseModel):
    email: str
    password: str

class InquiryCreate(BaseModel):
    first_name: str
    last_name: str
    company: Optional[str] = ""
    email: str
    phone: str
    event_date: str
    event_time: Optional[str] = ""
    location: str
    guest_count: int
    event_type: str
    indoor_outdoor: Optional[str] = "Outdoor"
    selected_trucks: List[str] = []
    extras: List[str] = []
    budget: Optional[str] = ""
    remarks: Optional[str] = ""
    is_organizer: bool = False
    privacy_accepted: bool = True
    customer_type: Optional[str] = "Privatkunde"

class InquiryStatusUpdate(BaseModel):
    status: str
    internal_notes: Optional[str] = ""
    assigned_employees: Optional[List[str]] = None

class CalendarBlockCreate(BaseModel):
    truck_slug: str
    date: str
    status: str = "blocked"
    notes: Optional[str] = ""

class FAQCreate(BaseModel):
    question_de: str
    answer_de: str
    question_en: str
    answer_en: str
    order: int = 0

class QuickInquiryCreate(BaseModel):
    name: str
    event_date: str
    location: str
    guest_count: int
    concept: str
    email: Optional[str] = ""
    phone: Optional[str] = ""

class SettingsUpdate(BaseModel):
    company_name: Optional[str] = "TruckOnRoad"
    company_address: Optional[str] = ""
    company_phone: Optional[str] = ""
    company_email: Optional[str] = ""
    whatsapp_number: Optional[str] = ""
    social_google_business: Optional[str] = ""
    social_instagram: Optional[str] = ""
    social_facebook: Optional[str] = ""
    social_tiktok: Optional[str] = ""
    social_linkedin: Optional[str] = ""
    email_notifications: Optional[bool] = False
    notification_email: Optional[str] = ""
    smtp_host: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 587
    smtp_email: Optional[str] = ""
    smtp_password: Optional[str] = ""

class EmployeeCreate(BaseModel):
    name: str
    phone: Optional[str] = ""
    role: Optional[str] = ""
    notes: Optional[str] = ""
    is_active: Optional[bool] = True

class CustomerRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    company: Optional[str] = ""
    phone: Optional[str] = ""

# --- EMAIL ---
async def get_email_settings():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return s or {}

# --- OBJECT STORAGE ---
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "truckonroad"
_storage_key = None

def init_storage():
    global _storage_key
    if _storage_key:
        return _storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    _storage_key = resp.json()["storage_key"]
    return _storage_key

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key, "Content-Type": content_type}, data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()

def get_object(path: str):
    key = init_storage()
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

async def send_email_background(to: str, subject: str, html_body: str):
    try:
        settings = await get_email_settings()
        host = settings.get("smtp_host", "smtp.gmail.com")
        port = settings.get("smtp_port", 587)
        sender = settings.get("smtp_email", "")
        password = settings.get("smtp_password", "")
        if not sender or not password:
            logger.warning("SMTP not configured, skipping email")
            return
        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to, msg.as_string())
        logger.info(f"Email sent to {to}")
    except Exception as e:
        logger.error(f"Email sending failed: {e}")

def build_confirmation_email(inquiry: dict) -> str:
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">Vielen Dank fuer Ihre Anfrage, {name}!</h2>
        <p style="color:#6b6b64;line-height:1.6;">Wir haben Ihre Anfrage erhalten und melden uns innerhalb von 24 Stunden mit einem individuellen Angebot.</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;"><strong>Event-Datum:</strong> {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>Ort:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>Gaeste:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>Eventtyp:</strong> {inquiry.get('event_type', inquiry.get('concept', '-'))}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">Bei Fragen erreichen Sie uns jederzeit unter info@truckonroad.ch oder +41 79 696 98 99.</p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

def build_admin_notification_email(inquiry: dict) -> str:
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    trucks = ', '.join(inquiry.get('selected_trucks', [])) or '-'
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">NEUE ANFRAGE</span>
      </div>
      <div style="padding:1.5rem 2rem;">
        <h3 style="color:#1a1a18;margin:0 0 1rem;">Neue Anfrage von {name}</h3>
        <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
          <tr><td style="padding:0.4rem 0;color:#6b6b64;width:120px;">Name</td><td>{name}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">E-Mail</td><td>{inquiry.get('email', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">Telefon</td><td>{inquiry.get('phone', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">Datum</td><td>{inquiry.get('event_date', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">Ort</td><td>{inquiry.get('location', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">Gaeste</td><td>{inquiry.get('guest_count', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">Eventtyp</td><td>{inquiry.get('event_type', inquiry.get('concept', '-'))}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">Trucks</td><td>{trucks}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">Budget</td><td>{inquiry.get('budget', '-')}</td></tr>
        </table>
      </div>
    </div>"""

def build_offer_email(inquiry: dict) -> str:
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    trucks = ', '.join(inquiry.get('selected_trucks', [])) or '-'
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">Ihr Angebot, {name}</h2>
        <p style="color:#6b6b64;line-height:1.6;">Vielen Dank fuer Ihr Interesse! Basierend auf Ihrer Anfrage haben wir folgendes Angebot fuer Sie zusammengestellt:</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;"><strong>Event-Datum:</strong> {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>Ort:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>Gaeste:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>Trucks:</strong> {trucks}</p>
          <p style="margin:0.3rem 0;"><strong>Eventtyp:</strong> {inquiry.get('event_type', inquiry.get('concept', '-'))}</p>
        </div>
        <p style="color:#6b6b64;line-height:1.6;">Wir melden uns in Kuerze mit den detaillierten Konditionen. Bei Fragen stehen wir Ihnen gerne zur Verfuegung.</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1.5rem;">Herzliche Gruesse,<br/><strong>TruckOnRoad Team</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

# --- STATUS & INVOICE NOTIFICATION EMAILS ---
STATUS_LABELS = {
    "new": "Neu",
    "in_review": "In Pruefung",
    "offer_sent": "Angebot gesendet",
    "confirmed": "Bestaetigt",
    "completed": "Abgeschlossen",
    "cancelled": "Storniert",
}

INVOICE_LABELS = {
    "none": "Keine",
    "pending": "Offen",
    "sent": "Gesendet",
    "paid": "Bezahlt",
    "overdue": "Ueberfaellig",
}

def build_status_notification_email(inquiry: dict, new_status: str) -> str:
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    status_label = STATUS_LABELS.get(new_status, new_status)
    status_color = {"confirmed": "#22c55e", "completed": "#6b7280", "cancelled": "#ef4444", "offer_sent": "#8b5cf6"}.get(new_status, "#4db6ac")
    messages = {
        "in_review": "Ihre Anfrage wird aktuell von unserem Team geprueft. Wir melden uns in Kuerze bei Ihnen.",
        "offer_sent": "Wir haben ein Angebot fuer Sie erstellt. Bitte pruefen Sie die Details und melden Sie sich bei Fragen.",
        "confirmed": "Ihre Buchung ist bestaetigt! Wir freuen uns auf Ihren Event.",
        "completed": "Vielen Dank fuer Ihren Auftrag! Wir hoffen, der Event war ein voller Erfolg.",
        "cancelled": "Ihre Anfrage wurde leider storniert. Bei Fragen kontaktieren Sie uns gerne.",
    }
    msg = messages.get(new_status, f"Der Status Ihrer Anfrage wurde aktualisiert: {status_label}")
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">STATUS-UPDATE</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 0.5rem;">Hallo {name},</h2>
        <div style="display:inline-block;background:{status_color};color:#fff;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;margin:0.5rem 0 1rem;">
          {status_label}
        </div>
        <p style="color:#6b6b64;line-height:1.7;margin-top:0.5rem;">{msg}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>Event:</strong> {inquiry.get('event_type', '-')} am {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>Ort:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>Gaeste:</strong> {inquiry.get('guest_count', '-')}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">Bei Fragen erreichen Sie uns unter info@truckonroad.ch oder +41 79 696 98 99.</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">Herzliche Gruesse,<br/><strong>TruckOnRoad Team</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

def build_invoice_notification_email(inquiry: dict, invoice_status: str, invoice_amount: float = 0) -> str:
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    inv_label = INVOICE_LABELS.get(invoice_status, invoice_status)
    inv_color = {"pending": "#e8b931", "sent": "#8b5cf6", "paid": "#22c55e", "overdue": "#ef4444"}.get(invoice_status, "#6b7280")
    messages = {
        "pending": "Fuer Ihren Event wurde eine Rechnung erstellt.",
        "sent": "Wir haben Ihnen eine Rechnung zugesendet. Bitte beachten Sie die Zahlungsfrist.",
        "paid": "Vielen Dank! Ihre Zahlung ist bei uns eingegangen.",
        "overdue": "Ihre Rechnung ist ueberfaellig. Bitte ueberpruefen Sie die Zahlung.",
    }
    msg = messages.get(invoice_status, f"Ihr Rechnungsstatus wurde aktualisiert: {inv_label}")
    amount_line = f'<p style="font-size:1.3rem;font-weight:700;color:#1a1a18;margin:0.5rem 0;">CHF {invoice_amount:,.2f}</p>' if invoice_amount > 0 else ""
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">RECHNUNG</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 0.5rem;">Hallo {name},</h2>
        <div style="display:inline-block;background:{inv_color};color:#fff;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;margin:0.5rem 0 1rem;">
          Rechnung: {inv_label}
        </div>
        <p style="color:#6b6b64;line-height:1.7;margin-top:0.5rem;">{msg}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;text-align:center;">
          {amount_line}
          <p style="margin:0.3rem 0;font-size:0.88rem;color:#6b6b64;"><strong>Event:</strong> {inquiry.get('event_type', '-')} am {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;color:#6b6b64;"><strong>Ort:</strong> {inquiry.get('location', '-')}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">Bei Fragen erreichen Sie uns unter info@truckonroad.ch oder +41 79 696 98 99.</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">Herzliche Gruesse,<br/><strong>TruckOnRoad Team</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


def build_file_upload_notification_email(inquiry: dict, filename: str) -> str:
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">NEUE DATEI</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">Hallo {name},</h2>
        <p style="color:#6b6b64;line-height:1.7;">Wir haben eine neue Datei zu Ihrer Anfrage hinzugefuegt:</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1rem 0;display:flex;align-items:center;gap:0.5rem;">
          <span style="font-size:1.2rem;">📎</span>
          <span style="font-weight:600;color:#1a1a18;">{filename}</span>
        </div>
        <p style="color:#6b6b64;font-size:0.88rem;">Sie koennen diese Datei in Ihrem Kundenportal herunterladen.</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">Herzliche Gruesse,<br/><strong>TruckOnRoad Team</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

def build_event_reminder_email(inquiry: dict, days_until: int) -> str:
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">ERINNERUNG</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">Hallo {name},</h2>
        <p style="color:#6b6b64;line-height:1.7;">Nur noch <strong>{days_until} Tage</strong> bis zu Ihrem Event!</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>Event:</strong> {inquiry.get('event_type', '-')} am {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>Ort:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>Gaeste:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>Trucks:</strong> {', '.join(inquiry.get('selected_trucks', []))}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.88rem;">Wir sind bereit und freuen uns auf Ihren Event! Bei letzten Fragen erreichen Sie uns unter info@truckonroad.ch oder +41 79 696 98 99.</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">Herzliche Gruesse,<br/><strong>TruckOnRoad Team</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

def generate_offer_pdf(inquiry: dict) -> bytes:
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 12, "TRUCKONROAD", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Bahnhofstrasse 75, 8620 Wetzikon | +41 79 696 98 99 | info@truckonroad.ch", ln=True, align="C")
    pdf.ln(8)
    pdf.set_draw_color(77, 182, 172)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Angebot", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Erstellt am: {datetime.now(timezone.utc).strftime('%d.%m.%Y')}", ln=True)
    pdf.cell(0, 7, f"Anfrage-Nr.: {inquiry.get('id', '-')[:8]}", ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(77, 182, 172)
    pdf.cell(0, 8, "Kundendaten", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    fields = [
        ("Name", name), ("E-Mail", inquiry.get("email", "-")), ("Telefon", inquiry.get("phone", "-")),
        ("Firma", inquiry.get("company", "-")),
    ]
    for label, val in fields:
        if val and val != "-":
            pdf.cell(50, 7, label + ":", 0)
            pdf.cell(0, 7, str(val), ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(77, 182, 172)
    pdf.cell(0, 8, "Event-Details", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    event_fields = [
        ("Datum", inquiry.get("event_date", "-")), ("Ort", inquiry.get("location", "-")),
        ("Gaeste", str(inquiry.get("guest_count", "-"))), ("Eventtyp", inquiry.get("event_type", inquiry.get("concept", "-"))),
        ("Indoor/Outdoor", inquiry.get("indoor_outdoor", "-")), ("Budget", inquiry.get("budget", "-")),
    ]
    for label, val in event_fields:
        if val and val != "-":
            pdf.cell(50, 7, label + ":", 0)
            pdf.cell(0, 7, str(val), ln=True)
    trucks = inquiry.get("selected_trucks", [])
    if trucks:
        pdf.cell(50, 7, "Trucks:", 0)
        pdf.cell(0, 7, ", ".join(trucks), ln=True)
    extras = inquiry.get("extras", [])
    if extras:
        pdf.cell(50, 7, "Extras:", 0)
        pdf.cell(0, 7, ", ".join(extras), ln=True)
    if inquiry.get("remarks"):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Bemerkungen:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, inquiry["remarks"])
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, "Dieses Angebot ist unverbindlich und 30 Tage gueltig. Fuer Fragen stehen wir Ihnen gerne zur Verfuegung.")
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.getvalue()

# --- AUTH ---
@api_router.post("/auth/login")
async def login(request: Request, response: Response, body: LoginRequest):
    email = body.email.lower().strip()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{email}"
    attempt = await db.login_attempts.find_one({"identifier": identifier}, {"_id": 0})
    if attempt and attempt.get("count", 0) >= 5:
        last = attempt.get("last_attempt")
        if last and datetime.now(timezone.utc) - datetime.fromisoformat(str(last)) < timedelta(minutes=15):
            raise HTTPException(status_code=429, detail="Zu viele Versuche. Bitte 15 Minuten warten.")
        await db.login_attempts.delete_one({"identifier": identifier})
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        await db.login_attempts.update_one(
            {"identifier": identifier},
            {"$inc": {"count": 1}, "$set": {"last_attempt": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
        raise HTTPException(status_code=401, detail="Ungueltige Anmeldedaten")
    await db.login_attempts.delete_one({"identifier": identifier})
    uid = str(user["_id"])
    at = create_access_token(uid, email)
    rt = create_refresh_token(uid)
    response.set_cookie(key="access_token", value=at, httponly=True, secure=False, samesite="lax", max_age=7200, path="/")
    response.set_cookie(key="refresh_token", value=rt, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return {"id": uid, "email": user["email"], "name": user.get("name", ""), "role": user.get("role", "user")}

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}

@api_router.get("/auth/me")
async def get_me(request: Request):
    return await get_current_user(request)

@api_router.post("/auth/refresh")
async def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        at = create_access_token(str(user["_id"]), user["email"])
        response.set_cookie(key="access_token", value=at, httponly=True, secure=False, samesite="lax", max_age=7200, path="/")
        return {"message": "Refreshed"}
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# --- CUSTOMER REGISTRATION ---
@api_router.post("/auth/register")
async def register_customer(body: CustomerRegister, response: Response):
    email = body.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="E-Mail bereits registriert")
    user_doc = {
        "email": email,
        "password_hash": hash_password(body.password),
        "name": f"{body.first_name} {body.last_name}",
        "first_name": body.first_name,
        "last_name": body.last_name,
        "company": body.company or "",
        "phone": body.phone or "",
        "role": "customer",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    uid = str(result.inserted_id)
    at = create_access_token(uid, email)
    rt = create_refresh_token(uid)
    response.set_cookie(key="access_token", value=at, httponly=True, secure=False, samesite="lax", max_age=7200, path="/")
    response.set_cookie(key="refresh_token", value=rt, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return {"id": uid, "email": email, "name": user_doc["name"], "role": "customer"}

# --- CUSTOMER PORTAL ---
@api_router.get("/customer/inquiries")
async def customer_get_inquiries(request: Request):
    user = await get_current_user(request)
    return await db.inquiries.find({"customer_id": str(user["_id"])}, {"_id": 0}).sort("created_at", -1).to_list(200)

@api_router.get("/customer/inquiries/{inquiry_id}")
async def customer_get_inquiry(inquiry_id: str, request: Request):
    user = await get_current_user(request)
    doc = await db.inquiries.find_one({"id": inquiry_id, "customer_id": str(user["_id"])}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    return doc

@api_router.get("/customer/profile")
async def customer_get_profile(request: Request):
    user = await get_current_user(request)
    return {"email": user["email"], "name": user.get("name", ""), "first_name": user.get("first_name", ""), "last_name": user.get("last_name", ""), "company": user.get("company", ""), "phone": user.get("phone", ""), "role": user.get("role", "customer")}

# --- PUBLIC TRUCKS ---
@api_router.get("/trucks")
async def get_trucks():
    return await db.trucks.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)

@api_router.get("/trucks/{slug}")
async def get_truck(slug: str):
    truck = await db.trucks.find_one({"slug": slug}, {"_id": 0})
    if not truck:
        raise HTTPException(status_code=404, detail="Not found")
    return truck

# --- INQUIRIES ---
@api_router.post("/inquiries")
async def create_inquiry(inquiry: InquiryCreate, request: Request, background_tasks: BackgroundTasks):
    doc = inquiry.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["status"] = "new"
    doc["internal_notes"] = ""
    doc["invoice_status"] = "none"
    doc["invoice_amount"] = 0
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    # Link to customer account if logged in
    try:
        user = await get_current_user(request)
        doc["customer_id"] = str(user["_id"])
    except Exception:
        doc["customer_id"] = ""
    # Check auto-confirmation setting
    settings = await get_email_settings()
    if settings.get("auto_confirmation"):
        doc["status"] = "confirmed"
    await db.inquiries.insert_one(doc)
    # Send confirmation email to customer
    if doc.get("email"):
        background_tasks.add_task(send_email_background, doc["email"], "Anfrage erhalten – TruckOnRoad", build_confirmation_email(doc))
    # Send notification to admin
    if settings.get("email_notifications") and settings.get("notification_email"):
        background_tasks.add_task(send_email_background, settings["notification_email"], f"Neue Anfrage: {doc.get('first_name', '')} {doc.get('last_name', '')}", build_admin_notification_email(doc))
    return {"message": "Anfrage erfolgreich gesendet", "id": doc["id"]}

# --- FILE UPLOAD ---
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES_PER_INQUIRY = 5

@api_router.post("/inquiries/{inquiry_id}/upload")
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
    # Notify customer if admin uploads a file
    try:
        user = await get_current_user(request)
        if user.get("role") == "admin":
            inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
            if inquiry and inquiry.get("email"):
                html = build_file_upload_notification_email(inquiry, file.filename)
                background_tasks.add_task(send_email_background, inquiry["email"], f"Neue Datei zu Ihrer Anfrage – TruckOnRoad", html)
    except Exception:
        pass
    return file_doc

@api_router.get("/inquiries/{inquiry_id}/files")
async def get_inquiry_files(inquiry_id: str):
    files = await db.files.find({"inquiry_id": inquiry_id, "is_deleted": False}, {"_id": 0}).to_list(20)
    return files

@api_router.get("/files/{file_id}/download")
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

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str, request: Request):
    await get_current_user(request)
    await db.files.update_one({"id": file_id}, {"$set": {"is_deleted": True}})
    return {"message": "Deleted"}

@api_router.post("/quick-inquiry")
async def create_quick_inquiry(inquiry: QuickInquiryCreate):
    doc = inquiry.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["status"] = "new"
    doc["type"] = "quick"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.inquiries.insert_one(doc)
    return {"message": "Schnellanfrage gesendet", "id": doc["id"]}

# --- FAQS ---
@api_router.get("/faqs")
async def get_faqs():
    return await db.faqs.find({}, {"_id": 0}).sort("order", 1).to_list(100)

# --- AVAILABILITY ---
@api_router.get("/availability")
async def get_availability():
    return await db.calendar_blocks.find({}, {"_id": 0}).to_list(10000)

@api_router.get("/availability/{date}")
async def check_date(date: str):
    total = await db.trucks.count_documents({"is_active": True})
    blocked = await db.calendar_blocks.count_documents({"date": date, "status": {"$in": ["blocked", "confirmed"]}})
    if blocked == 0:
        return {"date": date, "status": "available", "blocked": 0, "total": total}
    elif blocked >= total:
        return {"date": date, "status": "booked", "blocked": blocked, "total": total}
    return {"date": date, "status": "partial", "blocked": blocked, "total": total}

# --- ADMIN INQUIRIES ---
@api_router.get("/admin/inquiries")
async def admin_get_inquiries(request: Request):
    await get_current_user(request)
    return await db.inquiries.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)

@api_router.get("/admin/inquiries/{inquiry_id}")
async def admin_get_inquiry(inquiry_id: str, request: Request):
    await get_current_user(request)
    doc = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return doc

@api_router.put("/admin/inquiries/{inquiry_id}")
async def admin_update_inquiry(inquiry_id: str, update: InquiryStatusUpdate, request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    updates = {"status": update.status, "internal_notes": update.internal_notes, "updated_at": datetime.now(timezone.utc).isoformat()}
    # Auto-assign employees if provided
    if hasattr(update, 'assigned_employees') and update.assigned_employees is not None:
        updates["assigned_employees"] = update.assigned_employees
    result = await db.inquiries.update_one({"id": inquiry_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    # Auto-send offer email when status changes to offer_sent
    if update.status == "offer_sent":
        inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
        if inquiry and inquiry.get("email"):
            offer_html = build_offer_email(inquiry)
            background_tasks.add_task(send_email_background, inquiry["email"], "Ihr Angebot von TruckOnRoad", offer_html)
    # Send status notification email for other status changes
    elif update.status in ("in_review", "confirmed", "completed", "cancelled"):
        inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
        if inquiry and inquiry.get("email"):
            status_html = build_status_notification_email(inquiry, update.status)
            subject_map = {
                "in_review": "Ihre Anfrage wird geprueft",
                "confirmed": "Ihre Buchung ist bestaetigt!",
                "completed": "Event abgeschlossen – Vielen Dank!",
                "cancelled": "Anfrage storniert",
            }
            subject = f"{subject_map.get(update.status, 'Status-Update')} – TruckOnRoad"
            background_tasks.add_task(send_email_background, inquiry["email"], subject, status_html)
    return {"message": "Updated"}

@api_router.delete("/admin/inquiries/{inquiry_id}")
async def admin_delete_inquiry(inquiry_id: str, request: Request):
    await get_current_user(request)
    result = await db.inquiries.delete_one({"id": inquiry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}

@api_router.put("/admin/inquiries/{inquiry_id}/invoice")
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
    # Send invoice notification email
    if "invoice_status" in body and body["invoice_status"] not in ("none", ""):
        inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
        if inquiry and inquiry.get("email"):
            inv_html = build_invoice_notification_email(inquiry, body["invoice_status"], body.get("invoice_amount", inquiry.get("invoice_amount", 0)))
            subject_map = {
                "pending": "Rechnung erstellt",
                "sent": "Rechnung zugestellt",
                "paid": "Zahlung eingegangen – Danke!",
                "overdue": "Zahlungserinnerung",
            }
            subject = f"{subject_map.get(body['invoice_status'], 'Rechnungs-Update')} – TruckOnRoad"
            background_tasks.add_task(send_email_background, inquiry["email"], subject, inv_html)
    return {"message": "Invoice updated"}

# --- ADMIN CALENDAR ---
@api_router.get("/admin/calendar")
async def admin_get_calendar(request: Request):
    await get_current_user(request)
    return await db.calendar_blocks.find({}, {"_id": 0}).to_list(10000)

@api_router.post("/admin/calendar")
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

@api_router.delete("/admin/calendar/{block_id}")
async def admin_delete_block(block_id: str, request: Request):
    await get_current_user(request)
    result = await db.calendar_blocks.delete_one({"id": block_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}

# --- ADMIN FAQS ---
@api_router.post("/admin/faqs")
async def admin_create_faq(faq: FAQCreate, request: Request):
    await get_current_user(request)
    doc = faq.model_dump()
    doc["id"] = str(uuid.uuid4())
    await db.faqs.insert_one(doc)
    return {"message": "Created", "id": doc["id"]}

@api_router.put("/admin/faqs/{faq_id}")
async def admin_update_faq(faq_id: str, faq: FAQCreate, request: Request):
    await get_current_user(request)
    result = await db.faqs.update_one({"id": faq_id}, {"$set": faq.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}

@api_router.delete("/admin/faqs/{faq_id}")
async def admin_delete_faq(faq_id: str, request: Request):
    await get_current_user(request)
    result = await db.faqs.delete_one({"id": faq_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}

# --- ADMIN TRUCKS ---
@api_router.get("/admin/trucks")
async def admin_get_trucks(request: Request):
    await get_current_user(request)
    return await db.trucks.find({}, {"_id": 0}).sort("order", 1).to_list(100)

@api_router.put("/admin/trucks/{slug}")
async def admin_update_truck(slug: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("slug", None)
    result = await db.trucks.update_one({"slug": slug}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}

# --- ADMIN STATS ---
@api_router.get("/admin/stats")
async def admin_stats(request: Request):
    await get_current_user(request)
    total = await db.inquiries.count_documents({})
    new_count = await db.inquiries.count_documents({"status": "new"})
    confirmed = await db.inquiries.count_documents({"status": "confirmed"})
    trucks = await db.trucks.count_documents({"is_active": True})
    return {"total_inquiries": total, "new_inquiries": new_count, "confirmed": confirmed, "total_trucks": trucks}

# --- ADMIN SETTINGS ---
@api_router.get("/admin/settings")
async def admin_get_settings(request: Request):
    await get_current_user(request)
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    defaults = {
        "type": "general", "company_name": "TruckOnRoad",
        "company_address": "Bahnhofstrasse 75, 8620 Wetzikon",
        "company_phone": "+41 79 696 98 99", "company_email": "info@truckonroad.ch",
        "whatsapp_number": "+41796969899",
        "social_google_business": "", "social_instagram": "", "social_facebook": "",
        "social_tiktok": "", "social_linkedin": "",
        "google_verification": "",
        "event_reminder_days": 3,
        "auto_confirmation": False,
        "email_notifications": False, "notification_email": "",
        "smtp_host": "smtp.gmail.com", "smtp_port": 587,
        "smtp_email": "", "smtp_password": ""
    }
    if s:
        defaults.update(s)
    return defaults

@api_router.put("/admin/settings")
async def admin_update_settings(request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body["type"] = "general"
    await db.settings.update_one({"type": "general"}, {"$set": body}, upsert=True)
    return {"message": "Updated"}

@api_router.post("/admin/settings/test-email")
async def admin_test_email(request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    body = await request.json()
    to = body.get("to", "")
    if not to:
        raise HTTPException(status_code=400, detail="E-Mail-Adresse fehlt")
    background_tasks.add_task(send_email_background, to, "TruckOnRoad Test-E-Mail", "<h2>Test erfolgreich!</h2><p>Die E-Mail-Konfiguration funktioniert korrekt.</p>")
    return {"message": "Test-E-Mail wird gesendet"}

# --- PUBLIC SETTINGS (for contact page) ---
@api_router.get("/contact-info")
async def get_contact_info():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return {
        "company_name": (s or {}).get("company_name", "TruckOnRoad"),
        "address": (s or {}).get("company_address", "Bahnhofstrasse 75, 8620 Wetzikon"),
        "phone": (s or {}).get("company_phone", "+41 79 696 98 99"),
        "email": (s or {}).get("company_email", "info@truckonroad.ch"),
        "whatsapp": (s or {}).get("whatsapp_number", "+41796969899"),
    }

# --- PUBLIC STRUCTURED DATA (JSON-LD for SEO & AI Search) ---
@api_router.get("/seo/structured-data")
async def get_structured_data():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
    same_as = [v for k in ["social_google_business", "social_instagram", "social_facebook", "social_tiktok", "social_linkedin"] if (v := s.get(k, ""))]
    result = {
        "@context": "https://schema.org",
        "@type": "FoodEstablishment",
        "name": s.get("company_name", "TruckOnRoad"),
        "alternateName": f"{s.get('company_name', 'TruckOnRoad')} - Premium Foodtrucks",
        "description": "Premium Foodtrucks für Festivals, Firmenanlässe und Private Events in der ganzen Schweiz. 6 einzigartige Truck-Konzepte: Burger, Chicken Burger, Bowls, Pocket Bowls, Empanadas und Retro Trailer.",
        "url": "https://truckonroad.ch",
        "telephone": s.get("company_phone", "+41 79 696 98 99"),
        "email": s.get("company_email", "info@truckonroad.ch"),
        "servesCuisine": ["Burger", "Bowls", "Empanadas", "Street Food"],
        "priceRange": "$$",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": s.get("company_address", "Bahnhofstrasse 75, 8620 Wetzikon").split(",")[0].strip(),
            "addressLocality": s.get("company_address", "Bahnhofstrasse 75, 8620 Wetzikon").split(",")[-1].strip() if "," in s.get("company_address", "") else "Wetzikon",
            "addressCountry": "CH"
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 47.3769, "longitude": 8.5417},
        "areaServed": {"@type": "Country", "name": "Schweiz"},
        "sameAs": same_as,
        "hasMenu": {
            "@type": "Menu",
            "hasMenuSection": [
                {"@type": "MenuSection", "name": "Burger Truck", "description": "Klassische und kreative Burger vom Foodtruck"},
                {"@type": "MenuSection", "name": "Bowl Truck", "description": "Frische Bowls mit saisonalen Zutaten"},
                {"@type": "MenuSection", "name": "Empanadas Truck", "description": "Handgemachte Empanadas mit verschiedenen Füllungen"}
            ]
        },
        "additionalType": "https://schema.org/CateringService",
        "knowsAbout": ["Foodtruck Catering", "Festival Catering", "Firmenanlass Catering", "Hochzeit Catering", "Event Catering Schweiz"],
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Foodtruck Catering für Festivals", "description": "Premium Foodtruck-Catering für Open-Air-Festivals und Grossveranstaltungen in der Schweiz"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Foodtruck für Firmenanlässe", "description": "Individuelles Foodtruck-Erlebnis für Firmenevents, Teambuilding und Firmenanlässe"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Foodtruck für Private Events", "description": "Exklusives Foodtruck-Catering für Hochzeiten, Geburtstage und private Feiern"}}
        ]
    }
    # Add aggregateRating from reviews
    reviews = await db.reviews.find({"is_active": True}, {"_id": 0}).to_list(500)
    if reviews:
        ratings = [r.get("rating", 5) for r in reviews]
        result["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(sum(ratings) / len(ratings), 1),
            "reviewCount": len(ratings),
            "bestRating": 5,
            "worstRating": 1
        }
        result["review"] = [
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": r.get("author", "Kunde")},
                "reviewRating": {"@type": "Rating", "ratingValue": r.get("rating", 5)},
                "reviewBody": r.get("text", ""),
                "datePublished": r.get("date", "")
            }
            for r in reviews[:5]
        ]
    return result

# --- REVIEWS ---
@api_router.get("/reviews")
async def get_public_reviews():
    reviews = await db.reviews.find({"is_active": True}, {"_id": 0}).sort("date", -1).to_list(50)
    return reviews

@api_router.get("/admin/reviews")
async def admin_get_reviews(request: Request):
    await get_current_user(request)
    reviews = await db.reviews.find({}, {"_id": 0}).sort("date", -1).to_list(200)
    return reviews

@api_router.post("/admin/reviews")
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
        "is_active": body.get("is_active", True),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.reviews.insert_one(review)
    review.pop("_id", None)
    return review

@api_router.put("/admin/reviews/{review_id}")
async def admin_update_review(review_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("id", None)
    if "rating" in body:
        body["rating"] = max(1, min(5, int(body["rating"])))
    await db.reviews.update_one({"id": review_id}, {"$set": body})
    return {"message": "Updated"}

@api_router.delete("/admin/reviews/{review_id}")
async def admin_delete_review(review_id: str, request: Request):
    await get_current_user(request)
    await db.reviews.delete_one({"id": review_id})
    return {"message": "Deleted"}

@api_router.get("/robots.txt")
async def robots_txt():
    content = """User-agent: *
Allow: /
Sitemap: https://truckonroad.ch/api/sitemap.xml

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /
"""
    return FastAPIResponse(content=content, media_type="text/plain")

@api_router.get("/seo/google-verification")
async def google_verification():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
    return {"code": s.get("google_verification", "")}

@api_router.get("/sitemap.xml")
async def sitemap():
    base = "https://truckonroad.ch"
    trucks_list = await db.trucks.find({"is_active": True}, {"slug": 1, "_id": 0}).to_list(100)
    urls = [
        (base + "/", "1.0", "weekly"),
        (base + "/fuer-veranstalter", "0.8", "monthly"),
        (base + "/private-events", "0.8", "monthly"),
        (base + "/ueber-uns", "0.7", "monthly"),
        (base + "/kontakt", "0.7", "monthly"),
        (base + "/anfrage", "0.9", "weekly"),
        (base + "/faq", "0.6", "monthly"),
    ]
    for t in trucks_list:
        urls.append((f"{base}/trucks/{t['slug']}", "0.7", "monthly"))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, pri, freq in urls:
        xml += f"  <url><loc>{loc}</loc><priority>{pri}</priority><changefreq>{freq}</changefreq></url>\n"
    xml += "</urlset>"
    return FastAPIResponse(content=xml, media_type="application/xml")

# --- PDF DOWNLOAD ---
@api_router.get("/download/veranstalter-pdf")
async def download_veranstalter_pdf():
    trucks = await db.trucks.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 15, "TRUCKONROAD", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Premium Foodtrucks fuer jeden Anlass", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Bahnhofstrasse 75, 8620 Wetzikon  |  +41 79 696 98 99  |  info@truckonroad.ch", ln=True, align="C")
    pdf.ln(10)
    pdf.set_draw_color(77, 182, 172)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Unsere Truck-Konzepte", ln=True)
    pdf.ln(3)
    for t in trucks:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(77, 182, 172)
        pdf.cell(0, 8, t.get("name_de", ""), ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        desc = t.get("desc_de", "")
        if desc:
            pdf.multi_cell(0, 5, desc)
        pdf.ln(2)
        menu = t.get("menu_de", [])
        if menu:
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 5, "Menu: " + ", ".join(menu), ln=True)
        cap = t.get("capacity", "")
        if cap:
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 5, f"Kapazitaet: {cap}", ln=True)
        space = t.get("space_required", "")
        if space:
            pdf.cell(0, 5, f"Platzbedarf: {space}", ln=True)
        pdf.ln(5)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Warum TruckOnRoad?", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    reasons = [
        ("Schnelle Ausgabe", "Bis zu 300 Gaeste pro Stunde - auch bei Grossevents kein Stau."),
        ("Mehrere Trucks gleichzeitig", "Koordinierte Logistik und Personal fuer parallelen Einsatz."),
        ("Professioneller Auftritt", "Einheitliches Branding, klare Ablaeufe, erfahrenes Team."),
        ("Auffaelliges Design", "Unsere Trucks sind Hingucker und machen Events unvergesslich."),
    ]
    for title, text in reasons:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(77, 182, 172)
        pdf.cell(0, 7, title, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, text)
        pdf.ln(3)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Kontakt & Anfrage", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "TruckOnRoad", ln=True)
    pdf.cell(0, 6, "Bahnhofstrasse 75, 8620 Wetzikon", ln=True)
    pdf.cell(0, 6, "+41 79 696 98 99", ln=True)
    pdf.cell(0, 6, "info@truckonroad.ch", ln=True)
    pdf.cell(0, 6, "www.truckonroad.ch", ln=True)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return FastAPIResponse(content=buf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=TruckOnRoad_Veranstalter.pdf"})

# --- EMAIL PREVIEW ---
@api_router.get("/admin/email-preview")
async def admin_email_preview(request: Request):
    await get_current_user(request)
    sample = {
        "first_name": "Max", "last_name": "Mustermann",
        "email": "max@beispiel.ch", "phone": "+41 79 123 45 67",
        "event_date": "15.06.2026", "location": "Zürich, Sechseläutenplatz",
        "guest_count": 200, "event_type": "Firmenanlass",
        "selected_trucks": ["Burger Truck", "Bowl Truck"], "budget": "CHF 5'000 – 10'000",
    }
    return {
        "confirmation": build_confirmation_email(sample),
        "notification": build_admin_notification_email(sample),
        "status_confirmed": build_status_notification_email(sample, "confirmed"),
        "status_completed": build_status_notification_email(sample, "completed"),
        "invoice_sent": build_invoice_notification_email(sample, "sent", 4500),
        "invoice_paid": build_invoice_notification_email(sample, "paid", 4500),
        "file_upload": build_file_upload_notification_email(sample, "Event-Plan_2026.pdf"),
        "event_reminder": build_event_reminder_email(sample, 3),
    }

# --- ADMIN FAQS GET ---
@api_router.get("/admin/faqs")
async def admin_get_faqs(request: Request):
    await get_current_user(request)
    return await db.faqs.find({}, {"_id": 0}).sort("order", 1).to_list(100)

# --- ADMIN EMPLOYEES ---
@api_router.get("/admin/employees")
async def admin_get_employees(request: Request):
    await get_current_user(request)
    return await db.employees.find({}, {"_id": 0}).sort("name", 1).to_list(500)

@api_router.post("/admin/employees")
async def admin_create_employee(emp: EmployeeCreate, request: Request):
    await get_current_user(request)
    doc = emp.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.employees.insert_one(doc)
    return {"message": "Created", "id": doc["id"]}

@api_router.put("/admin/employees/{emp_id}")
async def admin_update_employee(emp_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("id", None)
    result = await db.employees.update_one({"id": emp_id}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}

@api_router.delete("/admin/employees/{emp_id}")
async def admin_delete_employee(emp_id: str, request: Request):
    await get_current_user(request)
    result = await db.employees.delete_one({"id": emp_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}

# --- OFFER PDF ---
@api_router.get("/admin/inquiries/{inquiry_id}/offer-pdf")
async def admin_offer_pdf(inquiry_id: str, request: Request):
    await get_current_user(request)
    inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
    if not inquiry:
        raise HTTPException(status_code=404, detail="Not found")
    pdf_bytes = generate_offer_pdf(inquiry)
    name = f"{inquiry.get('first_name', '')}_{inquiry.get('last_name', '')}".strip("_") or "Anfrage"
    return FastAPIResponse(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Angebot_{name}.pdf"})

# --- EXPORT ---
@api_router.get("/admin/export/{data_type}")
async def admin_export(data_type: str, format: str = "csv", request: Request = None):
    await get_current_user(request)
    import csv as csv_module
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
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page("L")
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"TruckOnRoad - {data_type.title()} Export", ln=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 5, f"Erstellt: {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')}", ln=True)
        pdf.ln(5)
        col_w = 277 / min(len(fields), 7)
        display_fields = fields[:7]
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_fill_color(240, 240, 240)
        for f in display_fields:
            pdf.cell(col_w, 6, f.replace("_", " ").title(), 1, 0, "C", True)
        pdf.ln()
        pdf.set_font("Helvetica", "", 7)
        for doc in docs[:200]:
            for f in display_fields:
                val = doc.get(f, "")
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                pdf.cell(col_w, 5, str(val)[:40], 1, 0)
            pdf.ln()
        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        return FastAPIResponse(content=buf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={data_type}_export.pdf"})

# --- INSTAGRAM GALLERY ---
@api_router.get("/instagram-gallery")
async def get_instagram_gallery():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return {
        "username": (s or {}).get("instagram_username", ""),
        "images": (s or {}).get("instagram_images", []),
    }

# --- FINANCE: Update inquiry financials ---
@api_router.put("/admin/inquiries/{inquiry_id}/finance")
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

# --- FINANCE: Dashboard overview ---
@api_router.get("/admin/finance/overview")
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
        # By month
        date_str = inq.get("event_date", "")
        if date_str and date_str != "-":
            month_key = date_str[:7]
            if month_key not in by_month:
                by_month[month_key] = {"revenue": 0, "costs": 0, "count": 0}
            by_month[month_key]["revenue"] += rev
            by_month[month_key]["costs"] += costs
            by_month[month_key]["count"] += 1
        # By truck
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

# --- ROUTING: Geocode address ---
BASE_LOCATION = {"lat": 47.3231, "lon": 8.7994, "name": "Wetzikon"}

@api_router.get("/admin/geocode")
async def admin_geocode(address: str, request: Request):
    await get_current_user(request)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1, "countrycodes": "ch"},
            headers={"User-Agent": "TruckOnRoad/1.0"},
            timeout=10,
        )
        results = resp.json()
        if not results:
            return {"found": False}
        r = results[0]
        return {"found": True, "lat": float(r["lat"]), "lon": float(r["lon"]), "display_name": r["display_name"]}

@api_router.get("/admin/route")
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

@api_router.get("/admin/route/optimize")
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

# --- ROUTING: Save/get coordinates for inquiry ---
@api_router.put("/admin/inquiries/{inquiry_id}/coords")
async def admin_update_coords(inquiry_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    updates = {"lat": body.get("lat"), "lon": body.get("lon"), "updated_at": datetime.now(timezone.utc).isoformat()}
    result = await db.inquiries.update_one({"id": inquiry_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Coordinates updated"}

# --- ROUTING: Get events with locations for map ---
@api_router.get("/admin/events-map")
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

@api_router.post("/admin/send-reminders")
async def admin_trigger_reminders(request: Request):
    await get_current_user(request)
    await send_event_reminders()
    return {"message": "Erinnerungen geprüft und gesendet"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000"), "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TRUCKS_SEED = [
    {
        "slug": "burger-truck", "name_de": "Burger Truck", "name_en": "Burger Truck",
        "tagline_de": "Classic \u00b7 Chicken \u00b7 Veggie \u2014 bis 300 G\u00e4ste/h",
        "tagline_en": "Classic \u00b7 Chicken \u00b7 Veggie \u2014 up to 300 guests/h",
        "description_de": "Unser Burger Truck ist auf schnelle, hochwertige Ausgabe ausgelegt und ideal f\u00fcr Events mit hoher Besucherzahl. Saftige Patties, frische Zutaten und unser Signature-Style machen jeden Burger zu einem Erlebnis.",
        "description_en": "Our Burger Truck is designed for fast, high-quality service and is ideal for events with large crowds. Juicy patties, fresh ingredients, and our signature style make every burger an experience.",
        "image": "https://images.unsplash.com/photo-1565123409695-7b5ef63a2efb?w=1200&q=80",
        "tag": "Flagship",
        "menu_de": ["Classic Burger", "Chicken Burger", "Veggie Burger", "Loaded Fries"],
        "menu_en": ["Classic Burger", "Chicken Burger", "Veggie Burger", "Loaded Fries"],
        "suitable_for_de": ["Festivals", "Firmenanl\u00e4sse", "Private Events", "Messen"],
        "suitable_for_en": ["Festivals", "Corporate Events", "Private Events", "Trade Fairs"],
        "capacity": "bis 300 G\u00e4ste/h", "space_required": "6m x 3m", "power": "230V / 16A",
        "water": "Wasseranschluss ben\u00f6tigt", "setup_time": "ca. 60 Min",
        "is_wide": True, "is_active": True, "order": 1
    },
    {
        "slug": "chicken-burger-truck", "name_de": "Chicken Burger Truck", "name_en": "Chicken Burger Truck",
        "tagline_de": "Knusprig \u00b7 W\u00fcrzig \u00b7 Einzigartig",
        "tagline_en": "Crispy \u00b7 Spicy \u00b7 Unique",
        "description_de": "Unser Chicken Burger Truck bietet ein spezialisiertes Konzept rund um knusprige Chicken Burger mit hauseigenen Marinaden und frischen Saucen.",
        "description_en": "Our Chicken Burger Truck offers a specialized concept centered around crispy chicken burgers with house-made marinades and fresh sauces.",
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80",
        "tag": "",
        "menu_de": ["Classic Chicken Burger", "Spicy Chicken", "BBQ Chicken", "Veggie Alternative"],
        "menu_en": ["Classic Chicken Burger", "Spicy Chicken", "BBQ Chicken", "Veggie Alternative"],
        "suitable_for_de": ["Festivals", "Firmenanl\u00e4sse", "Streetfood Events"],
        "suitable_for_en": ["Festivals", "Corporate Events", "Street Food Events"],
        "capacity": "bis 250 G\u00e4ste/h", "space_required": "5m x 3m", "power": "230V / 16A",
        "water": "Wasseranschluss ben\u00f6tigt", "setup_time": "ca. 45 Min",
        "is_wide": False, "is_active": True, "order": 2
    },
    {
        "slug": "bowl-truck", "name_de": "Bowl Truck", "name_en": "Bowl Truck",
        "tagline_de": "Signature \u00b7 Protein \u00b7 Veggie",
        "tagline_en": "Signature \u00b7 Protein \u00b7 Veggie",
        "description_de": "Unser Bowl Truck liefert frische, gesunde Bowls mit saisonalen Zutaten. Ideal f\u00fcr gesundheitsbewusste G\u00e4ste und moderne Events.",
        "description_en": "Our Bowl Truck delivers fresh, healthy bowls with seasonal ingredients. Ideal for health-conscious guests and modern events.",
        "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80",
        "tag": "",
        "menu_de": ["Signature Bowl", "Protein Bowl", "Veggie Bowl", "Vegan Bowl"],
        "menu_en": ["Signature Bowl", "Protein Bowl", "Veggie Bowl", "Vegan Bowl"],
        "suitable_for_de": ["Firmenanl\u00e4sse", "Messen", "Gesundheits-Events", "Private Events"],
        "suitable_for_en": ["Corporate Events", "Trade Fairs", "Health Events", "Private Events"],
        "capacity": "bis 200 G\u00e4ste/h", "space_required": "5m x 3m", "power": "230V / 16A",
        "water": "Wasseranschluss ben\u00f6tigt", "setup_time": "ca. 45 Min",
        "is_wide": False, "is_active": True, "order": 3
    },
    {
        "slug": "pocket-bowl-truck", "name_de": "Pocket Bowl Truck", "name_en": "Pocket Bowl Truck",
        "tagline_de": "Ideal f\u00fcr hohe Frequenz",
        "tagline_en": "Ideal for high frequency",
        "description_de": "Der Pocket Bowl Truck ist unser schnellstes Konzept. Kleine, handliche Bowls ideal f\u00fcr Events mit schnellem Durchlauf und hoher G\u00e4stefrequenz.",
        "description_en": "The Pocket Bowl Truck is our fastest concept. Small, handy bowls ideal for events with fast throughput and high guest frequency.",
        "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=80",
        "tag": "Speed",
        "menu_de": ["Pocket Bowl Classic", "Pocket Bowl Spicy", "Pocket Bowl Veggie"],
        "menu_en": ["Pocket Bowl Classic", "Pocket Bowl Spicy", "Pocket Bowl Veggie"],
        "suitable_for_de": ["Festivals", "Grossevents", "Messen", "Sportanl\u00e4sse"],
        "suitable_for_en": ["Festivals", "Large Events", "Trade Fairs", "Sports Events"],
        "capacity": "bis 400 G\u00e4ste/h", "space_required": "5m x 3m", "power": "230V / 16A",
        "water": "Wasseranschluss ben\u00f6tigt", "setup_time": "ca. 40 Min",
        "is_wide": False, "is_active": True, "order": 4
    },
    {
        "slug": "empanadas-truck", "name_de": "Empanadas Truck", "name_en": "Empanadas Truck",
        "tagline_de": "Herzhaft \u00b7 Vegetarisch \u00b7 Schnell",
        "tagline_en": "Savory \u00b7 Vegetarian \u00b7 Fast",
        "description_de": "Unser Empanadas Truck bringt s\u00fcdamerikanisches Flair auf jedes Event. Handgemachte Empanadas in verschiedenen Sorten \u2013 herzhaft und vegetarisch.",
        "description_en": "Our Empanadas Truck brings South American flair to every event. Handmade empanadas in various flavors \u2013 savory and vegetarian.",
        "image": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=600&q=80",
        "tag": "",
        "menu_de": ["Classic Beef", "Chicken Empanada", "Veggie Empanada", "Cheese Empanada"],
        "menu_en": ["Classic Beef", "Chicken Empanada", "Veggie Empanada", "Cheese Empanada"],
        "suitable_for_de": ["Festivals", "Private Events", "Streetfood M\u00e4rkte", "Firmenanl\u00e4sse"],
        "suitable_for_en": ["Festivals", "Private Events", "Street Food Markets", "Corporate Events"],
        "capacity": "bis 300 G\u00e4ste/h", "space_required": "5m x 3m", "power": "230V / 16A",
        "water": "Wasseranschluss ben\u00f6tigt", "setup_time": "ca. 45 Min",
        "is_wide": False, "is_active": True, "order": 5
    },
    {
        "slug": "retro-trailer", "name_de": "Retro Trailer", "name_en": "Retro Trailer",
        "tagline_de": "Pferdeanh\u00e4nger \u00b7 Vintage Charme",
        "tagline_en": "Horse Trailer \u00b7 Vintage Charm",
        "description_de": "Unser Retro Trailer im Pferdeanh\u00e4nger-Stil ist ein echter Hingucker. Perfekt f\u00fcr Hochzeiten, Privatanl\u00e4sse und \u00fcberall dort, wo Charme und Stil gefragt sind.",
        "description_en": "Our Retro Trailer in horse trailer style is a real eye-catcher. Perfect for weddings, private events, and wherever charm and style are needed.",
        "image": "https://images.unsplash.com/photo-1509315811345-672d83ef2fbc?w=600&q=80",
        "tag": "Retro",
        "menu_de": ["Individuell nach Absprache", "Kaffee & Desserts", "Alpine Spezialit\u00e4ten"],
        "menu_en": ["Customized by arrangement", "Coffee & Desserts", "Alpine Specialties"],
        "suitable_for_de": ["Hochzeiten", "Private Events", "Firmenfeiern", "M\u00e4rkte"],
        "suitable_for_en": ["Weddings", "Private Events", "Corporate Celebrations", "Markets"],
        "capacity": "bis 150 G\u00e4ste/h", "space_required": "4m x 2.5m", "power": "230V / 16A",
        "water": "Optional", "setup_time": "ca. 30 Min",
        "is_wide": False, "is_active": True, "order": 6
    }
]

FAQS_SEED = [
    {"id": str(uuid.uuid4()), "question_de": "Wie fr\u00fch muss man buchen?", "answer_de": "Wir empfehlen mindestens 4\u20138 Wochen im Voraus, bei grossen Festivals gerne fr\u00fcher. Kurzfristige Anfragen pr\u00fcfen wir ebenfalls gerne.", "question_en": "How far in advance should I book?", "answer_en": "We recommend at least 4-8 weeks in advance, for large festivals preferably earlier. We're also happy to review short-notice inquiries.", "order": 1},
    {"id": str(uuid.uuid4()), "question_de": "Wie viele G\u00e4ste sind m\u00f6glich?", "answer_de": "Einzelne Trucks sind auf bis zu 300 G\u00e4ste/Stunde ausgelegt. Bei gr\u00f6sseren Events k\u00f6nnen mehrere Trucks gleichzeitig eingesetzt werden.", "question_en": "How many guests are possible?", "answer_en": "Individual trucks can serve up to 300 guests per hour. For larger events, multiple trucks can be deployed simultaneously.", "order": 2},
    {"id": str(uuid.uuid4()), "question_de": "Kommt ihr in die ganze Schweiz?", "answer_de": "Ja. Unser Heimgebiet ist Z\u00fcrich, Wetzikon und der Z\u00fcrcher Oberland, aber wir fahren f\u00fcr Events in die ganze Schweiz \u2013 je nach Aufwand mit Anfahrtspauschale.", "question_en": "Do you come to all of Switzerland?", "answer_en": "Yes. Our home area is Zurich, Wetzikon and the Zurich Oberland, but we travel across Switzerland for events \u2013 with a travel surcharge depending on distance.", "order": 3},
    {"id": str(uuid.uuid4()), "question_de": "Braucht ihr Strom und Wasser?", "answer_de": "Je nach Truck unterschiedlich. Die genauen technischen Anforderungen geben wir euch nach der Anfrage mit den Unterlagen weiter.", "question_en": "Do you need power and water?", "answer_en": "It varies by truck. We'll provide detailed technical requirements with the documentation after your inquiry.", "order": 4},
    {"id": str(uuid.uuid4()), "question_de": "Gibt es vegetarische/vegane Optionen?", "answer_de": "Ja, bei allen Konzepten sind vegetarische Optionen verf\u00fcgbar. Vegane Anpassungen sind je nach Konzept m\u00f6glich \u2013 bitte beim Anfragen angeben.", "question_en": "Are there vegetarian/vegan options?", "answer_en": "Yes, vegetarian options are available with all concepts. Vegan adaptations are possible depending on the concept \u2013 please specify when inquiring.", "order": 5},
    {"id": str(uuid.uuid4()), "question_de": "Was kostet ein Foodtruck-Einsatz?", "answer_de": "Der Preis h\u00e4ngt von G\u00e4stezahl, Ort, Einsatzdauer und Konzept ab. Wir kalkulieren individuell und senden euch eine transparente Offerte.", "question_en": "What does a food truck deployment cost?", "answer_en": "The price depends on guest count, location, duration, and concept. We calculate individually and send you a transparent offer.", "order": 6},
    {"id": str(uuid.uuid4()), "question_de": "Kann man mehrere Trucks buchen?", "answer_de": "Ja, genau das ist unsere St\u00e4rke. Ihr k\u00f6nnt mehrere Konzepte kombinieren und so f\u00fcr Abwechslung und k\u00fcrzere Wartezeiten sorgen.", "question_en": "Can I book multiple trucks?", "answer_en": "Yes, that's exactly our strength. You can combine multiple concepts to provide variety and shorter wait times.", "order": 7},
    {"id": str(uuid.uuid4()), "question_de": "Was passiert bei schlechtem Wetter?", "answer_de": "Unsere Trucks sind grunds\u00e4tzlich wetterfest. Bei extremen Bedingungen besprechen wir gemeinsam Alternativen. Details regeln wir im Vertrag.", "question_en": "What happens in bad weather?", "answer_en": "Our trucks are generally weatherproof. In extreme conditions, we discuss alternatives together. Details are regulated in the contract.", "order": 8}
]


# --- EVENT REMINDER BACKGROUND TASK ---
import asyncio

async def send_event_reminders():
    """Check for upcoming events and send reminder emails."""
    try:
        settings = await get_email_settings()
        reminder_days = settings.get("event_reminder_days", 3)
        if not reminder_days or reminder_days < 1:
            return
        target_date = (datetime.now(timezone.utc) + timedelta(days=reminder_days)).strftime("%Y-%m-%d")
        inquiries = await db.inquiries.find({
            "event_date": target_date,
            "status": {"$in": ["confirmed", "offer_sent"]},
        }, {"_id": 0}).to_list(100)
        for inq in inquiries:
            already_sent = await db.reminders.find_one({"inquiry_id": inq["id"], "type": "event_reminder"})
            if already_sent:
                continue
            if inq.get("email"):
                html = build_event_reminder_email(inq, reminder_days)
                try:
                    send_email_sync(inq["email"], f"Noch {reminder_days} Tage bis zu Ihrem Event! – TruckOnRoad", html, settings)
                except Exception:
                    pass
                await db.reminders.insert_one({"inquiry_id": inq["id"], "type": "event_reminder", "sent_at": datetime.now(timezone.utc).isoformat()})
                logger.info(f"Event reminder sent for inquiry {inq['id']} to {inq['email']}")
    except Exception as e:
        logger.warning(f"Event reminder check failed: {e}")

def send_email_sync(to_email, subject, html_body, settings):
    """Synchronous email sending for background tasks."""
    smtp_user = settings.get("smtp_user", "")
    smtp_pass = settings.get("smtp_password", "")
    smtp_host = settings.get("smtp_host", "smtp.gmail.com")
    smtp_port = settings.get("smtp_port", 587)
    if not smtp_user or not smtp_pass:
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())

async def event_reminder_loop():
    """Background loop that checks for event reminders every 6 hours."""
    while True:
        await asyncio.sleep(6 * 3600)  # Check every 6 hours
        await send_event_reminders()


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.trucks.create_index("slug", unique=True)
    await db.inquiries.create_index("id")
    await db.calendar_blocks.create_index([("truck_slug", 1), ("date", 1)])
    await db.login_attempts.create_index("identifier")

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@truckonroad.ch")
    admin_password = os.environ.get("ADMIN_PASSWORD", "TruckOnRoad2026!")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({"email": admin_email, "password_hash": hash_password(admin_password), "name": "Admin", "role": "admin", "created_at": datetime.now(timezone.utc).isoformat()})
        logger.info(f"Admin seeded: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})

    for t in TRUCKS_SEED:
        existing_truck = await db.trucks.find_one({"slug": t["slug"]})
        if not existing_truck:
            await db.trucks.insert_one(t.copy())
            logger.info(f"Truck seeded: {t['slug']}")
        else:
            await db.trucks.update_one({"slug": t["slug"]}, {"$set": {"image": t["image"]}})
            logger.info(f"Truck image updated: {t['slug']}")

    if await db.faqs.count_documents({}) == 0:
        for f in FAQS_SEED:
            await db.faqs.insert_one(f.copy())
        logger.info("FAQs seeded")

    Path("/app/memory").mkdir(exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"# Test Credentials\n\n## Admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: admin\n\n## Customer (Test)\n- Register at /konto/registrieren\n- Or use API: POST /api/auth/register\n\n## Auth Endpoints\n- POST /api/auth/login\n- POST /api/auth/register\n- POST /api/auth/logout\n- GET /api/auth/me\n- POST /api/auth/refresh\n\n## Customer Portal Endpoints\n- GET /api/customer/inquiries\n- GET /api/customer/inquiries/{{id}}\n- GET /api/customer/profile\n")
    logger.info("Startup complete")
    # Init object storage
    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.warning(f"Object storage init failed (will retry on first upload): {e}")
    # Start event reminder background task
    import asyncio
    asyncio.create_task(event_reminder_loop())

@app.on_event("shutdown")
async def shutdown():
    client.close()
