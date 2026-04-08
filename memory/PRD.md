# TrucksOnRoad - Premium Foodtruck Website (PRD)

## Problem Statement
Premium, professionelle Website fuer "TRUCKSonROAD" – Foodtruck-Unternehmen fuer Festivals, Firmenanlaesse und Private Events in der Schweiz. Conversion-optimiert mit SSR fuer beste SEO-Performance.

## Tech Stack
- **Frontend:** Next.js 16 (App Router, Production Build), React 19, Tailwind CSS
- **Backend:** FastAPI, Motor (async MongoDB), JWT Auth
- **Database:** MongoDB
- **3rd Party:** Emergent Object Storage, Perplexity API (Event Scout), LiteLLM, Gmail SMTP, Leaflet/OpenStreetMap

## Architecture
```
/app/backend/
  server.py, database.py, auth.py, models.py, seed.py
  services/ (email.py, pdf.py, storage.py, event_scout.py)
  routes/ (admin.py, auth_routes.py, customer.py, public.py)
/app/frontend/
  next.config.js, package.json
  src/app/ (Next.js App Router: 34 routes incl. /trucks)
  src/views/ (React components with "use client")
  src/components/ (Navbar, Footer, Providers, PublicShell, UI)
  src/contexts/ (AuthContext, LanguageContext)
  src/lib/ (api.js, translations.js)
```

## Completed Features

### Public Website
- [x] Homepage mit CRO-optimiertem Layout: Hero -> Use Cases -> So funktioniert's -> Pricing -> Trust -> Logos -> Reviews -> Trucks -> Quick Inquiry Widget -> CTA -> FAQ -> Blog -> Instagram
- [x] **Schnellanfrage-Widget** ("Rueckruf anfordern") auf Homepage mit Name + Telefon/E-Mail (NEU 08.04.2026)
- [x] Dedicated Truck-Seiten + Trucks-Uebersichtsseite (/trucks)
- [x] Anfrage-Formular mit Fortschrittsbalken und Inline-Validierung
- [x] Ueber uns, Kontakt, FAQ, Blog, Agenda, Veranstalter Seiten
- [x] WhatsApp Button
- [x] **5-Sprachen-Support komplett: DE, EN, FR, IT, ES** (ES NEU 08.04.2026)

### Offerte-Bestaetigungsseite
- [x] 2-Schritt-Flow: Event-Details anzeigen -> Zahlungsart waehlen -> Bestaetigen
- [x] Zahlungsart: Rechnung (30 Tage) oder Barzahlung (vor Ort)

### Admin Dashboard
- [x] Anfragen-Management mit Offerte-senden-Dialog (Betrag + Event-Vorschau)
- [x] Kalender, Truck-Bearbeitung, FAQ-Verwaltung, Mitarbeiter, Bewertungen
- [x] Finanzen, Routen (Leaflet), Export, KI Event-Scout, Blog mit Auto-Generator

### Kundenportal
- [x] Login/Registrierung, Anfragen, Datei-Upload, Profil

### SEO & SSR
- [x] Server-Side Rendering fuer alle oeffentlichen Seiten
- [x] JSON-LD Structured Data, Meta-Tags, OpenGraph, Sitemap.xml

## Remaining Tasks
- [ ] Impressum-Seite mit MWST/UID (wartet auf Nutzerdaten) (P2)
- [ ] Google Search Console setup (manueller Schritt) (P2)
- [ ] Emergent LLM Key Budget auffuellen (P3)

## Test Reports
- iteration_32: 100% (13/13 Backend, Frontend komplett)
- iteration_33: **100%** (9/9 Backend, alle 5 Sprachen + Quick Inquiry Widget)
