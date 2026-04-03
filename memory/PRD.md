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
    auth_routes.py    (Login, Register, Logout, Refresh, Me, Passwort-Reset)
    public.py         (Trucks, FAQs, Reviews, SEO, Sitemap, Agenda, Events-Schema)
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

### SEO & AI Suchmaschinen-Optimierung
- [x] JSON-LD Structured Data (FoodEstablishment + FAQ + FoodEvent Schema)
- [x] Sitemap.xml (alle Seiten + Truck-Detailseiten, Domain: trucksonroad.ch)
- [x] Robots.txt (AI-Crawler erlaubt: GPTBot, ChatGPT-User, PerplexityBot, ClaudeBot, Google-Extended)
- [x] Meta-Tags, OpenGraph, Twitter Cards
- [x] Hreflang-Tags (DE, EN, FR, IT + x-default)
- [x] Google Search Console Verifikation (manuell)
- [x] Event JSON-LD Schema fuer oeffentliche Agenda (/api/seo/events-schema)
- [x] Domain-Update: trucksonroad.ch ueberall konsistent

### E-Mail-System
- [x] 7+ Templates (Bestaetigung, Angebot, Status, Rechnung, Erinnerung, Datei, Event-Bewerbung)
- [x] Alle Templates in 4 Sprachen (DE/FR/IT/EN)
- [x] SMTP konfigurierbar via Admin

### Passwort-Management
- [x] "Passwort vergessen" per E-Mail (Token-basiert, 1h Ablauf, Single-Use)
- [x] "Passwort zuruecksetzen" Seite
- [x] "Passwort aendern" im Kundenportal und Admin

### Google Review Import (03.04.2026)
- [x] `source`-Feld fuer Bewertungen: "google" oder "placeholder"
- [x] Oeffentliche API blendet Platzhalter automatisch aus, sobald Google-Bewertungen vorhanden
- [x] Admin-UI: Quelle-Dropdown, Platzhalter/Google Badges, Info-Banner
- [x] Homepage zeigt "Google Review" Badge bei echten Bewertungen
- [x] 100% Tests bestanden (10/10 Backend + alle Frontend)

### Blog-System (03.04.2026)
- [x] Oeffentliche Blog-Seite (/blog) mit Kategorie-Filter (Ratgeber, Standorte, Tipps, Events, Regionen, Rezepte, News)
- [x] Blog-Detailseite (/blog/{slug}) mit Markdown-Rendering und CTA
- [x] Alle 4 Sprachen (DE/FR/IT/EN) fuer Titel, Auszug und Inhalt
- [x] Admin Blog-Verwaltung (/admin/blog) mit CRUD, Sprach-Tabs, Publish/Draft
- [x] 6 SEO-optimierte Platzhalter-Beitraege (Foodtruck Schweiz, Zuerich, Firmenanlass, Hochzeit, Bern/Basel/Luzern, Smash Burger)
- [x] Sitemap.xml automatisch mit Blog-URLs erweitert
- [x] Article JSON-LD Schema (/api/seo/blog-schema/{slug})
- [x] Navigation: Blog-Link in Navbar, Footer und Admin-Sidebar
- [x] 100% Tests bestanden (17/17 Backend + alle Frontend)

## Remaining Tasks
- [ ] Google Search Console setup (manueller Schritt durch den Nutzer)

## Test Reports
- iteration_3 bis iteration_23: Alle 100% bestanden
