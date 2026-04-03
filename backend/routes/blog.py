from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from datetime import datetime, timezone
from database import db
from auth import get_current_user
from services.blog_generator import generate_blog_post
import uuid

router = APIRouter()

CATEGORIES = {
    "guide": {"de": "Ratgeber", "en": "Guide", "fr": "Guide", "it": "Guida"},
    "locations": {"de": "Standorte", "en": "Locations", "fr": "Emplacements", "it": "Posizioni"},
    "tipps": {"de": "Tipps", "en": "Tips", "fr": "Conseils", "it": "Consigli"},
    "events": {"de": "Events", "en": "Events", "fr": "Evenements", "it": "Eventi"},
    "regionen": {"de": "Regionen", "en": "Regions", "fr": "Regions", "it": "Regioni"},
    "rezepte": {"de": "Rezepte", "en": "Recipes", "fr": "Recettes", "it": "Ricette"},
    "news": {"de": "News", "en": "News", "fr": "Actualites", "it": "Notizie"},
}


# --- PUBLIC BLOG ---
@router.get("/blog")
async def get_blog_posts(category: str = None, limit: int = 20):
    query = {"is_published": True}
    if category:
        query["category"] = category
    posts = await db.blog_posts.find(query, {"_id": 0, "content_de": 0, "content_en": 0, "content_fr": 0, "content_it": 0}).sort("created_at", -1).to_list(limit)
    return {"posts": posts, "categories": CATEGORIES}


@router.get("/blog/{slug}")
async def get_blog_post(slug: str):
    post = await db.blog_posts.find_one({"slug": slug, "is_published": True}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/blog-categories")
async def get_blog_categories():
    return CATEGORIES


# --- SEO: BLOG ARTICLE SCHEMA ---
@router.get("/seo/blog-schema/{slug}")
async def get_blog_schema(slug: str):
    post = await db.blog_posts.find_one({"slug": slug, "is_published": True}, {"_id": 0})
    if not post:
        return {}
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post.get("title_de", ""),
        "description": post.get("excerpt_de", ""),
        "image": post.get("image", ""),
        "author": {"@type": "Organization", "name": "TrucksOnRoad", "url": "https://trucksonroad.ch"},
        "publisher": {"@type": "Organization", "name": "TrucksOnRoad", "url": "https://trucksonroad.ch"},
        "datePublished": post.get("created_at", ""),
        "dateModified": post.get("updated_at", ""),
        "mainEntityOfPage": f"https://trucksonroad.ch/blog/{slug}",
        "inLanguage": ["de", "en", "fr", "it"],
        "keywords": ", ".join(post.get("tags", []))
    }


# --- ADMIN BLOG ---
@router.get("/admin/blog")
async def admin_get_blog(request: Request):
    await get_current_user(request)
    posts = await db.blog_posts.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return posts


@router.post("/admin/blog")
async def admin_create_blog(request: Request):
    await get_current_user(request)
    body = await request.json()
    post = {
        "id": str(uuid.uuid4()),
        "slug": body.get("slug", ""),
        "title_de": body.get("title_de", ""), "title_en": body.get("title_en", ""),
        "title_fr": body.get("title_fr", ""), "title_it": body.get("title_it", ""),
        "excerpt_de": body.get("excerpt_de", ""), "excerpt_en": body.get("excerpt_en", ""),
        "excerpt_fr": body.get("excerpt_fr", ""), "excerpt_it": body.get("excerpt_it", ""),
        "content_de": body.get("content_de", ""), "content_en": body.get("content_en", ""),
        "content_fr": body.get("content_fr", ""), "content_it": body.get("content_it", ""),
        "category": body.get("category", "news"),
        "image": body.get("image", ""),
        "tags": body.get("tags", []),
        "author": body.get("author", "TrucksOnRoad Team"),
        "is_published": body.get("is_published", False),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.blog_posts.insert_one(post)
    post.pop("_id", None)
    return post


@router.put("/admin/blog/{post_id}")
async def admin_update_blog(post_id: str, request: Request):
    await get_current_user(request)
    body = await request.json()
    body.pop("_id", None)
    body.pop("id", None)
    body["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.blog_posts.update_one({"id": post_id}, {"$set": body})
    return {"message": "Updated"}


@router.delete("/admin/blog/{post_id}")
async def admin_delete_blog(post_id: str, request: Request):
    await get_current_user(request)
    await db.blog_posts.delete_one({"id": post_id})
    return {"message": "Deleted"}


# --- AI BLOG GENERATION ---
@router.post("/admin/blog/generate")
async def admin_generate_blog(request: Request, background_tasks: BackgroundTasks):
    await get_current_user(request)
    post = await generate_blog_post()
    if not post:
        raise HTTPException(status_code=500, detail="KI-Generierung fehlgeschlagen. Bitte erneut versuchen.")
    return post


@router.get("/admin/blog/auto-status")
async def admin_blog_auto_status(request: Request):
    await get_current_user(request)
    settings = await db.settings.find_one({}, {"_id": 0, "blog_auto_enabled": 1, "blog_auto_interval_hours": 1})
    return {
        "enabled": (settings or {}).get("blog_auto_enabled", False),
        "interval_hours": (settings or {}).get("blog_auto_interval_hours", 24)
    }


@router.post("/admin/blog/auto-toggle")
async def admin_blog_auto_toggle(request: Request):
    await get_current_user(request)
    body = await request.json()
    enabled = body.get("enabled", False)
    interval = body.get("interval_hours", 24)
    await db.settings.update_one({}, {"$set": {"blog_auto_enabled": enabled, "blog_auto_interval_hours": interval}}, upsert=True)
    return {"enabled": enabled, "interval_hours": interval}

