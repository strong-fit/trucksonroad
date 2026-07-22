from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import Response as FastAPIResponse
from datetime import datetime, timezone
from database import db
from models import QuickInquiryCreate
from services.pdf import generate_veranstalter_pdf
from services.email import (
    get_email_t, build_confirmation_email, build_admin_notification_email,
    build_status_notification_email, build_invoice_notification_email,
    build_file_upload_notification_email, build_event_reminder_email,
    send_email_background, get_email_settings
)
import uuid
import math
import re
import httpx

router = APIRouter()


# --- PUBLIC TRUCKS ---
@router.get("/trucks")
async def get_trucks():
    return await db.trucks.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)


# --- PUBLIC MARKETING / TRACKING CONFIG ---
@router.get("/marketing/config")
async def get_marketing_config():
    """
    Returns non-sensitive tracking IDs that the frontend uses to inject
    analytics scripts. Consent gating is done client-side via the cookie banner.
    """
    s = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
    return {
        "ga4_measurement_id": s.get("ga4_measurement_id", ""),
        "gtm_container_id": s.get("gtm_container_id", ""),
        "meta_pixel_id": s.get("meta_pixel_id", ""),
        "google_ads_conversion_id": s.get("google_ads_conversion_id", ""),
        "google_ads_conversion_label": s.get("google_ads_conversion_label", ""),
        "clarity_project_id": s.get("clarity_project_id", ""),
        "tiktok_pixel_id": s.get("tiktok_pixel_id", ""),
        "linkedin_partner_id": s.get("linkedin_partner_id", ""),
        "bing_uet_tag": s.get("bing_uet_tag", ""),
        "google_verification": s.get("google_verification", ""),
    }


@router.get("/trucks/{slug}")
async def get_truck(slug: str):
    truck = await db.trucks.find_one({"slug": slug}, {"_id": 0})
    if not truck:
        raise HTTPException(status_code=404, detail="Not found")
    return truck


# --- FAQS ---
@router.get("/faqs")
async def get_faqs():
    return await db.faqs.find({}, {"_id": 0}).sort("order", 1).to_list(100)


# --- AVAILABILITY ---
@router.get("/availability")
async def get_availability():
    return await db.calendar_blocks.find({}, {"_id": 0}).to_list(10000)


@router.get("/availability/{date}")
async def check_date(date: str):
    total = await db.trucks.count_documents({"is_active": True})
    blocked = await db.calendar_blocks.count_documents({"date": date, "status": {"$in": ["blocked", "confirmed"]}})
    if blocked == 0:
        return {"date": date, "status": "available", "blocked": 0, "total": total}
    elif blocked >= total:
        return {"date": date, "status": "booked", "blocked": blocked, "total": total}
    return {"date": date, "status": "partial", "blocked": blocked, "total": total}


# --- QUICK INQUIRY ---
@router.post("/quick-inquiry")
async def create_quick_inquiry(inquiry: QuickInquiryCreate, background_tasks: BackgroundTasks):
    doc = inquiry.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["status"] = "new"
    doc["type"] = "quick"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()

    # Split contact into email/phone for the admin notification template
    contact = (doc.get("contact") or "").strip()
    email_match = re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", contact)
    if email_match:
        doc["email"] = contact
        doc["phone"] = ""
    else:
        doc["email"] = ""
        doc["phone"] = contact

    await db.inquiries.insert_one(doc)

    # Notify admin in background (does not block the response)
    settings = await get_email_settings()
    admin_email = settings.get("admin_notification_email") or settings.get("smtp_email") or ""
    if admin_email:
        try:
            notif_doc = {
                "name": doc.get("name", ""),
                "email": doc.get("email", ""),
                "phone": doc.get("phone", ""),
                "event_date": doc.get("event_date", ""),
                "location": doc.get("location", ""),
                "guest_count": doc.get("guest_count", 0),
                "event_type": "Rueckruf-Anfrage (Schnellanfrage)",
                "selected_trucks": [],
                "budget": "-",
            }
            html = build_admin_notification_email(notif_doc, lang="de")
            subject = f"Neue Rueckruf-Anfrage von {doc.get('name', 'Gast')}"
            background_tasks.add_task(send_email_background, admin_email, subject, html)
        except Exception:
            pass  # do not break the public endpoint if email fails

    # Confirmation to customer if they provided a valid email
    if doc.get("email"):
        try:
            conf_html = build_confirmation_email(doc, lang="de")
            background_tasks.add_task(
                send_email_background,
                doc["email"],
                "Wir haben deine Anfrage erhalten | TRUCKSonROAD",
                conf_html,
            )
        except Exception:
            pass

    return {"message": "Schnellanfrage gesendet", "id": doc["id"]}


# --- BOOKING FLOW: TRUCK AVAILABILITY ---
@router.get("/truck-availability/{truck_slug}")
async def get_truck_availability(truck_slug: str, year: int = 2026, month: int = 1):
    blocks = await db.calendar_blocks.find(
        {"truck_slug": truck_slug, "date": {"$regex": f"^{year}-{month:02d}"}},
        {"_id": 0}
    ).to_list(100)
    return blocks


# --- BOOKING FLOW: MENU CATEGORIES ---
@router.get("/menu-categories")
async def get_menu_categories():
    cats = await db.menu_categories.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return cats


# --- BOOKING FLOW: DELIVERY COST CALCULATION ---
BASE_COORDS = {"lat": 47.3230, "lng": 8.7990}  # Wetzikon default

@router.post("/calculate-delivery")
async def calculate_delivery(request: Request):
    body = await request.json()
    plz = body.get("plz", "").strip()
    if not plz:
        raise HTTPException(status_code=400, detail="PLZ erforderlich")
    settings = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
    price_per_km = settings.get("delivery_price_per_km", 2.0)
    base_plz = settings.get("company_plz", "8620")
    # Geocode customer PLZ
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"postalcode": plz, "country": "CH", "format": "json", "limit": 1},
                headers={"User-Agent": "TrucksOnRoad/1.0"}
            )
            data = r.json()
            if not data:
                return {"km": 0, "cost": 0, "error": "PLZ nicht gefunden"}
            cust_lat, cust_lng = float(data[0]["lat"]), float(data[0]["lon"])
        # Geocode base PLZ
        async with httpx.AsyncClient(timeout=5.0) as client:
            r2 = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"postalcode": base_plz, "country": "CH", "format": "json", "limit": 1},
                headers={"User-Agent": "TrucksOnRoad/1.0"}
            )
            data2 = r2.json()
            if data2:
                base_lat, base_lng = float(data2[0]["lat"]), float(data2[0]["lon"])
            else:
                base_lat, base_lng = BASE_COORDS["lat"], BASE_COORDS["lng"]
    except Exception:
        return {"km": 0, "cost": 0, "error": "Berechnung fehlgeschlagen"}
    # Haversine distance
    R = 6371
    dlat = math.radians(cust_lat - base_lat)
    dlng = math.radians(cust_lng - base_lng)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(base_lat)) * math.cos(math.radians(cust_lat)) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    straight_km = R * c
    road_km = round(straight_km * 1.3, 1)  # Road factor
    cost = round(road_km * price_per_km, 2)
    return {"km": road_km, "cost": cost, "price_per_km": price_per_km}


# --- PUBLIC CONTACT INFO ---
@router.get("/contact-info")
async def get_contact_info():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return {
        "company_name": (s or {}).get("company_name", "TrucksOnRoad"),
        "address": (s or {}).get("company_address", "Bahnhofstrasse 75, 8620 Wetzikon"),
        "phone": (s or {}).get("company_phone", "+41 79 696 98 99"),
        "email": (s or {}).get("company_email", "info@trucksonroad.ch"),
        "whatsapp": (s or {}).get("whatsapp_number", "+41796969899"),
    }


# --- REVIEWS ---
@router.get("/reviews")
async def get_public_reviews():
    google_count = await db.reviews.count_documents({"is_active": True, "source": "google"})
    if google_count > 0:
        reviews = await db.reviews.find({"is_active": True, "source": "google"}, {"_id": 0}).sort("date", -1).to_list(50)
    else:
        reviews = await db.reviews.find({"is_active": True}, {"_id": 0}).sort("date", -1).to_list(50)
    return reviews


# --- SEO: STRUCTURED DATA ---
@router.get("/seo/structured-data")
async def get_structured_data():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
    same_as = [v for k in ["social_google_business", "social_instagram", "social_facebook", "social_tiktok", "social_linkedin"] if (v := s.get(k, ""))]
    result = {
        "@context": "https://schema.org",
        "@type": "FoodEstablishment",
        "name": s.get("company_name", "TrucksOnRoad"),
        "alternateName": f"{s.get('company_name', 'TrucksOnRoad')} - Premium Foodtrucks",
        "description": "Premium Foodtrucks für Festivals, Firmenanlässe und Private Events in der ganzen Schweiz. 6 einzigartige Truck-Konzepte: Burger, Chicken Burger, Bowls, Pocket Bowls, Empanadas und Retro Trailer.",
        "url": "https://trucksonroad.ch",
        "telephone": s.get("company_phone", "+41 79 696 98 99"),
        "email": s.get("company_email", "info@trucksonroad.ch"),
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
    reviews = await db.reviews.find({"is_active": True}, {"_id": 0}).to_list(500)
    if reviews:
        ratings = [r.get("rating", 5) for r in reviews]
        result["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(sum(ratings) / len(ratings), 1),
            "reviewCount": len(ratings),
            "bestRating": 5, "worstRating": 1
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


@router.get("/seo/google-verification")
async def google_verification():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
    return {"code": s.get("google_verification", "")}


# --- ROBOTS.TXT ---
@router.get("/robots.txt")
async def robots_txt():
    content = """User-agent: *
Allow: /
Sitemap: https://trucksonroad.ch/api/sitemap.xml

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


# --- SITEMAP ---
@router.get("/sitemap.xml")
async def sitemap():
    base = "https://trucksonroad.ch"
    trucks_list = await db.trucks.find({"is_active": True}, {"slug": 1, "_id": 0}).to_list(100)
    blog_list = await db.blog_posts.find({"is_published": True}, {"slug": 1, "_id": 0}).to_list(200)
    urls = [
        (base + "/", "1.0", "weekly"),
        (base + "/fuer-veranstalter", "0.8", "monthly"),
        (base + "/private-events", "0.8", "monthly"),
        (base + "/ueber-uns", "0.7", "monthly"),
        (base + "/kontakt", "0.7", "monthly"),
        (base + "/anfrage", "0.9", "weekly"),
        (base + "/trucks", "0.8", "weekly"),
        (base + "/faq", "0.6", "monthly"),
        (base + "/blog", "0.8", "weekly"),
    ]
    for t in trucks_list:
        urls.append((f"{base}/trucks/{t['slug']}", "0.7", "monthly"))
    for bp in blog_list:
        urls.append((f"{base}/blog/{bp['slug']}", "0.7", "weekly"))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, pri, freq in urls:
        xml += f"  <url><loc>{loc}</loc><priority>{pri}</priority><changefreq>{freq}</changefreq></url>\n"
    xml += "</urlset>"
    return FastAPIResponse(content=xml, media_type="application/xml")


# --- VERANSTALTER PDF ---
@router.get("/download/veranstalter-pdf")
async def download_veranstalter_pdf():
    pdf_bytes = await generate_veranstalter_pdf()
    return FastAPIResponse(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=TrucksOnRoad_Veranstalter.pdf"})


# --- INSTAGRAM GALLERY ---
@router.get("/instagram-gallery")
async def get_instagram_gallery():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return {
        "username": (s or {}).get("instagram_username", ""),
        "images": (s or {}).get("instagram_images", []),
    }


# --- PUBLIC AGENDA ---
@router.get("/agenda")
async def get_public_agenda():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    inquiries = await db.inquiries.find(
        {"status": {"$in": ["confirmed", "completed"]}, "event_date": {"$gte": today}},
        {"_id": 0, "id": 1, "event_date": 1, "location": 1, "event_type": 1, "event_name": 1, "selected_trucks": 1}
    ).sort("event_date", 1).to_list(100)
    return inquiries


# --- SEO: EVENT JSON-LD SCHEMA ---
@router.get("/seo/events-schema")
async def get_events_schema():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    events = await db.inquiries.find(
        {"status": {"$in": ["confirmed", "completed"]}, "event_date": {"$gte": today}},
        {"_id": 0, "event_date": 1, "location": 1, "event_type": 1, "event_name": 1}
    ).sort("event_date", 1).to_list(50)
    if not events:
        return []
    schema_events = []
    for e in events:
        schema_events.append({
            "@context": "https://schema.org",
            "@type": "FoodEvent",
            "name": e.get("event_name") or f"TrucksOnRoad @ {e.get('event_type', 'Event')}",
            "startDate": e.get("event_date", ""),
            "location": {
                "@type": "Place",
                "name": e.get("location", "Schweiz"),
                "address": {"@type": "PostalAddress", "addressLocality": e.get("location", ""), "addressCountry": "CH"}
            },
            "organizer": {
                "@type": "Organization",
                "name": "TrucksOnRoad",
                "url": "https://trucksonroad.ch"
            },
            "description": f"TrucksOnRoad Premium Foodtruck-Catering bei {e.get('event_type', 'Event')} in {e.get('location', 'der Schweiz')}",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled"
        })
    return schema_events



@router.get("/confirm-offer/{inquiry_id}/{token}")
async def public_get_offer_details(inquiry_id: str, token: str):
    """Return offer details for the confirmation page (no auto-confirm)"""
    inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
    if not inquiry:
        raise HTTPException(404, "Anfrage nicht gefunden")
    if inquiry.get("confirm_token") != token:
        raise HTTPException(400, "Ungültiger Link")
    already_confirmed = inquiry.get("status") not in ("offer_sent",)
    return {
        "inquiry_id": inquiry_id,
        "status": inquiry.get("status"),
        "already_confirmed": already_confirmed,
        "confirmed_at": inquiry.get("confirmed_at"),
        "payment_method": inquiry.get("payment_method"),
        "first_name": inquiry.get("first_name", ""),
        "last_name": inquiry.get("last_name", ""),
        "event_date": inquiry.get("event_date", ""),
        "event_time": inquiry.get("event_time", ""),
        "location": inquiry.get("location", ""),
        "guest_count": inquiry.get("guest_count", 0),
        "event_type": inquiry.get("event_type", ""),
        "selected_trucks": inquiry.get("selected_trucks", []),
        "invoice_amount": inquiry.get("invoice_amount", 0),
    }


@router.post("/confirm-offer/{inquiry_id}/{token}")
async def public_confirm_offer(inquiry_id: str, token: str, request: Request):
    """Confirm offer with payment method selection"""
    inquiry = await db.inquiries.find_one({"id": inquiry_id}, {"_id": 0})
    if not inquiry:
        raise HTTPException(404, "Anfrage nicht gefunden")
    if inquiry.get("confirm_token") != token:
        raise HTTPException(400, "Ungültiger Link")
    if inquiry.get("status") != "offer_sent":
        return {"message": "Offerte bereits bestätigt", "status": inquiry.get("status"), "already_confirmed": True}
    body = await request.json()
    payment_method = body.get("payment_method", "invoice")
    await db.inquiries.update_one({"id": inquiry_id}, {"$set": {
        "status": "confirmed",
        "payment_method": payment_method,
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }})
    return {"message": "Offerte erfolgreich bestätigt! Wir melden uns bei Ihnen.", "status": "confirmed"}
