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
- [x] **Erweiterte SSR-SEO-Ausgabe**: Canonical Tags + serverseitige JSON-LD-Skripte fuer Layout, /trucks, /faq und Truck-Detailseiten (NEU 08.04.2026)
- [x] **FAQ-Interaktion verbessert**: FAQ-Toggles als echte Buttons mit data-testid und aria-expanded (NEU 08.04.2026)
- [x] **Sicheres CSS-Aufraeumen**: doppelte Font-Einbindung entfernt, mehrere `transition: all` auf gezielte Properties reduziert (NEU 08.04.2026)

## Remaining Tasks
- [ ] Impressum-Seite mit MWST/UID (wartet auf Nutzerdaten) (P2)
- [x] Google Search Console setup (laut Nutzer bereits erledigt)
- [ ] Emergent LLM Key Budget auffuellen (P3)

## Latest Update - 08.04.2026
- SSR-SEO fuer AI-Crawler/Google deutlich erweitert: Layout liefert jetzt serverseitig FoodEstablishment-, Organization-, WebSite- und Event-JSON-LD direkt im HTML.
- /trucks rendert zusaetzlich ItemList + BreadcrumbList serverseitig; /faq rendert FAQPage + BreadcrumbList serverseitig; Truck-Detailseiten rendert truck-spezifisches JSON-LD + BreadcrumbList serverseitig.
- Canonical Tags sind auf /trucks, /faq und /trucks/[slug] aktiv.
- Frontend-Produktions-Build aktualisiert (`yarn build`) und Frontend-Service neu gestartet, damit Next.js `next start` die neuen App-Router-Aenderungen ausliefert.

## Test Reports
- iteration_32: 100% (13/13 Backend, Frontend komplett)
- iteration_33: **100%** (9/9 Backend, alle 5 Sprachen + Quick Inquiry Widget)
- 08.04.2026: Frontend Smoke-Test auf Preview erfolgreich (/trucks, /faq, /trucks/burger-truck)
- 08.04.2026: Frontend-Testagent erfolgreich - Canonical + JSON-LD + FAQ-Toggles ohne Layout-Regression
- 08.04.2026: Backend-Testagent erfolgreich - API-/SEO-Endpunkte 11/11 bestanden
