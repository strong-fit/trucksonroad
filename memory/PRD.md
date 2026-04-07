# TrucksOnRoad - Premium Foodtruck Website (PRD)

## Problem Statement
Premium, professionelle Website fuer "TRUCKSonROAD" – Foodtruck-Unternehmen fuer Festivals, Firmenanlaesse und Private Events in der Schweiz. Conversion-optimiert mit SSR fuer beste SEO-Performance.

## Tech Stack
- **Frontend:** Next.js 16 (App Router, Production Build), React 19, Tailwind CSS, Shadcn/UI, React-Leaflet
- **Backend:** FastAPI, Motor (async MongoDB), JWT Auth
- **Database:** MongoDB
- **3rd Party:** Emergent Object Storage, Perplexity API (Event Scout), LiteLLM (GPT-4o/5.2), Gmail SMTP, Leaflet/OpenStreetMap/Nominatim

## Architecture
```
/app/backend/
  server.py          (~96 Zeilen - App, Middleware, Startup, Router)
  database.py         (DB-Verbindung)
  auth.py             (JWT, Passwort-Hashing, get_current_user)
  models.py           (Pydantic Models)
  seed.py             (Seed-Daten: 6 Trucks, 8 FAQs)
  services/
    email.py          (E-Mail-Templates + 4-Sprachen-i18n + SMTP)
    pdf.py            (PDF: Angebot, Veranstalter, Export)
    storage.py        (Emergent Object Storage)
    event_scout.py    (Perplexity AI + Auto-Scan + Background Tasks)
  routes/
    auth_routes.py    (Login, Register, Logout, Refresh, Me, Passwort-Reset)
    public.py         (Trucks, FAQs, Reviews, SEO, Sitemap, Agenda, Offer Confirm)
    customer.py       (Kundenportal: Anfragen, Profil)
    admin.py          (Admin: Anfragen, Kalender, Trucks, Personal, Finanzen, Export, Event-Scout)
/app/frontend/
  next.config.js      (Rewrites /api -> backend, env mapping)
  src/app/            (Next.js App Router - 34 routes incl. /trucks)
  src/views/          (Migrated React components with "use client")
  src/components/     (Navbar, Footer, Providers, PublicShell, UI)
  src/contexts/       (AuthContext, LanguageContext)
  src/lib/            (api.js, translations.js)
```

## Completed Features

### Public Website
- [x] Homepage mit CRO-optimiertem Layout: Hero -> Use Cases -> So funktioniert's -> Pricing -> Trust -> Logos -> Reviews -> Trucks -> CTA -> FAQ -> Blog
- [x] Emotionaler Hero: "EINZIGARTIGE FOODTRUCKS FUER EVENTS, DIE IN ERINNERUNG BLEIBEN."
- [x] Use-Cases, Pricing, Trust-Zahlen, Kundenlogos Sektionen
- [x] Dedicated Truck-Seiten mit Galerie, Video, Story, Menue
- [x] **Trucks-Uebersichtsseite (/trucks)** mit SSR SEO Meta-Tags (NEU, 07.04.2026)
- [x] Anfrage-Formular mit **Fortschrittsbalken** und **Inline-Validierung** (VERBESSERT, 07.04.2026)
- [x] Ueber uns, Kontakt, FAQ, Blog, Agenda, Veranstalter Seiten
- [x] WhatsApp Button
- [x] Mehrsprachig (DE/FR/IT/EN)

### Offerte-Bestaetigungsseite (KOMPLETT NEU, 07.04.2026)
- [x] 2-Schritt-Flow: Event-Details anzeigen → Zahlungsart waehlen → Bestaetigen
- [x] Zeigt: Datum, Ort, Gaeste, Eventtyp, Trucks, Offerte-Betrag (CHF)
- [x] Zahlungsart: Rechnung (30 Tage) oder Barzahlung (vor Ort)
- [x] Status-Anzeige: "Bereits bestaetigt" mit Datum und Zahlungsart
- [x] Backend: GET liefert Vorschau, POST bestaetigt mit Zahlungsart

### Admin Dashboard
- [x] Anfragen-Management, Kalender, Truck-Bearbeitung, FAQ-Verwaltung
- [x] **Offerte-senden-Dialog** mit Betrag-Eingabe und Event-Vorschau (NEU, 07.04.2026)
- [x] Mitarbeiter, Bewertungen, Finanzen, Routen (Leaflet), Export
- [x] KI Event-Scout, Rechnungen, E-Mail-Templates, Einstellungen
- [x] Blog-Verwaltung mit KI Auto-Blog Generator (GPT-5.2)

### Kundenportal
- [x] Login/Registrierung, Anfragen, Datei-Upload, Profil

### SEO & SSR (Next.js Migration)
- [x] Echtes Server-Side Rendering: Voller HTML-Content im initialen Response
- [x] 34 Routen (32 statisch prerendered, 2 dynamisch)
- [x] JSON-LD Structured Data (FoodEstablishment Schema) im HTML Head
- [x] Meta-Tags, OpenGraph, Twitter Cards korrekt
- [x] Sitemap.xml mit 27+ Seiten (inkl. /trucks)

## Remaining Tasks
- [ ] Impressum-Seite mit MWST/UID (wartet auf Nutzerdaten) (P2)
- [ ] Google Search Console setup (manueller Schritt) (P2)
- [ ] Mehrsprachigkeit FR/IT komplett befuellen (P2)
- [ ] Emergent LLM Key Budget auffuellen (P3)

## Test Reports
- iteration_31: 100% bestanden (Backend + Frontend + SSR + Navigation)
- iteration_32: **100% bestanden** (13/13 Backend, alle Frontend-Features: Offerte-Bestaetigung, Admin-Dialog, Fortschrittsbalken, Inline-Validierung, /trucks-Seite)
