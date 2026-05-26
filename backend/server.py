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
from datetime import datetime, timezone, timedelta

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
from routes.backups import router as backups_router
from services import db_backup, cloud_backup
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
api_router.include_router(backups_router)

_cors_origins_env = os.environ.get("CORS_ORIGINS", "*")
_allow_origins = ["*"] if _cors_origins_env.strip() == "*" else [
    o.strip() for o in _cors_origins_env.split(",") if o.strip()
]
# When using wildcard, allow_credentials must be False (CORS spec).
_allow_credentials = _allow_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=_allow_credentials,
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
    asyncio.create_task(_db_backup_loop())


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



async def _db_backup_loop():
    """Runs mongodump daily at 03:00 Europe/Zurich, packs as tar.gz, uploads to Cloud."""
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("Europe/Zurich")
    except Exception:
        tz = timezone.utc
    while True:
        try:
            now = datetime.now(tz)
            target = now.replace(hour=3, minute=0, second=0, microsecond=0)
            if target <= now:
                target = target + timedelta(days=1)
            sleep_seconds = max(60.0, (target - now).total_seconds())
            logger.info(f"DB-Backup: next run at {target.isoformat()} (in {int(sleep_seconds)}s)")
            await asyncio.sleep(sleep_seconds)

            mongo_url = os.environ.get("MONGO_URL")
            db_name = os.environ.get("DB_NAME")
            if not mongo_url:
                logger.warning("DB-Backup: MONGO_URL not set, skipping")
                continue
            try:
                result = db_backup.run_mongodump(mongo_url, db_name)
                logger.info(f"DB-Backup: local archive {result['filename']} ({result['size_mb']} MB)")
            except Exception as exc:
                logger.error(f"DB-Backup: mongodump failed: {exc}")
                continue

            cfg = await db.settings.find_one({"type": "cloud_backup"}, {"_id": 0}) or {}
            environment = (os.environ.get("ENVIRONMENT") or "preview").lower()
            if cfg.get("enabled") and environment == "production":
                try:
                    up = cloud_backup.upload_archive(cfg, result["path"])
                    logger.info(f"DB-Backup: cloud upload OK key={up['key']}")
                    try:
                        deleted = cloud_backup.prune_cloud_backups(cfg, cfg.get("retention_days", 30))
                        if deleted:
                            logger.info(f"DB-Backup: cloud retention pruned {len(deleted)} object(s)")
                    except Exception as prune_exc:
                        logger.warning(f"DB-Backup: cloud prune failed: {prune_exc}")
                except Exception as exc:
                    logger.error(f"DB-Backup: cloud upload failed: {exc}")
            elif cfg.get("enabled"):
                logger.info(f"DB-Backup: cloud upload skipped (environment='{environment}', only 'production' uploads)")
        except Exception as exc:
            logger.error(f"DB-Backup loop fatal: {exc}")
            await asyncio.sleep(3600)
