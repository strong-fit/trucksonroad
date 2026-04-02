# TrucksOnRoad - Premium Foodtruck Website (PRD)

## Problem Statement
Premium, professionelle Website fuer "TrucksOnRoad" – Foodtruck-Unternehmen fuer Festivals, Firmenanlaesse und Private Events in der Schweiz.

## Tech Stack
- **Frontend:** React, Tailwind CSS, Shadcn/UI, React-Leaflet
- **Backend:** FastAPI, Motor (async MongoDB), JWT Auth
- **Database:** MongoDB
- **3rd Party:** Emergent Object Storage, Perplexity API (Event Scout), Gmail SMTP, Leaflet/OpenStreetMap/Nominatim

## Architecture (Post-Refactoring Feb 2026)
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
    auth_routes.py    (Login, Register, Logout, Refresh, Me)
    public.py         (Trucks, FAQs, Reviews, SEO, Sitemap, Agenda)
    customer.py       (Kundenportal: Anfragen, Profil)
    admin.py          (Admin: Anfragen, Kalender, Trucks, Personal, Finanzen, Export, Event-Scout)
```

## Completed Features

### Public Website
- [x] Homepage mit Hero, Truck-Karten, Reviews, FAQ, Instagram
- [x] Dedicated Truck-Seiten mit Details
- [x] Anfrage-Formular (vollstaendig)
- [x] Quick-Inquiry fuer schnelle Anfragen
- [x] Ueber uns, Kontakt Seiten
- [x] FAQ-Seite
- [x] Veranstalter PDF Download
- [x] Verfuegbarkeits-Kalender
- [x] Agenda (oeffentliche Events)
- [x] Mehrsprachig (DE/FR/IT/EN) mit Language Switcher

### Admin Dashboard
- [x] Anfragen-Management (CRUD, Status, Notizen)
- [x] Kalender/Verfuegbarkeit
- [x] Truck-Bearbeitung
- [x] FAQ-Verwaltung
- [x] Mitarbeiter-Verwaltung & Zuteilung
- [x] Bewertungs-Verwaltung
- [x] Finanz-Uebersicht (Umsatz, Kosten, Gewinn pro Event)
- [x] Routen-Planung mit Karte (Leaflet)
- [x] Export (CSV/PDF)
- [x] E-Mail-Vorschau (alle Templates in 4 Sprachen)
- [x] Einstellungen (SMTP, Firma, Social Media)
- [x] KI Event-Scout (Perplexity API, Auto-Scan, Bewerbung)
- [x] Rechnungs-Management (Status + Betrag)
- [x] Dynamische Sprach-Aenderung pro Anfrage

### Kundenportal
- [x] Login/Registrierung
- [x] Anfragen-Uebersicht
- [x] Datei-Upload/Download
- [x] Profil mit Sprach-Wahl
- [x] Dynamische Sprach-Aenderung

### SEO & AI
- [x] JSON-LD Structured Data (FoodEstablishment)
- [x] Sitemap.xml
- [x] Robots.txt (AI-Crawler erlaubt)
- [x] Meta-Tags, OpenGraph
- [x] Google Search Console Verifikation (manuell)

### E-Mail-System
- [x] 7+ Templates (Bestaetigung, Angebot, Status, Rechnung, Erinnerung, Datei, Event-Bewerbung)
- [x] Alle Templates in 4 Sprachen (DE/FR/IT/EN)
- [x] SMTP konfigurierbar via Admin

### Backend-Refactoring (02.04.2026)
- [x] server.py von 2353 auf 96 Zeilen reduziert
- [x] 12 Module erstellt (routes/, services/, etc.)
- [x] 100% Regression bestanden (37/37 Backend + 3/3 Frontend)

### Multi-Language Content (02.04.2026)
- [x] FR/IT Felder fuer alle 6 Trucks (name, tagline, description, menu, suitable_for)
- [x] FR/IT Felder fuer alle 8 FAQs (question, answer)
- [x] ~60 neue Translation-Keys fuer EventOrganizers, PrivateEvents, InquiryPage, Homepage
- [x] Alle hardcoded lang==='de' Ternaries durch t() ersetzt
- [x] 100% Regression bestanden (15/15 Backend + alle Frontend)

## Remaining Tasks
- [ ] Google Search Console setup (manueller Schritt)

## Test Reports
- iteration_13.json bis iteration_18.json: Alle 100% bestanden
