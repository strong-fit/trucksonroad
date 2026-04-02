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
import json as json_mod
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
    lang: Optional[str] = "de"

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

def build_confirmation_email(inquiry: dict, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{t['thank_you'].format(name=name)}</h2>
        <p style="color:#6b6b64;line-height:1.6;">{t['inquiry_received']}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;"><strong>{t['event_date']}:</strong> {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['guests']}:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['event_type']}:</strong> {inquiry.get('event_type', inquiry.get('concept', '-'))}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">{t['questions_contact']}</p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

def build_admin_notification_email(inquiry: dict, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    trucks = ', '.join(inquiry.get('selected_trucks', [])) or '-'
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['new_inquiry']}</span>
      </div>
      <div style="padding:1.5rem 2rem;">
        <h3 style="color:#1a1a18;margin:0 0 1rem;">{t['new_inquiry_from'].format(name=name)}</h3>
        <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
          <tr><td style="padding:0.4rem 0;color:#6b6b64;width:120px;">{t['name']}</td><td>{name}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['email']}</td><td>{inquiry.get('email', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['phone']}</td><td>{inquiry.get('phone', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['event_date']}</td><td>{inquiry.get('event_date', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['location']}</td><td>{inquiry.get('location', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['guests']}</td><td>{inquiry.get('guest_count', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['event_type']}</td><td>{inquiry.get('event_type', inquiry.get('concept', '-'))}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['trucks']}</td><td>{trucks}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['budget']}</td><td>{inquiry.get('budget', '-')}</td></tr>
        </table>
      </div>
    </div>"""

def build_offer_email(inquiry: dict, lang: str = "de") -> str:
    t = get_email_t(lang)
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
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{t['your_offer'].format(name=name)}</h2>
        <p style="color:#6b6b64;line-height:1.6;">{t['offer_intro']}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;"><strong>{t['event_date']}:</strong> {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['guests']}:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['trucks']}:</strong> {trucks}</p>
          <p style="margin:0.3rem 0;"><strong>{t['event_type']}:</strong> {inquiry.get('event_type', inquiry.get('concept', '-'))}</p>
        </div>
        <p style="color:#6b6b64;line-height:1.6;">{t['offer_follow_up']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1.5rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
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

# --- MULTILINGUAL EMAIL/PDF TRANSLATIONS ---
EMAIL_I18N = {
    "de": {
        "thank_you": "Vielen Dank fuer Ihre Anfrage, {name}!",
        "inquiry_received": "Wir haben Ihre Anfrage erhalten und melden uns innerhalb von 24 Stunden mit einem individuellen Angebot.",
        "event_date": "Event-Datum", "location": "Ort", "guests": "Gaeste", "event_type": "Eventtyp",
        "trucks": "Trucks", "budget": "Budget", "questions_contact": "Bei Fragen erreichen Sie uns jederzeit unter info@truckonroad.ch oder +41 79 696 98 99.",
        "greeting": "Herzliche Gruesse", "team": "TruckOnRoad Team",
        "new_inquiry": "NEUE ANFRAGE", "new_inquiry_from": "Neue Anfrage von {name}",
        "name": "Name", "email": "E-Mail", "phone": "Telefon",
        "your_offer": "Ihr Angebot, {name}", "offer_intro": "Vielen Dank fuer Ihr Interesse! Basierend auf Ihrer Anfrage haben wir folgendes Angebot fuer Sie zusammengestellt:",
        "offer_follow_up": "Wir melden uns in Kuerze mit den detaillierten Konditionen. Bei Fragen stehen wir Ihnen gerne zur Verfuegung.",
        "status_update": "STATUS-UPDATE", "hello": "Hallo {name},",
        "status_in_review": "Ihre Anfrage wird aktuell von unserem Team geprueft. Wir melden uns in Kuerze bei Ihnen.",
        "status_offer_sent": "Wir haben ein Angebot fuer Sie erstellt. Bitte pruefen Sie die Details und melden Sie sich bei Fragen.",
        "status_confirmed": "Ihre Buchung ist bestaetigt! Wir freuen uns auf Ihren Event.",
        "status_completed": "Vielen Dank fuer Ihren Auftrag! Wir hoffen, der Event war ein voller Erfolg.",
        "status_cancelled": "Ihre Anfrage wurde leider storniert. Bei Fragen kontaktieren Sie uns gerne.",
        "status_default": "Der Status Ihrer Anfrage wurde aktualisiert: {status}",
        "event": "Event", "at": "am",
        "invoice_label": "RECHNUNG", "invoice_word": "Rechnung",
        "inv_pending": "Fuer Ihren Event wurde eine Rechnung erstellt.",
        "inv_sent": "Wir haben Ihnen eine Rechnung zugesendet. Bitte beachten Sie die Zahlungsfrist.",
        "inv_paid": "Vielen Dank! Ihre Zahlung ist bei uns eingegangen.",
        "inv_overdue": "Ihre Rechnung ist ueberfaellig. Bitte ueberpruefen Sie die Zahlung.",
        "inv_default": "Ihr Rechnungsstatus wurde aktualisiert: {status}",
        "new_file": "NEUE DATEI", "file_added": "Wir haben eine neue Datei zu Ihrer Anfrage hinzugefuegt:",
        "file_download": "Sie koennen diese Datei in Ihrem Kundenportal herunterladen.",
        "reminder": "ERINNERUNG", "days_until": "Nur noch {days} Tage bis zu Ihrem Event!",
        "ready_for_event": "Wir sind bereit und freuen uns auf Ihren Event! Bei letzten Fragen erreichen Sie uns unter info@truckonroad.ch oder +41 79 696 98 99.",
        "subject_inquiry": "Anfrage erhalten", "subject_offer": "Ihr Angebot von TruckOnRoad",
        "subject_confirmed": "Ihre Buchung ist bestaetigt!", "subject_completed": "Event abgeschlossen",
        "subject_cancelled": "Anfrage storniert", "subject_status": "Status-Update",
        "subject_inv_pending": "Rechnung erstellt", "subject_inv_sent": "Rechnung zugestellt",
        "subject_inv_paid": "Zahlung erhalten", "subject_inv_overdue": "Rechnung ueberfaellig",
        "subject_reminder": "Noch {days} Tage bis zu Ihrem Event!",
        "pdf_offer": "Angebot", "pdf_created": "Erstellt am", "pdf_inquiry_nr": "Anfrage-Nr.",
        "pdf_customer": "Kundendaten", "pdf_event_details": "Event-Details", "pdf_indoor": "Indoor/Outdoor",
        "pdf_remarks": "Bemerkungen", "pdf_disclaimer": "Dieses Angebot ist unverbindlich und 30 Tage gueltig. Fuer Fragen stehen wir Ihnen gerne zur Verfuegung.",
        "pdf_company": "Firma", "pdf_date": "Datum",
        "status_labels": {"new": "Neu", "in_review": "In Pruefung", "offer_sent": "Angebot gesendet", "confirmed": "Bestaetigt", "completed": "Abgeschlossen", "cancelled": "Storniert"},
        "invoice_labels": {"none": "Keine", "pending": "Offen", "sent": "Gesendet", "paid": "Bezahlt", "overdue": "Ueberfaellig"},
    },
    "en": {
        "thank_you": "Thank you for your inquiry, {name}!",
        "inquiry_received": "We have received your inquiry and will get back to you within 24 hours with a personalized offer.",
        "event_date": "Event Date", "location": "Location", "guests": "Guests", "event_type": "Event Type",
        "trucks": "Trucks", "budget": "Budget", "questions_contact": "For questions, reach us at info@truckonroad.ch or +41 79 696 98 99.",
        "greeting": "Best regards", "team": "TruckOnRoad Team",
        "new_inquiry": "NEW INQUIRY", "new_inquiry_from": "New inquiry from {name}",
        "name": "Name", "email": "Email", "phone": "Phone",
        "your_offer": "Your Offer, {name}", "offer_intro": "Thank you for your interest! Based on your inquiry, we have prepared the following offer:",
        "offer_follow_up": "We will get back to you shortly with detailed terms. Please don't hesitate to contact us with any questions.",
        "status_update": "STATUS UPDATE", "hello": "Hello {name},",
        "status_in_review": "Your inquiry is currently being reviewed by our team. We will contact you shortly.",
        "status_offer_sent": "We have prepared an offer for you. Please review the details and contact us with any questions.",
        "status_confirmed": "Your booking is confirmed! We look forward to your event.",
        "status_completed": "Thank you for your order! We hope the event was a great success.",
        "status_cancelled": "Your inquiry has been cancelled. Please contact us if you have any questions.",
        "status_default": "Your inquiry status has been updated: {status}",
        "event": "Event", "at": "on",
        "invoice_label": "INVOICE", "invoice_word": "Invoice",
        "inv_pending": "An invoice has been created for your event.",
        "inv_sent": "We have sent you an invoice. Please note the payment deadline.",
        "inv_paid": "Thank you! Your payment has been received.",
        "inv_overdue": "Your invoice is overdue. Please check the payment.",
        "inv_default": "Your invoice status has been updated: {status}",
        "new_file": "NEW FILE", "file_added": "A new file has been added to your inquiry:",
        "file_download": "You can download this file in your customer portal.",
        "reminder": "REMINDER", "days_until": "Only {days} days until your event!",
        "ready_for_event": "We are ready and looking forward to your event! For any last questions, reach us at info@truckonroad.ch or +41 79 696 98 99.",
        "subject_inquiry": "Inquiry received", "subject_offer": "Your offer from TruckOnRoad",
        "subject_confirmed": "Your booking is confirmed!", "subject_completed": "Event completed",
        "subject_cancelled": "Inquiry cancelled", "subject_status": "Status Update",
        "subject_inv_pending": "Invoice created", "subject_inv_sent": "Invoice sent",
        "subject_inv_paid": "Payment received", "subject_inv_overdue": "Invoice overdue",
        "subject_reminder": "{days} days until your event!",
        "pdf_offer": "Offer", "pdf_created": "Created on", "pdf_inquiry_nr": "Inquiry No.",
        "pdf_customer": "Customer Details", "pdf_event_details": "Event Details", "pdf_indoor": "Indoor/Outdoor",
        "pdf_remarks": "Remarks", "pdf_disclaimer": "This offer is non-binding and valid for 30 days. Please contact us with any questions.",
        "pdf_company": "Company", "pdf_date": "Date",
        "status_labels": {"new": "New", "in_review": "In Review", "offer_sent": "Offer Sent", "confirmed": "Confirmed", "completed": "Completed", "cancelled": "Cancelled"},
        "invoice_labels": {"none": "None", "pending": "Pending", "sent": "Sent", "paid": "Paid", "overdue": "Overdue"},
    },
    "fr": {
        "thank_you": "Merci pour votre demande, {name} !",
        "inquiry_received": "Nous avons recu votre demande et vous recontacterons dans les 24 heures avec une offre personnalisee.",
        "event_date": "Date", "location": "Lieu", "guests": "Invites", "event_type": "Type",
        "trucks": "Trucks", "budget": "Budget", "questions_contact": "Pour toute question, contactez-nous a info@truckonroad.ch ou +41 79 696 98 99.",
        "greeting": "Cordialement", "team": "L'equipe TruckOnRoad",
        "new_inquiry": "NOUVELLE DEMANDE", "new_inquiry_from": "Nouvelle demande de {name}",
        "name": "Nom", "email": "E-mail", "phone": "Telephone",
        "your_offer": "Votre offre, {name}", "offer_intro": "Merci pour votre interet ! Voici notre offre basee sur votre demande :",
        "offer_follow_up": "Nous reviendrons vers vous avec les conditions detaillees. N'hesitez pas a nous contacter.",
        "status_update": "MISE A JOUR", "hello": "Bonjour {name},",
        "status_in_review": "Votre demande est en cours d'examen. Nous vous contacterons prochainement.",
        "status_offer_sent": "Nous avons prepare une offre pour vous. Veuillez verifier les details.",
        "status_confirmed": "Votre reservation est confirmee ! Nous nous rejouissons de votre evenement.",
        "status_completed": "Merci pour votre commande ! Nous esperons que l'evenement a ete un succes.",
        "status_cancelled": "Votre demande a ete annulee. N'hesitez pas a nous contacter.",
        "status_default": "Le statut de votre demande a ete mis a jour : {status}",
        "event": "Evenement", "at": "le",
        "invoice_label": "FACTURE", "invoice_word": "Facture",
        "inv_pending": "Une facture a ete creee pour votre evenement.",
        "inv_sent": "Nous vous avons envoye une facture. Veuillez respecter le delai de paiement.",
        "inv_paid": "Merci ! Votre paiement a ete recu.",
        "inv_overdue": "Votre facture est en retard. Veuillez verifier le paiement.",
        "inv_default": "Le statut de votre facture a ete mis a jour : {status}",
        "new_file": "NOUVEAU FICHIER", "file_added": "Un nouveau fichier a ete ajoute a votre demande :",
        "file_download": "Vous pouvez telecharger ce fichier dans votre portail client.",
        "reminder": "RAPPEL", "days_until": "Plus que {days} jours avant votre evenement !",
        "ready_for_event": "Nous sommes prets ! Pour toute question, contactez-nous a info@truckonroad.ch ou +41 79 696 98 99.",
        "subject_inquiry": "Demande recue", "subject_offer": "Votre offre de TruckOnRoad",
        "subject_confirmed": "Reservation confirmee !", "subject_completed": "Evenement termine",
        "subject_cancelled": "Demande annulee", "subject_status": "Mise a jour du statut",
        "subject_inv_pending": "Facture creee", "subject_inv_sent": "Facture envoyee",
        "subject_inv_paid": "Paiement recu", "subject_inv_overdue": "Facture en retard",
        "subject_reminder": "Plus que {days} jours !",
        "pdf_offer": "Offre", "pdf_created": "Cree le", "pdf_inquiry_nr": "No. demande",
        "pdf_customer": "Donnees client", "pdf_event_details": "Details evenement", "pdf_indoor": "Interieur/Exterieur",
        "pdf_remarks": "Remarques", "pdf_disclaimer": "Cette offre est sans engagement et valable 30 jours.",
        "pdf_company": "Entreprise", "pdf_date": "Date",
        "status_labels": {"new": "Nouveau", "in_review": "En examen", "offer_sent": "Offre envoyee", "confirmed": "Confirme", "completed": "Termine", "cancelled": "Annule"},
        "invoice_labels": {"none": "Aucune", "pending": "Ouverte", "sent": "Envoyee", "paid": "Payee", "overdue": "En retard"},
    },
    "it": {
        "thank_you": "Grazie per la sua richiesta, {name}!",
        "inquiry_received": "Abbiamo ricevuto la sua richiesta e le risponderemo entro 24 ore con un'offerta personalizzata.",
        "event_date": "Data", "location": "Luogo", "guests": "Ospiti", "event_type": "Tipo",
        "trucks": "Trucks", "budget": "Budget", "questions_contact": "Per domande contattateci a info@truckonroad.ch o +41 79 696 98 99.",
        "greeting": "Cordiali saluti", "team": "Il team TruckOnRoad",
        "new_inquiry": "NUOVA RICHIESTA", "new_inquiry_from": "Nuova richiesta da {name}",
        "name": "Nome", "email": "E-mail", "phone": "Telefono",
        "your_offer": "La sua offerta, {name}", "offer_intro": "Grazie per il suo interesse! Ecco la nostra offerta basata sulla sua richiesta:",
        "offer_follow_up": "La contatteremo a breve con le condizioni dettagliate. Non esiti a contattarci.",
        "status_update": "AGGIORNAMENTO", "hello": "Salve {name},",
        "status_in_review": "La sua richiesta e in fase di revisione. La contatteremo a breve.",
        "status_offer_sent": "Abbiamo preparato un'offerta per lei. Verifichi i dettagli.",
        "status_confirmed": "La sua prenotazione e confermata! Non vediamo l'ora del suo evento.",
        "status_completed": "Grazie per il suo ordine! Speriamo che l'evento sia stato un successo.",
        "status_cancelled": "La sua richiesta e stata annullata. Non esiti a contattarci.",
        "status_default": "Lo stato della sua richiesta e stato aggiornato: {status}",
        "event": "Evento", "at": "il",
        "invoice_label": "FATTURA", "invoice_word": "Fattura",
        "inv_pending": "E stata creata una fattura per il suo evento.",
        "inv_sent": "Le abbiamo inviato una fattura. Rispetti il termine di pagamento.",
        "inv_paid": "Grazie! Il suo pagamento e stato ricevuto.",
        "inv_overdue": "La sua fattura e scaduta. Verifichi il pagamento.",
        "inv_default": "Lo stato della sua fattura e stato aggiornato: {status}",
        "new_file": "NUOVO FILE", "file_added": "Un nuovo file e stato aggiunto alla sua richiesta:",
        "file_download": "Puo scaricare questo file nel suo portale cliente.",
        "reminder": "PROMEMORIA", "days_until": "Mancano solo {days} giorni al suo evento!",
        "ready_for_event": "Siamo pronti! Per domande contattateci a info@truckonroad.ch o +41 79 696 98 99.",
        "subject_inquiry": "Richiesta ricevuta", "subject_offer": "La sua offerta da TruckOnRoad",
        "subject_confirmed": "Prenotazione confermata!", "subject_completed": "Evento completato",
        "subject_cancelled": "Richiesta annullata", "subject_status": "Aggiornamento stato",
        "subject_inv_pending": "Fattura creata", "subject_inv_sent": "Fattura inviata",
        "subject_inv_paid": "Pagamento ricevuto", "subject_inv_overdue": "Fattura scaduta",
        "subject_reminder": "Mancano {days} giorni!",
        "pdf_offer": "Offerta", "pdf_created": "Creata il", "pdf_inquiry_nr": "Nr. richiesta",
        "pdf_customer": "Dati cliente", "pdf_event_details": "Dettagli evento", "pdf_indoor": "Interno/Esterno",
        "pdf_remarks": "Osservazioni", "pdf_disclaimer": "Questa offerta e senza impegno e valida 30 giorni.",
        "pdf_company": "Azienda", "pdf_date": "Data",
        "status_labels": {"new": "Nuovo", "in_review": "In esame", "offer_sent": "Offerta inviata", "confirmed": "Confermato", "completed": "Completato", "cancelled": "Annullato"},
        "invoice_labels": {"none": "Nessuna", "pending": "Aperta", "sent": "Inviata", "paid": "Pagata", "overdue": "Scaduta"},
    },
}

def get_email_t(lang: str = "de"):
    return EMAIL_I18N.get(lang, EMAIL_I18N["de"])

def build_status_notification_email(inquiry: dict, new_status: str, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    status_label = t["status_labels"].get(new_status, new_status)
    status_color = {"confirmed": "#22c55e", "completed": "#6b7280", "cancelled": "#ef4444", "offer_sent": "#8b5cf6"}.get(new_status, "#4db6ac")
    msg_key = f"status_{new_status}"
    msg = t.get(msg_key, t["status_default"].format(status=status_label))
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['status_update']}</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 0.5rem;">{t['hello'].format(name=name)}</h2>
        <div style="display:inline-block;background:{status_color};color:#fff;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;margin:0.5rem 0 1rem;">
          {status_label}
        </div>
        <p style="color:#6b6b64;line-height:1.7;margin-top:0.5rem;">{msg}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['event']}:</strong> {inquiry.get('event_type', '-')} {t['at']} {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['guests']}:</strong> {inquiry.get('guest_count', '-')}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">{t['questions_contact']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

def build_invoice_notification_email(inquiry: dict, invoice_status: str, invoice_amount: float = 0, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    inv_label = t["invoice_labels"].get(invoice_status, invoice_status)
    inv_color = {"pending": "#e8b931", "sent": "#8b5cf6", "paid": "#22c55e", "overdue": "#ef4444"}.get(invoice_status, "#6b7280")
    msg_key = f"inv_{invoice_status}"
    msg = t.get(msg_key, t["inv_default"].format(status=inv_label))
    amount_line = f'<p style="font-size:1.3rem;font-weight:700;color:#1a1a18;margin:0.5rem 0;">CHF {invoice_amount:,.2f}</p>' if invoice_amount > 0 else ""
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['invoice_label']}</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 0.5rem;">{t['hello'].format(name=name)}</h2>
        <div style="display:inline-block;background:{inv_color};color:#fff;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;margin:0.5rem 0 1rem;">
          {t['invoice_word']}: {inv_label}
        </div>
        <p style="color:#6b6b64;line-height:1.7;margin-top:0.5rem;">{msg}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;text-align:center;">
          {amount_line}
          <p style="margin:0.3rem 0;font-size:0.88rem;color:#6b6b64;"><strong>{t['event']}:</strong> {inquiry.get('event_type', '-')} {t['at']} {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;color:#6b6b64;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">{t['questions_contact']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


def build_file_upload_notification_email(inquiry: dict, filename: str, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['new_file']}</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{t['hello'].format(name=name)}</h2>
        <p style="color:#6b6b64;line-height:1.7;">{t['file_added']}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1rem 0;display:flex;align-items:center;gap:0.5rem;">
          <span style="font-weight:600;color:#1a1a18;">{filename}</span>
        </div>
        <p style="color:#6b6b64;font-size:0.88rem;">{t['file_download']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

def build_event_reminder_email(inquiry: dict, days_until: int, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['reminder']}</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{t['hello'].format(name=name)}</h2>
        <p style="color:#6b6b64;line-height:1.7;"><strong>{t['days_until'].format(days=days_until)}</strong></p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['event']}:</strong> {inquiry.get('event_type', '-')} {t['at']} {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['guests']}:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['trucks']}:</strong> {', '.join(inquiry.get('selected_trucks', []))}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.88rem;">{t['ready_for_event']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TruckOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""

def generate_offer_pdf(inquiry: dict, lang: str = "de") -> bytes:
    t = get_email_t(lang)
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
    pdf.cell(0, 10, t["pdf_offer"], ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"{t['pdf_created']}: {datetime.now(timezone.utc).strftime('%d.%m.%Y')}", ln=True)
    pdf.cell(0, 7, f"{t['pdf_inquiry_nr']}: {inquiry.get('id', '-')[:8]}", ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(77, 182, 172)
    pdf.cell(0, 8, t["pdf_customer"], ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    fields = [
        (t["name"], name), (t["email"], inquiry.get("email", "-")), (t["phone"], inquiry.get("phone", "-")),
        (t["pdf_company"], inquiry.get("company", "-")),
    ]
    for label, val in fields:
        if val and val != "-":
            pdf.cell(50, 7, label + ":", 0)
            pdf.cell(0, 7, str(val), ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(77, 182, 172)
    pdf.cell(0, 8, t["pdf_event_details"], ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    event_fields = [
        (t["pdf_date"], inquiry.get("event_date", "-")), (t["location"], inquiry.get("location", "-")),
        (t["guests"], str(inquiry.get("guest_count", "-"))), (t["event_type"], inquiry.get("event_type", inquiry.get("concept", "-"))),
        (t["pdf_indoor"], inquiry.get("indoor_outdoor", "-")), (t["budget"], inquiry.get("budget", "-")),
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
        pdf.cell(0, 7, t["pdf_remarks"] + ":", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, inquiry["remarks"])
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, t["pdf_disclaimer"])
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
    return {"email": user["email"], "name": user.get("name", ""), "first_name": user.get("first_name", ""), "last_name": user.get("last_name", ""), "company": user.get("company", ""), "phone": user.get("phone", ""), "role": user.get("role", "customer"), "lang": user.get("lang", "de")}

@api_router.put("/customer/profile")
async def customer_update_profile(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    update_fields = {}
    if "lang" in body and body["lang"] in ("de", "en", "fr", "it"):
        update_fields["lang"] = body["lang"]
        await db.inquiries.update_many({"customer_id": user["_id"]}, {"$set": {"lang": body["lang"]}})
    if "first_name" in body:
        update_fields["first_name"] = body["first_name"]
    if "last_name" in body:
        update_fields["last_name"] = body["last_name"]
    if "phone" in body:
        update_fields["phone"] = body["phone"]
    if "company" in body:
        update_fields["company"] = body["company"]
    if update_fields:
        await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_fields})
    return {"message": "Updated"}

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
    lang = doc.get("lang", "de")
    t = get_email_t(lang)
    if doc.get("email"):
        background_tasks.add_task(send_email_background, doc["email"], f"{t['subject_inquiry']} – TruckOnRoad", build_confirmation_email(doc, lang))
    # Send notification to admin (always in DE)
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
                il = inquiry.get("lang", "de")
                it = get_email_t(il)
                html = build_file_upload_notification_email(inquiry, file.filename, il)
                background_tasks.add_task(send_email_background, inquiry["email"], f"{it['new_file']} – TruckOnRoad", html)
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
            il = inquiry.get("lang", "de")
            it = get_email_t(il)
            offer_html = build_offer_email(inquiry, il)
            background_tasks.add_task(send_email_background, inquiry["email"], f"{it['subject_offer']} – TruckOnRoad", offer_html)
    # Send status notification email for other status changes
    elif update.status in ("in_review", "confirmed", "completed", "cancelled"):
        inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
        if inquiry and inquiry.get("email"):
            il = inquiry.get("lang", "de")
            it = get_email_t(il)
            status_html = build_status_notification_email(inquiry, update.status, il)
            subject_key = f"subject_{update.status}" if update.status != "in_review" else "subject_status"
            subject = f"{it.get(subject_key, it['subject_status'])} – TruckOnRoad"
            background_tasks.add_task(send_email_background, inquiry["email"], subject, status_html)
    return {"message": "Updated"}

@api_router.put("/admin/inquiries/{inquiry_id}/lang")
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
            il = inquiry.get("lang", "de")
            it = get_email_t(il)
            inv_html = build_invoice_notification_email(inquiry, body["invoice_status"], body.get("invoice_amount", inquiry.get("invoice_amount", 0)), il)
            subject_key = f"subject_inv_{body['invoice_status']}"
            subject = f"{it.get(subject_key, it['invoice_word'])} – TruckOnRoad"
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
        "smtp_email": "", "smtp_password": "",
        "perplexity_api_key": ""
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
    pdf_bytes = generate_offer_pdf(inquiry, inquiry.get("lang", "de"))
    il = inquiry.get("lang", "de")
    it = get_email_t(il)
    name = f"{inquiry.get('first_name', '')}_{inquiry.get('last_name', '')}".strip("_") or "Anfrage"
    return FastAPIResponse(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={it['pdf_offer']}_{name}.pdf"})

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
                il = inq.get("lang", "de")
                it = get_email_t(il)
                html = build_event_reminder_email(inq, reminder_days, il)
                try:
                    send_email_sync(inq["email"], f"{it['subject_reminder'].format(days=reminder_days)} – TruckOnRoad", html, settings)
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


# --- PUBLIC AGENDA ---
@api_router.get("/agenda")
async def get_public_agenda():
    """Public endpoint: upcoming confirmed events."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    inquiries = await db.inquiries.find(
        {"status": {"$in": ["confirmed", "completed"]}, "event_date": {"$gte": today}},
        {"_id": 0, "id": 1, "event_date": 1, "location": 1, "event_type": 1, "event_name": 1, "selected_trucks": 1}
    ).sort("event_date", 1).to_list(100)
    return inquiries


# --- EVENT SCOUT (Perplexity AI) ---
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

async def get_perplexity_key():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return (s or {}).get("perplexity_api_key", "")

@api_router.post("/admin/event-scout/search")
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

    # Get fixed sources for extra context
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
            # Parse JSON from content
            try:
                # Extract JSON array from response (may have markdown code blocks)
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


@api_router.get("/admin/event-scout/events")
async def get_scouted_events(request: Request):
    await get_current_user(request)
    events = await db.scouted_events.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return events

@api_router.post("/admin/event-scout/events")
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

@api_router.put("/admin/event-scout/events/{event_id}")
async def update_scouted_event(event_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("id", None)
    await db.scouted_events.update_one({"id": event_id}, {"$set": body})
    return {"message": "Updated"}

@api_router.delete("/admin/event-scout/events/{event_id}")
async def delete_scouted_event(event_id: str, request: Request):
    await get_current_user(request)
    await db.scouted_events.delete_one({"id": event_id})
    return {"message": "Deleted"}

@api_router.post("/admin/event-scout/events/{event_id}/apply")
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
    company = settings.get("company_name", "TruckOnRoad")
    phone = settings.get("company_phone", "")
    email = settings.get("company_email", "")
    address = settings.get("company_address", "")

    html = f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">Bewerbung: {event.get('name', 'Event')}</h2>
        <p style="color:#6b6b64;line-height:1.6;">{custom_message if custom_message else f"Guten Tag, wir von {company} sind ein Premium-Foodtruck-Unternehmen und moechten uns fuer Ihr Event '{event.get('name', '')}' bewerben."}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;">
          <h3 style="color:#1a1a18;margin:0 0 0.75rem;">Unser Angebot</h3>
          <p style="color:#6b6b64;line-height:1.6;">Wir bieten massgeschneiderte Foodtruck-Erlebnisse fuer Events jeder Groesse. Unsere Trucks sind spezialisiert auf verschiedene Kuechen und Konzepte – von Gourmet-Burgern ueber Asian Fusion bis hin zu Dessert-Trucks.</p>
          <ul style="color:#6b6b64;line-height:1.8;">
            <li>Professionelle Ausstattung &amp; Hygiene</li>
            <li>Flexible Menuezusammenstellung</li>
            <li>Erfahrung mit Grossevents (500+ Gaeste)</li>
            <li>Kompletter Service inkl. Auf-/Abbau</li>
          </ul>
        </div>
        <p style="color:#6b6b64;line-height:1.6;">Wir wuerden uns ueber ein Gespraech freuen. Kontaktieren Sie uns gerne!</p>
        <div style="margin-top:1.5rem;padding-top:1rem;border-top:1px solid #e8e7e3;">
          <p style="color:#1a1a18;font-weight:600;margin:0;">{company}</p>
          <p style="color:#6b6b64;margin:0.25rem 0;">{address}</p>
          <p style="color:#6b6b64;margin:0.25rem 0;">Tel: {phone} | E-Mail: {email}</p>
        </div>
      </div>
    </div>"""

    background_tasks.add_task(send_email_background, to_email, f"Bewerbung Foodtruck - {event.get('name', 'Event')} | {company}", html)
    await db.scouted_events.update_one({"id": event_id}, {"$set": {"status": "contacted", "organizer_email": to_email}})
    return {"message": "Bewerbung wird gesendet"}


# --- EVENT SCOUT: Fixed Sources ---
@api_router.get("/admin/event-scout/sources")
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

@api_router.put("/admin/event-scout/sources")
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

@api_router.post("/admin/event-scout/scan-now")
async def trigger_manual_scan(request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    background_tasks.add_task(run_event_scan)
    return {"message": "Scan gestartet"}


# --- EVENT SCOUT: Auto Scan Logic ---

async def call_perplexity_search(api_key: str, query: str, extra_context: str = "") -> list:
    """Call Perplexity API and return parsed events list."""
    system_prompt = f"""Du bist ein Experte fuer Event-Recherche in der SCHWEIZ.
Suche nach relevanten Events, Festivals, Weihnachtsmaerkten, Strassenfesten, Maerkten und Firmenevents in der Schweiz.
{extra_context}
WICHTIG: Nur Events in der SCHWEIZ. Keine Events aus anderen Laendern.
Antworte IMMER im folgenden JSON-Format (Array von Events):
[
  {{
    "name": "Event-Name",
    "date": "Datum oder Zeitraum (z.B. 15.-18. Dezember 2026)",
    "location": "Stadt/Ort in der Schweiz",
    "type": "festival|weihnachtsmarkt|markt|firmenevent|strassenfest|andere",
    "description": "Kurzbeschreibung (1-2 Saetze)",
    "organizer_email": "E-Mail des Veranstalters falls verfuegbar, sonst leer",
    "website": "URL zur Event-Website falls verfuegbar"
  }}
]
Liefere so viele relevante Schweizer Events wie moeglich (mindestens 5-15). Gib NUR den JSON-Array zurueck."""

    try:
        async with httpx.AsyncClient(timeout=90) as http_client:
            resp = await http_client.post(
                PERPLEXITY_API_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.3
                }
            )
            if resp.status_code != 200:
                logger.error(f"Perplexity API error: {resp.status_code}")
                return []
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "[]")
            clean = content.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[-1]
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()
            return json_mod.loads(clean)
    except Exception as e:
        logger.error(f"Perplexity search error: {e}")
        return []


async def run_event_scan():
    """Run the daily event scan: search via Perplexity, deduplicate, save new, email admin."""
    try:
        settings = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
        api_key = settings.get("perplexity_api_key", "")
        if not api_key:
            logger.info("Event scan skipped: no Perplexity API key")
            return

        sources = settings.get("scout_sources", [])
        keywords = settings.get("scout_keywords", ["Festival", "Weihnachtsmarkt", "Strassenfest", "Food Festival", "Markt"])

        # Build source context for the AI
        source_context = ""
        if sources:
            source_context = "Durchsuche auch diese bekannten Event-Webseiten: " + ", ".join(sources)

        # Get existing event names for deduplication
        existing = await db.scouted_events.find({}, {"_id": 0, "name": 1}).to_list(1000)
        existing_names = set(e.get("name", "").lower().strip() for e in existing)

        all_new_events = []

        # Search for each keyword
        for keyword in keywords:
            query = f"Finde aktuelle und kommende Events: {keyword} in der Schweiz 2025/2026/2027"
            events = await call_perplexity_search(api_key, query, source_context)
            for ev in events:
                name = (ev.get("name") or "").strip()
                if not name:
                    continue
                # Deduplicate
                if name.lower() in existing_names:
                    continue
                existing_names.add(name.lower())
                doc = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "date": ev.get("date", ""),
                    "location": ev.get("location", ""),
                    "type": ev.get("type", "andere"),
                    "description": ev.get("description", ""),
                    "organizer_email": ev.get("organizer_email", ""),
                    "website": ev.get("website", ""),
                    "status": "new",
                    "notes": "",
                    "source": "auto_scan",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                try:
                    await db.scouted_events.insert_one(doc)
                    all_new_events.append(doc)
                except Exception:
                    pass  # Duplicate key or other error

        # Update last scan info
        await db.settings.update_one({"type": "general"}, {"$set": {
            "scout_last_scan": datetime.now(timezone.utc).isoformat(),
            "scout_last_scan_count": len(all_new_events)
        }}, upsert=True)

        # Send admin email notification if there are new events
        if all_new_events:
            notification_email = settings.get("notification_email", "")
            if notification_email and settings.get("email_notifications"):
                event_rows = ""
                for ev in all_new_events[:20]:
                    event_rows += f"""<tr>
                        <td style="padding:8px 12px;border-bottom:1px solid #e8e7e3;font-size:0.85rem;">{ev['name']}</td>
                        <td style="padding:8px 12px;border-bottom:1px solid #e8e7e3;font-size:0.85rem;">{ev['date']}</td>
                        <td style="padding:8px 12px;border-bottom:1px solid #e8e7e3;font-size:0.85rem;">{ev['location']}</td>
                        <td style="padding:8px 12px;border-bottom:1px solid #e8e7e3;font-size:0.85rem;">{ev['type']}</td>
                    </tr>"""

                html = f"""
                <div style="font-family:'DM Sans',Arial,sans-serif;max-width:650px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
                  <div style="background:#1a1a18;padding:2rem;text-align:center;">
                    <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
                      <span style="color:#f5f0e8;">TRUCK</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
                    </span>
                  </div>
                  <div style="padding:2rem;">
                    <h2 style="color:#1a1a18;margin:0 0 0.5rem;">Event-Scout: {len(all_new_events)} neue Events gefunden</h2>
                    <p style="color:#6b6b64;margin:0 0 1.5rem;">Der automatische Event-Scanner hat neue Schweizer Events gefunden:</p>
                    <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #e8e7e3;border-radius:8px;overflow:hidden;">
                      <thead>
                        <tr style="background:#f5f5f2;">
                          <th style="padding:10px 12px;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b6b64;">Event</th>
                          <th style="padding:10px 12px;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b6b64;">Datum</th>
                          <th style="padding:10px 12px;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b6b64;">Ort</th>
                          <th style="padding:10px 12px;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b6b64;">Typ</th>
                        </tr>
                      </thead>
                      <tbody>{event_rows}</tbody>
                    </table>
                    {f'<p style="color:#6b6b64;margin-top:1rem;font-size:0.82rem;">... und {len(all_new_events) - 20} weitere Events</p>' if len(all_new_events) > 20 else ''}
                    <p style="color:#6b6b64;margin-top:1.5rem;">Melden Sie sich im <a href="#" style="color:#4db6ac;font-weight:600;">Admin-Dashboard</a> an, um die Events zu verwalten und Bewerbungen zu versenden.</p>
                  </div>
                </div>"""
                await send_email_background(notification_email, f"Event-Scout: {len(all_new_events)} neue Schweizer Events gefunden", html)

        logger.info(f"Event scan complete: {len(all_new_events)} new events found")

    except Exception as e:
        logger.error(f"Event scan failed: {e}")


async def event_scan_loop():
    """Background loop that runs the event scan every 24 hours."""
    while True:
        await asyncio.sleep(24 * 3600)
        settings = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
        if settings.get("scout_auto_scan"):
            await run_event_scan()


app.include_router(api_router)

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.trucks.create_index("slug", unique=True)
    await db.inquiries.create_index("id")
    await db.calendar_blocks.create_index([("truck_slug", 1), ("date", 1)])
    await db.login_attempts.create_index("identifier")
    await db.scouted_events.create_index("id", unique=True)

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
    asyncio.create_task(event_scan_loop())

@app.on_event("shutdown")
async def shutdown():
    client.close()
