from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
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
async def create_inquiry(inquiry: InquiryCreate):
    doc = inquiry.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["status"] = "new"
    doc["internal_notes"] = ""
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.inquiries.insert_one(doc)
    return {"message": "Anfrage erfolgreich gesendet", "id": doc["id"]}

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
async def admin_update_inquiry(inquiry_id: str, update: InquiryStatusUpdate, request: Request):
    await get_current_user(request)
    result = await db.inquiries.update_one(
        {"id": inquiry_id},
        {"$set": {"status": update.status, "internal_notes": update.internal_notes, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}

@api_router.delete("/admin/inquiries/{inquiry_id}")
async def admin_delete_inquiry(inquiry_id: str, request: Request):
    await get_current_user(request)
    result = await db.inquiries.delete_one({"id": inquiry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}

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
    return s or {"type": "general", "company_name": "StrongFood", "email_notifications": False, "notification_email": "", "whatsapp_number": "+41791234567"}

@api_router.put("/admin/settings")
async def admin_update_settings(request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    await db.settings.update_one({"type": "general"}, {"$set": body}, upsert=True)
    return {"message": "Updated"}

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
        "image": "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/apahq84l_Bildschirmfoto%202026-03-23%20um%2017.15.39.png",
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
        "image": "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/apahq84l_Bildschirmfoto%202026-03-23%20um%2017.15.39.png",
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
        "image": "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/6dfmnt16_Bildschirmfoto%202026-03-23%20um%2017.15.33.png",
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
        "image": "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/9fk5box5_Bildschirmfoto%202026-03-25%20um%2023.23.44.png",
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
        "image": "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/3kne14pi_Bildschirmfoto%202026-03-23%20um%2017.09.13.png",
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
        "image": "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/d3mmcf6i_Bildschirmfoto%202026-03-25%20um%2023.21.42.png",
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

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.trucks.create_index("slug", unique=True)
    await db.inquiries.create_index("id")
    await db.calendar_blocks.create_index([("truck_slug", 1), ("date", 1)])
    await db.login_attempts.create_index("identifier")

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@strongfood.ch")
    admin_password = os.environ.get("ADMIN_PASSWORD", "StrongFood2026!")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({"email": admin_email, "password_hash": hash_password(admin_password), "name": "Admin", "role": "admin", "created_at": datetime.now(timezone.utc).isoformat()})
        logger.info(f"Admin seeded: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})

    for t in TRUCKS_SEED:
        if not await db.trucks.find_one({"slug": t["slug"]}):
            await db.trucks.insert_one(t.copy())
            logger.info(f"Truck seeded: {t['slug']}")

    if await db.faqs.count_documents({}) == 0:
        for f in FAQS_SEED:
            await db.faqs.insert_one(f.copy())
        logger.info("FAQs seeded")

    Path("/app/memory").mkdir(exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"# Test Credentials\n\n## Admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: admin\n\n## Auth Endpoints\n- POST /api/auth/login\n- POST /api/auth/logout\n- GET /api/auth/me\n- POST /api/auth/refresh\n")
    logger.info("Startup complete")

@app.on_event("shutdown")
async def shutdown():
    client.close()
