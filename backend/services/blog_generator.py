import os
import uuid
import json
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

    system_msg = """Du bist ein erfahrener SEO-Texter fuer TrucksOnRoad, ein Premium-Foodtruck-Catering-Unternehmen in der Schweiz (Sitz: Wetzikon, Einsatzgebiet: ganze Schweiz).
Du schreibst professionelle, ausfuehrliche Blog-Artikel die fuer Google SEO optimiert sind.
Deine Artikel sind informativ, praxisnah und enthalten konkrete Tipps.
Du verwendest Markdown-Formatierung (##, ###, -, **bold**).
Jeder Artikel MUSS 800-1500 Woerter lang sein (nicht kuerzer!).
Du baust in jeden Artikel 2-3 interne Links ein, z.B.:
  - [Jetzt Foodtruck anfragen](/anfrage)
  - [Unsere Trucks entdecken](/trucks)
  - [Mehr Tipps im Blog](/blog)
  - [Kontaktiere uns](/kontakt)
  - [FAQ lesen](/faq)
Du erwaehnt konkrete Schweizer Staedte und Regionen.
Du nutzt Zwischen-Ueberschriften (H2/H3) fuer gute Struktur."""

    # Try gpt-4o first (more reliable), fallback to gpt-5.2
    models = ["gpt-4o", "gpt-5.2"]

    # Get existing post titles to avoid duplicates
    existing_titles = set()
    existing_posts = await db.blog_posts.find({}, {"title_de": 1, "_id": 0}).to_list(500)
    for ep in existing_posts:
        existing_titles.add(ep.get("title_de", "").lower().strip())

    prompt = f"""Erstelle einen ausfuehrlichen Blog-Artikel zum Thema: "{topic}"

BEREITS EXISTIERENDE ARTIKEL-TITEL (NICHT wiederholen, erstelle etwas ANDERES):
{chr(10).join(f'- {t}' for t in list(existing_titles)[:20])}

Antworte NUR im folgenden JSON-Format (kein anderer Text):
{{
  "slug": "kurzer-url-slug-ohne-sonderzeichen",
  "title_de": "Deutscher Titel (SEO-optimiert, max 70 Zeichen)",
  "title_en": "English Title",
  "title_fr": "Titre francais",
  "title_it": "Titolo italiano",
  "excerpt_de": "Kurzbeschreibung deutsch (max 160 Zeichen fuer Google Snippet)",
  "excerpt_en": "Short description english (max 160 chars)",
  "excerpt_fr": "Description courte francais",
  "excerpt_it": "Descrizione breve italiano",
  "content_de": "Ausfuehrlicher Artikel auf Deutsch mit Markdown. MINDESTENS 800 Woerter. Mit ## und ### Ueberschriften, Listen, **fett**. Baue 2-3 interne Links ein: [Jetzt anfragen](/anfrage), [Unsere Trucks](/trucks), [Mehr im Blog](/blog). Erwaehne TrucksOnRoad und Schweizer Staedte.",
  "content_en": "Full article in English (min 800 words) with internal links",
  "content_fr": "Article complet en francais (min 800 mots) avec liens internes",
  "content_it": "Articolo completo in italiano (min 800 parole) con link interni",
  "category": "Eine Kategorie: guide, locations, tipps, events, regionen, rezepte oder news",
  "tags": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"],
  "meta_title_de": "SEO Title fuer Google (max 60 Zeichen)",
  "meta_description_de": "SEO Meta Description (max 155 Zeichen, mit Call-to-Action)"
}}

Wichtig:
- Der slug muss URL-freundlich sein (nur Kleinbuchstaben, Bindestrich, keine Umlaute)
- MINDESTENS 800 Woerter pro Sprache im Content
- 2-3 interne Links pro Artikel einbauen
- Erwaehne TrucksOnRoad als Experten im Text
- Beziehe dich auf die Schweiz (Zuerich, Bern, Basel, Luzern, Genf etc.)
- Alle 4 Sprachen muessen vollstaendige, qualitativ hochwertige Inhalte haben
- Der Titel muss sich von existierenden Artikeln unterscheiden"""

    msg = UserMessage(text=prompt)
    response = None
    for model in models:
        chat_instance = LlmChat(
            api_key=api_key,
            session_id=f"{session_id}-{model}",
            system_message=system_msg
        ).with_model("openai", model)
        try:
            logger.info(f"Trying model: {model}")
            response = await chat_instance.send_message(msg)
            logger.info(f"Model {model} succeeded")
            break
        except Exception as e:
            logger.warning(f"Model {model} failed: {e}")
            continue

    if not response:
        logger.error("All models failed")
        return None

    try:
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

    # --- KI CONTENT CHECKER (KI #2) ---
    content_de = data.get("content_de", "")
    word_count = len(content_de.split())
    check_passed = True
    check_notes = []

    # Check 1: Minimum word count (flexible for fallback models)
    if word_count < 200:
        check_notes.append(f"Zu kurz: {word_count} Woerter (min 200)")
        check_passed = False

    # Check 2: Has internal links
    has_links = any(link in content_de for link in ["/anfrage", "/trucks", "/blog", "/kontakt", "/faq"])
    if not has_links:
        check_notes.append("Keine internen Links gefunden")

    # Check 3: Has proper structure (H2/H3)
    has_structure = "##" in content_de
    if not has_structure:
        check_notes.append("Keine Ueberschriften-Struktur (## / ###)")

    # Check 4: Duplicate title check
    title_lower = data.get("title_de", "").lower().strip()
    existing_titles_set = set()
    for ep in existing_posts:
        existing_titles_set.add(ep.get("title_de", "").lower().strip())
    if title_lower in existing_titles_set:
        check_notes.append("Duplicate Title erkannt!")
        check_passed = False

    # Check 5: AI quality check via second LLM call
    if check_passed:
        try:
            checker = None
            for cmodel in ["gpt-4o"]:
                try:
                    checker = LlmChat(
                        api_key=api_key,
                        session_id=f"blog-check-{uuid.uuid4().hex[:8]}",
                        system_message="Du bist ein strenger SEO-Content-Pruefer. Bewerte Blog-Artikel auf Qualitaet, Relevanz und SEO-Tauglichkeit."
                    ).with_model("openai", cmodel)
                    break
                except Exception:
                    continue

            check_prompt = f"""Pruefe diesen Blog-Artikel fuer ein Foodtruck-Catering-Unternehmen (TrucksOnRoad, Schweiz):

Titel: {data.get('title_de', '')}
Auszug: {data.get('excerpt_de', '')}
Woerteranzahl: {word_count}
Interne Links vorhanden: {has_links}

Antworte NUR mit JSON:
{{"pass": true/false, "score": 1-10, "reason": "kurze Begruendung"}}

Pruefkriterien:
- Ist der Inhalt relevant fuer Foodtruck/Catering/Events?
- Ist die Qualitaet akzeptabel (kein Spam oder voelliger Unsinn)?
- Gibt es einen Nutzen fuer den Leser?
Score ab 4 = pass. Nur offensichtlich schlechte Artikel ablehnen."""

            check_response = await checker.send_message(UserMessage(text=check_prompt))
            check_text = check_response.strip()
            if check_text.startswith("```"):
                check_text = check_text.split("\n", 1)[1].rsplit("```", 1)[0]
            check_result = json.loads(check_text)
            if not check_result.get("pass", True) or check_result.get("score", 10) < 4:
                check_notes.append(f"KI-Check failed: Score {check_result.get('score')}/10 - {check_result.get('reason', '')}")
                check_passed = False
            else:
                check_notes.append(f"KI-Check passed: Score {check_result.get('score')}/10")
        except Exception as e:
            logger.warning(f"Content check failed (publishing anyway): {e}")
            check_notes.append("KI-Check fehlgeschlagen (trotzdem veroeffentlicht)")

    if not check_passed:
        logger.warning(f"Blog post rejected by content checker: {check_notes}")
        return None

    logger.info(f"Content check: {check_notes}")

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
        "meta_title_de": data.get("meta_title_de", data.get("title_de", "")),
        "meta_description_de": data.get("meta_description_de", data.get("excerpt_de", "")),
        "author": "TrucksOnRoad KI",
        "is_published": True,
        "ai_generated": True,
        "word_count": word_count,
        "quality_score": next((int(n.split("Score ")[1].split("/")[0]) for n in check_notes if "Score" in n), 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    await db.blog_posts.insert_one(post)
    post.pop("_id", None)
    logger.info(f"AI Blog post created: {post['slug']}")
    return post
