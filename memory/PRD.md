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
- [x] **Landingpage-SEO erweitert**: Blog-, ContactPage-, AboutPage-, Service- und Breadcrumb-JSON-LD fuer /blog, /kontakt, /ueber-uns, /fuer-veranstalter und /private-events (NEU 08.04.2026)
- [x] **FAQ-Interaktion verbessert**: FAQ-Toggles als echte Buttons mit data-testid und aria-expanded (NEU 08.04.2026)
- [x] **Sicheres CSS-Aufraeumen**: doppelte Font-Einbindung entfernt, mehrere `transition: all` auf gezielte Properties reduziert (NEU 08.04.2026)

## Remaining Tasks
- [ ] Impressum-Seite mit MWST/UID (wartet auf Nutzerdaten) (P2)
- [x] Google Search Console setup (laut Nutzer bereits erledigt)
- [ ] Emergent LLM Key Budget auffuellen (P3)

## Latest Update - 10.04.2026
- **Homepage Premium Visual Upgrade** (8 Verbesserungen):
  1. Hero-Section: Ghost-Akzentbild entfernt, Hauptbild mit Gradient-Mask, Stats unterhalb der CTA-Buttons als Glassmorphism-Cards
  2. Section-Titel: Groesse reduziert von clamp(3rem,6vw,5.5rem) auf clamp(2.4rem,4.5vw,3.8rem) fuer bessere Balance
  3. Visuelle Abwechslung: CTA mit anthrazit-Hintergrund, Pricing mit Gradient-Background, Section-Divider
  4. So funktioniert's: Groessere Nummern (3.5rem), Hintergrund-Nummer-Effekt, verbindende Linie zwischen Steps
  5. Pricing: Featured-Card mit Glow/Shadow-Effekt, prominenteres BELIEBT-Badge mit Schatten
  6. Micro-Animationen: Cubic-bezier Transitions, Hover-Box-Shadows auf allen Cards, Button-Glow
  7. Kundenlogos: Frosted-Glass-Pill-Styling mit Border und Backdrop-Blur
  8. Trust-Bar: Gradient-Hintergrund, Count-Up-Animation fuer Zahlen (500+, 98%, 24H, 6)
- Frontend-Build aktualisiert und neu gestartet
- Testing-Agent bestaetigt: 100% Erfolgsrate, alle 13 Frontend-Features verifiziert

## Test Reports
- iteration_32: 100% (13/13 Backend, Frontend komplett)
- iteration_33: **100%** (9/9 Backend, alle 5 Sprachen + Quick Inquiry Widget)
- 08.04.2026: Frontend Smoke-Test auf Preview erfolgreich (/trucks, /faq, /trucks/burger-truck)
- 08.04.2026: Frontend-Testagent erfolgreich - Canonical + JSON-LD + FAQ-Toggles ohne Layout-Regression
- 08.04.2026: Backend-Testagent erfolgreich - API-/SEO-Endpunkte 11/11 bestanden
- 08.04.2026: Frontend Smoke-Test erfolgreich (/blog) inkl. visueller Kontrolle der neuen SEO-Landingpage-Ausgabe
- 08.04.2026: Frontend-Testagent erfolgreich - /blog, /kontakt, /ueber-uns, /fuer-veranstalter, /private-events mit Canonical + JSON-LD 5/5 bestanden
- 08.04.2026: Backend-Testagent erfolgreich - /api/blog, /api/seo/structured-data, /api/seo/events-schema, /api/seo/google-verification, /api/trucks 5/5 bestanden
- iteration_34: **100%** Frontend-Visual-Upgrade (13/13 Features verifiziert, alle 8 Verbesserungen bestanden)
