"""
Updates the Burger Truck images to reflect the real Pferdeanhänger (horse trailer) truck,
and creates a new blog post about Stadtfest Wetzikon 2026.
Run from /app/backend with proper env vars set.
"""
import os
import asyncio
import re
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient


# === REAL EVENT PHOTOS – Stadtfest Wetzikon 2026 ===
ASSETS_BASE = "https://customer-assets.emergentagent.com/job_c7d7e05b-941f-4a81-be34-a87b5e1bfbb0/artifacts"

# Side view of the dark Burger horse trailer at night with marquee BURGER lights (the full truck)
TRUCK_HERO = f"{ASSETS_BASE}/5nu0g6zd_IMG_3311.jpeg"

GALLERY = [
    TRUCK_HERO,                                                       # full side view night
    f"{ASSETS_BASE}/qvojhtm5_a9c9c1f9-5318-4962-8842-68fea553e18a.jpeg",  # day side w/ menu + waving
    f"{ASSETS_BASE}/5jisg6w9_66c78aa1-a1a3-4bfa-8aac-0b92058990cd.jpeg",  # BURGER lights front close
    f"{ASSETS_BASE}/qhzla3l0_e84b202b-039d-4f10-9abb-6f9eba688cb3.jpeg",  # BURGER night with queue
    f"{ASSETS_BASE}/89vxpebg_7849BED6-074B-410A-AC2D-588B4FF9F398.png",   # BURGER smiling
    f"{ASSETS_BASE}/cyioba3g_b74876cc-d204-41d1-883e-01e393fcc362.jpeg",  # chef + buns on grill
    f"{ASSETS_BASE}/3eoot6oi_d0fc4907-570f-4e6e-b772-f9783b2dfd41.jpeg",  # two-woman team selfie
    f"{ASSETS_BASE}/6co95yxu_66222ef6-9e69-44a0-9bf2-cfed7e60df0d.jpeg",  # grill action team
]

BLOG_TITLE_DE = "Rückblick: Stadtfest Wetzikon 2026 – unvergessliche Burger-Momente"
BLOG_SLUG = "stadtfest-wetzikon-2026-burger-truck-rueckblick"
BLOG_EXCERPT_DE = ("Tausende Gäste, eine leuchtende BURGER-Marquee und unzählige hausgemachte Poulet-Burger – "
                   "der TRUCKSonROAD Pferdeanhänger-Burger-Truck war das Highlight am Stadtfest Wetzikon 2026.")

BLOG_CONTENT_DE = """## Ein Wochenende voller Foodtruck-Magie

Das **Stadtfest Wetzikon 2026** war für unser Team ein absolutes Highlight. Unser markanter
schwarzer **Pferdeanhänger-Burger-Truck** mit der leuchtenden BURGER-Marquee-Schrift
verwandelte die Bahnhofstrasse in einen Hotspot für Foodlover aus der ganzen Region.

Vom Sonnenuntergang bis tief in die Nacht zauberten unsere Köche **handgemachte Poulet-Burger
mit hausgemachter Sauce und gerösteten Zwiebeln** auf die Hot-Plate. Schweizer Poulet,
frische Brioche-Buns, knusprige Frites – nichts von der Stange, alles mit Leidenschaft.

## Zahlen, die uns sprachlos machen

- Über **2'000 Burger** in zwei Festabenden
- Bis zu **120 Gäste pro Stunde** an der Theke
- 6-köpfiges Team, **9 Stunden non-stop** am Service
- **0 Reklamationen** – nur Lob, Selfies und Komplimente

## Warum unser Pferdeanhänger-Truck etwas Besonderes ist

Aus einem klassischen Pferdetransporter haben wir einen **rollenden Burger-Tempel** gebaut.
Die Lichterketten, die warmweisse Beleuchtung und das ikonische BURGER-Marquee schaffen
eine Atmosphäre, die man auf normalen Foodtrucks nicht findet. Egal ob **Stadtfest**,
**Firmenanlass** oder **Hochzeit** – unser Burger-Truck wird zum Hingucker des Abends.

## Galerie – Stadtfest Wetzikon 2026

Schaut Euch unsere Lieblings-Momente aus dem Festwochenende an. Jedes Bild erzählt eine
Geschichte von Teamwork, Gastfreundschaft und echtem Foodtruck-Spirit.

## Lust auf unseren Burger-Truck bei eurem Event?

Ob **Festival**, **Geburtstag**, **Firmenevent** oder **Hochzeit** – wir bringen das volle
Stadtfest-Erlebnis zu Dir. **Über 500 erfolgreiche Events**, **98 % Kundenzufriedenheit**,
Antwortzeit unter 24 Stunden.

[Jetzt unverbindlich anfragen](https://trucksonroad.ch/anfrage) – wir freuen uns auf Dein Event.
"""

BLOG_META_TITLE_DE = "Stadtfest Wetzikon 2026 – Rückblick TRUCKSonROAD Burger-Truck"
BLOG_META_DESC_DE = ("Über 2'000 Burger, 120 Gäste pro Stunde, die ikonische BURGER-Marquee: Unser Rückblick "
                     "auf den TRUCKSonROAD Pferdeanhänger-Burger-Truck am Stadtfest Wetzikon 2026.")


async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]

    # 1) Update Burger Truck
    result = await db.trucks.update_one(
        {"slug": "burger-truck"},
        {"$set": {
            "image": TRUCK_HERO,
            "gallery": GALLERY,
        }}
    )
    print(f"[trucks] burger-truck updated: matched={result.matched_count}, modified={result.modified_count}")

    # 2) Upsert Blog Post
    now = datetime.now(timezone.utc).isoformat()
    existing = await db.blog_posts.find_one({"slug": BLOG_SLUG})
    doc = {
        "slug": BLOG_SLUG,
        "title_de": BLOG_TITLE_DE,
        "title_en": "Recap: Wetzikon City Festival 2026 – unforgettable burger moments",
        "title_fr": "Rétrospective : Fête de la ville de Wetzikon 2026 – nos burgers inoubliables",
        "title_it": "Rétrospettiva: Stadtfest Wetzikon 2026 – burger indimenticabili",
        "excerpt_de": BLOG_EXCERPT_DE,
        "excerpt_en": "Thousands of guests, a glowing BURGER marquee and countless homemade chicken burgers – our trailer truck was the highlight of Wetzikon City Festival 2026.",
        "excerpt_fr": "Des milliers d'invités, une enseigne BURGER lumineuse et d'innombrables burgers au poulet maison – notre food truck a fait sensation à la fête de la ville de Wetzikon 2026.",
        "excerpt_it": "Migliaia di ospiti, l'insegna BURGER illuminata e tantissimi burger di pollo fatti in casa – il nostro food truck è stato il protagonista dello Stadtfest Wetzikon 2026.",
        "content_de": BLOG_CONTENT_DE,
        "content_en": BLOG_CONTENT_DE,  # placeholder; same content for now
        "content_fr": BLOG_CONTENT_DE,
        "content_it": BLOG_CONTENT_DE,
        "category": "Events",
        "image": TRUCK_HERO,
        "gallery": GALLERY,
        "tags": ["Stadtfest", "Wetzikon", "Burger", "Foodtruck", "Event 2026", "Pferdeanhänger"],
        "author": "TRUCKSonROAD",
        "is_published": True,
        "meta_title_de": BLOG_META_TITLE_DE,
        "meta_description_de": BLOG_META_DESC_DE,
        "updated_at": now,
    }
    if existing:
        await db.blog_posts.update_one({"_id": existing["_id"]}, {"$set": doc})
        print(f"[blog] updated existing post: {BLOG_SLUG}")
    else:
        doc["id"] = str(uuid.uuid4())
        doc["created_at"] = now
        await db.blog_posts.insert_one(doc)
        print(f"[blog] created new post: {BLOG_SLUG} (id={doc['id']})")

    print("\n=== Done ===")
    print(f"Truck page:  /trucks/burger-truck")
    print(f"Blog post:   /blog/{BLOG_SLUG}")


if __name__ == "__main__":
    asyncio.run(main())
