# TrucksOnRoad - Premium Foodtruck Website (PRD)

## Problem Statement
Premium, professionelle Website fuer "TRUCKSonROAD" – Foodtruck-Unternehmen fuer Festivals, Firmenanlaesse und Private Events in der Schweiz. Conversion-optimiert mit SSR fuer beste SEO-Performance.

## Tech Stack
- **Frontend:** Next.js 16 (App Router, Production Build), React 19, Tailwind CSS, Shadcn/UI, React-Leaflet
- **Backend:** FastAPI, Motor (async MongoDB), JWT Auth
- **Database:** MongoDB
- **3rd Party:** Emergent Object Storage, Perplexity API (Event Scout), LiteLLM (GPT-4o/5.2), Gmail SMTP, Leaflet/OpenStreetMap/Nominatim

## Architecture (Post Next.js Migration, Apr 2026)
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
    public.py         (Trucks, FAQs, Reviews, SEO, Sitemap, Agenda, Events-Schema)
    customer.py       (Kundenportal: Anfragen, Profil)
    admin.py          (Admin: Anfragen, Kalender, Trucks, Personal, Finanzen, Export, Event-Scout)
/app/frontend/
  next.config.js      (Rewrites /api -> backend, env mapping, allowedDevOrigins)
  src/app/            (Next.js App Router - 33 routes, static + dynamic)
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
- [x] Anfrage-Formular (vollstaendig, vorausgefuellt via Query Params)
- [x] Ueber uns, Kontakt, FAQ, Blog, Agenda, Veranstalter Seiten
- [x] WhatsApp Button
- [x] Mehrsprachig (DE/FR/IT/EN)

### Admin Dashboard
- [x] Anfragen-Management, Kalender, Truck-Bearbeitung, FAQ-Verwaltung
- [x] Mitarbeiter, Bewertungen, Finanzen, Routen (Leaflet), Export
- [x] KI Event-Scout, Rechnungen, E-Mail-Templates, Einstellungen
- [x] Blog-Verwaltung mit KI Auto-Blog Generator (GPT-5.2)

### Kundenportal
- [x] Login/Registrierung, Anfragen, Datei-Upload, Profil

### SEO & SSR (Next.js Migration, 04.04.2026)
- [x] **MIGRATION VON CRA ZU NEXT.JS 16 APP ROUTER ABGESCHLOSSEN**
- [x] Echtes Server-Side Rendering: Voller HTML-Content im initialen Response
- [x] 33 Routen (31 statisch prerendered, 2 dynamisch: /trucks/[slug], /blog/[slug])
- [x] JSON-LD Structured Data (FoodEstablishment Schema) im HTML Head
- [x] Meta-Tags, OpenGraph, Twitter Cards korrekt im SSR-Response
- [x] Production Build (next build && next start) fuer volle Hydration
- [x] Client-Side Navigation funktioniert (Next.js Link/Router)
- [x] Leaflet dynamisch importiert (ssr: false) fuer Admin Routen
- [x] useSearchParams in Suspense Boundary gewrappt
- [x] Sitemap.xml, Robots.txt, Hreflang-Tags

### E-Mail, Passwort, Google Reviews, Blog, KI-Features
- [x] Alle wie zuvor (siehe vorherige PRD-Eintraege)

## Remaining Tasks
- [ ] Impressum-Seite mit MWST/UID (wartet auf Nutzerdaten) (P2)
- [ ] Google Search Console setup (manueller Schritt) (P2)
- [ ] Emergent LLM Key Budget auffuellen (P3)

## Test Reports
- iteration_3 bis iteration_29: Alle bestanden (pre-migration)
- iteration_30: SSR 100%, Client-Hydration 0% (dev mode Proxy-Problem identifiziert)
- iteration_31: **100% bestanden** (Backend 44/44, Frontend alle Seiten + Hydration + Navigation)
