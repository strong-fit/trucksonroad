import asyncio
import logging
import json as json_mod
from datetime import datetime, timezone, timedelta
import uuid
import httpx
from database import db
from services.email import (
    get_email_settings, get_email_t, send_email_background, send_email_sync,
    build_event_reminder_email, build_event_scan_notification_email
)

logger = logging.getLogger(__name__)

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


async def get_perplexity_key():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return (s or {}).get("perplexity_api_key", "")


async def call_perplexity_search(api_key: str, query: str, extra_context: str = "") -> list:
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
    try:
        settings = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
        api_key = settings.get("perplexity_api_key", "")
        if not api_key:
            logger.info("Event scan skipped: no Perplexity API key")
            return

        sources = settings.get("scout_sources", [])
        keywords = settings.get("scout_keywords", ["Festival", "Weihnachtsmarkt", "Strassenfest", "Food Festival", "Markt"])

        source_context = ""
        if sources:
            source_context = "Durchsuche auch diese bekannten Event-Webseiten: " + ", ".join(sources)

        existing = await db.scouted_events.find({}, {"_id": 0, "name": 1}).to_list(1000)
        existing_names = set(e.get("name", "").lower().strip() for e in existing)

        all_new_events = []

        for keyword in keywords:
            query = f"Finde aktuelle und kommende Events: {keyword} in der Schweiz 2025/2026/2027"
            events = await call_perplexity_search(api_key, query, source_context)
            for ev in events:
                name = (ev.get("name") or "").strip()
                if not name:
                    continue
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
                    pass

        await db.settings.update_one({"type": "general"}, {"$set": {
            "scout_last_scan": datetime.now(timezone.utc).isoformat(),
            "scout_last_scan_count": len(all_new_events)
        }}, upsert=True)

        if all_new_events:
            notification_email = settings.get("notification_email", "")
            if notification_email and settings.get("email_notifications"):
                html = build_event_scan_notification_email(all_new_events)
                await send_email_background(notification_email, f"Event-Scout: {len(all_new_events)} neue Schweizer Events gefunden", html)

        logger.info(f"Event scan complete: {len(all_new_events)} new events found")

    except Exception as e:
        logger.error(f"Event scan failed: {e}")


async def send_event_reminders():
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
                    send_email_sync(inq["email"], f"{it['subject_reminder'].format(days=reminder_days)} – TRUCKSonROAD", html, settings)
                except Exception:
                    pass
                await db.reminders.insert_one({"inquiry_id": inq["id"], "type": "event_reminder", "sent_at": datetime.now(timezone.utc).isoformat()})
                logger.info(f"Event reminder sent for inquiry {inq['id']} to {inq['email']}")
    except Exception as e:
        logger.warning(f"Event reminder check failed: {e}")


async def event_reminder_loop():
    while True:
        await asyncio.sleep(6 * 3600)
        await send_event_reminders()


async def event_scan_loop():
    while True:
        await asyncio.sleep(24 * 3600)
        settings = await db.settings.find_one({"type": "general"}, {"_id": 0}) or {}
        if settings.get("scout_auto_scan"):
            await run_event_scan()
