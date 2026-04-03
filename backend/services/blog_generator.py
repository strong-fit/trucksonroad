import os
import uuid
import random
import logging
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
from database import db

logger = logging.getLogger(__name__)

FOOD_TRUCK_TOPICS = [
    "Foodtruck Catering fuer Sommerfeste in der Schweiz",
    "Street Food Trends 2026: Was kommt auf Schweizer Events",
    "Foodtruck mieten fuer Geburtstagsfeiern: Tipps und Ideen",
    "Die besten Foodtruck-Gerichte fuer grosse Events",
    "Nachhaltiges Catering: Oekologische Foodtrucks im Trend",
    "Foodtruck vs. klassisches Catering: Was passt besser?",
    "Winterevents mit Foodtruck: So wird's warm und lecker",
    "Foodtruck Catering fuer Messen und Kongresse",
    "Street Food Festival organisieren: Ein Leitfaden",
    "Foodtruck Hochzeit im Sommer: Die schoensten Locations",
    "Vegane Foodtrucks: Pflanzliches Catering fuer Events",
    "Foodtruck Team Building: Kochen als Teamevent",
    "Open Air Kino mit Foodtruck: Das perfekte Erlebnis",
    "Foodtruck Catering fuer Weihnachtsfeiern und Adventsmaerkte",
    "Die beliebtesten Foodtruck-Konzepte in der Schweiz",
    "Foodtruck fuer Schulanlaesse und Vereinsfeste",
    "Asiatische Streetfood-Trends auf Schweizer Foodtrucks",
    "Dessert-Trucks: Suesse Versuchungen fuer Events",
    "Foodtruck Catering bei Sportevents und Turnieren",
    "Brunch mit Foodtruck: Der neue Trend fuer Wochenend-Events",
    "Foodtruck mieten in der Westschweiz: Genf, Lausanne, Fribourg",
    "Burger-Trends 2026: Was auf dem Foodtruck-Grill landet",
    "Foodtruck fuer Firmen-Sommerfeste: Planung und Kosten",
    "Regionale Zutaten auf dem Foodtruck: Schweizer Qualitaet",
    "Foodtruck-Catering fuer Taufen und Familienfeiern",
    "Die Geschichte der Foodtrucks in der Schweiz",
    "Foodtruck mieten fuer Produktlancierungen und PR-Events",
    "Bowl-Trends: Gesunde Gerichte vom Foodtruck",
    "Foodtruck-Events in Zuerich: Die besten Plaetze und Termine",
    "Catering-Trends 2026: Warum Foodtrucks immer beliebter werden",
]


async def get_blog_image(category: str, tags: list) -> str:
    """Get a relevant curated image for the blog post based on category."""
    CATEGORY_IMAGES = {
        "guide": [
            "https://images.unsplash.com/photo-1565123409695-7b5ef63a2efb?w=800&q=80",
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
            "https://images.unsplash.com/photo-1460306855393-0410f61241c7?w=800&q=80",
        ],
        "locations": [
            "https://images.unsplash.com/photo-1515542622106-78bda8ba0e5b?w=800&q=80",
            "https://images.unsplash.com/photo-1527668752968-14dc70a27c95?w=800&q=80",
            "https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?w=800&q=80",
        ],
        "tipps": [
            "https://images.unsplash.com/photo-1540914124281-342587941389?w=800&q=80",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
            "https://images.unsplash.com/photo-1556909114-44e3e70034e2?w=800&q=80",
        ],
        "events": [
            "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80",
            "https://images.unsplash.com/photo-1529543544282-ea6407407db9?w=800&q=80",
            "https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=800&q=80",
        ],
        "regionen": [
            "https://images.unsplash.com/photo-1527668752968-14dc70a27c95?w=800&q=80",
            "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?w=800&q=80",
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
        ],
        "rezepte": [
            "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80",
            "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=800&q=80",
            "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&q=80",
        ],
        "news": [
            "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
            "https://images.unsplash.com/photo-1565123409695-7b5ef63a2efb?w=800&q=80",
        ],
    }
    images = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["news"])
    return random.choice(images)


async def generate_blog_post():
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        logger.error("EMERGENT_LLM_KEY not set")
        return None

    used_slugs = set()
    existing = await db.blog_posts.find({}, {"slug": 1, "_id": 0}).to_list(500)
    for e in existing:
        used_slugs.add(e["slug"])

    topic = random.choice(FOOD_TRUCK_TOPICS)
    session_id = f"blog-gen-{uuid.uuid4().hex[:8]}"

    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message="""Du bist ein erfahrener SEO-Texter fuer TrucksOnRoad, ein Premium-Foodtruck-Catering-Unternehmen in der Schweiz.
Du schreibst professionelle Blog-Artikel die fuer Google SEO optimiert sind.
Deine Artikel sind informativ, praxisnah und enthalten konkrete Tipps.
Du verwendest Markdown-Formatierung (##, ###, -, **bold**).
Jeder Artikel sollte 400-600 Woerter lang sein."""
    ).with_model("openai", "gpt-5.2")

    prompt = f"""Erstelle einen Blog-Artikel zum Thema: "{topic}"

Antworte NUR im folgenden JSON-Format (kein anderer Text):
{{
  "slug": "kurzer-url-slug-ohne-sonderzeichen",
  "title_de": "Deutscher Titel (SEO-optimiert, max 70 Zeichen)",
  "title_en": "English Title",
  "title_fr": "Titre francais",
  "title_it": "Titolo italiano",
  "excerpt_de": "Kurzbeschreibung deutsch (max 160 Zeichen fuer SEO)",
  "excerpt_en": "Short description english",
  "excerpt_fr": "Description courte francais",
  "excerpt_it": "Descrizione breve italiano",
  "content_de": "Vollstaendiger Artikel auf Deutsch mit Markdown (## Titel, ### Untertitel, - Listen, **fett**). 400-600 Woerter.",
  "content_en": "Full article in English with Markdown",
  "content_fr": "Article complet en francais avec Markdown",
  "content_it": "Articolo completo in italiano con Markdown",
  "category": "Eine Kategorie: guide, locations, tipps, events, regionen, rezepte oder news",
  "tags": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"]
}}

Wichtig:
- Der slug muss URL-freundlich sein (nur Kleinbuchstaben, Bindestrich, keine Umlaute)
- Erwaehne TrucksOnRoad als Experten im Text
- Beziehe dich auf die Schweiz (Staedte, Regionen, Kultur)
- Alle 4 Sprachen muessen vollstaendige, qualitativ hochwertige Inhalte haben"""

    msg = UserMessage(text=prompt)
    response = await chat.send_message(msg)

    try:
        import json
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        data = json.loads(text)
    except Exception as e:
        logger.error(f"Failed to parse AI response: {e}")
        logger.error(f"Response was: {response[:500]}")
        return None

    slug = data.get("slug", "").strip()
    if not slug or slug in used_slugs:
        slug = f"{slug or 'post'}-{uuid.uuid4().hex[:6]}"

    post = {
        "id": str(uuid.uuid4()),
        "slug": slug,
        "title_de": data.get("title_de", ""),
        "title_en": data.get("title_en", ""),
        "title_fr": data.get("title_fr", ""),
        "title_it": data.get("title_it", ""),
        "excerpt_de": data.get("excerpt_de", ""),
        "excerpt_en": data.get("excerpt_en", ""),
        "excerpt_fr": data.get("excerpt_fr", ""),
        "excerpt_it": data.get("excerpt_it", ""),
        "content_de": data.get("content_de", ""),
        "content_en": data.get("content_en", ""),
        "content_fr": data.get("content_fr", ""),
        "content_it": data.get("content_it", ""),
        "category": data.get("category", "tipps"),
        "image": await get_blog_image(data.get("category", "tipps"), data.get("tags", [])),
        "tags": data.get("tags", []),
        "author": "TrucksOnRoad KI",
        "is_published": True,
        "ai_generated": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    await db.blog_posts.insert_one(post)
    post.pop("_id", None)
    logger.info(f"AI Blog post created: {post['slug']}")
    return post
