from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import asyncio
import uuid
from datetime import datetime, timezone

from database import db, client
from auth import hash_password, verify_password
from seed import TRUCKS_SEED, FAQS_SEED
from blog_seed import BLOG_SEED
from services.storage import init_storage
from services.event_scout import event_reminder_loop, event_scan_loop
from services.blog_generator import generate_blog_post
from routes.auth_routes import router as auth_router
from routes.public import router as public_router
from routes.customer import router as customer_router
from routes.admin import router as admin_router
from routes.blog import router as blog_router
from routes.legal import router as legal_router
from legal_seed import LEGAL_SEED

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(public_router)
api_router.include_router(customer_router)
api_router.include_router(admin_router)
api_router.include_router(blog_router)
api_router.include_router(legal_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
        "https://trucksonroad.ch",
        "https://www.trucksonroad.ch",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    admin_password = os.environ.get("ADMIN_PASSWORD", "TrucksOnRoad2026!")
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

    if await db.blog_posts.count_documents({}) == 0:
        for bp in BLOG_SEED:
            await db.blog_posts.insert_one(bp.copy())
        logger.info(f"Blog posts seeded: {len(BLOG_SEED)}")
    await db.blog_posts.create_index("slug", unique=True)

    # Seed legal documents (AGB, Datenschutz, Impressum) as version 1 if not present
    await db.legal_documents.create_index("type", unique=True)
    await db.legal_versions.create_index([("doc_type", 1), ("version", -1)])
    for doc_type, seed_doc in LEGAL_SEED.items():
        if not await db.legal_documents.find_one({"type": doc_type}):
            now = datetime.now(timezone.utc).isoformat()
            initial = {
                **seed_doc,
                "version": 1,
                "updated_at": now,
                "updated_by_email": admin_email,
                "updated_by_name": "System (Initial Seed)",
            }
            await db.legal_documents.insert_one(initial.copy())
            version_entry = {
                "id": str(uuid.uuid4()),
                "doc_type": doc_type,
                "version": 1,
                "title": seed_doc["title"],
                "subtitle": seed_doc.get("subtitle", ""),
                "sections": seed_doc["sections"],
                "change_notes": "Initiale Version (System-Seed)",
                "admin_email": admin_email,
                "admin_name": "System",
                "created_at": now,
                "diff_added": sum(len(s["content"].splitlines()) for s in seed_doc["sections"]),
                "diff_removed": 0,
                "diff_text": "",
            }
            await db.legal_versions.insert_one(version_entry)
            logger.info(f"Legal seeded: {doc_type} v1")

    Path("/app/memory").mkdir(exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"# Test Credentials\n\n## Admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: admin\n\n## Customer (Test)\n- Register at /konto/registrieren\n- Or use API: POST /api/auth/register\n\n## Auth Endpoints\n- POST /api/auth/login\n- POST /api/auth/register\n- POST /api/auth/logout\n- GET /api/auth/me\n- POST /api/auth/refresh\n\n## Customer Portal Endpoints\n- GET /api/customer/inquiries\n- GET /api/customer/inquiries/{{id}}\n- GET /api/customer/profile\n")
    logger.info("Startup complete")

    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.warning(f"Object storage init failed (will retry on first upload): {e}")

    asyncio.create_task(event_reminder_loop())
    asyncio.create_task(event_scan_loop())
    asyncio.create_task(blog_auto_loop())


@app.on_event("shutdown")
async def shutdown():
    client.close()


async def blog_auto_loop():
    while True:
        try:
            settings = await db.settings.find_one({}, {"_id": 0, "blog_auto_enabled": 1, "blog_auto_interval_hours": 1})
            enabled = (settings or {}).get("blog_auto_enabled", False)
            interval_hours = (settings or {}).get("blog_auto_interval_hours", 24)
            if enabled:
                logger.info("Auto-Blog: Generating new post...")
                post = await generate_blog_post()
                if post:
                    logger.info(f"Auto-Blog: Published '{post['slug']}'")
                else:
                    logger.warning("Auto-Blog: Generation failed")
            await asyncio.sleep(interval_hours * 3600)
        except Exception as e:
            logger.error(f"Auto-Blog loop error: {e}")
            await asyncio.sleep(3600)
