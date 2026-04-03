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
- [x] Homepage mit CRO-optimiertem Layout: Hero → Use Cases → So funktioniert's → Trust → Reviews → Trucks → CTA → FAQ → Blog
- [x] Emotionaler Hero: "MACH DEIN EVENT UNVERGESSLICH." mit 500+ Events, 24h Antwortzeit, 6 Konzepte
- [x] Use-Cases Sektion: Firmenanlass, Hochzeit, Festival, Geburtstag (alle verlinken auf /anfrage)
- [x] "So funktioniert's" Sektion: 3 Schritte (Anfrage → Angebot → Event geniessen)
- [x] Trust-Zahlen Bar: 500+ Events, 98% Zufriedenheit, 24h Antwort, 6 Konzepte
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

### KI Auto-Blog Generator (03.04.2026)
- [x] GPT-5.2 generiert automatisch 4-sprachige Foodtruck-Artikel (DE/FR/IT/EN)
- [x] 30 vordefinierte Themen (Foodtruck Catering, Events, Regionen, Trends, Rezepte)
- [x] Admin: "Jetzt generieren" Button fuer sofortige Erstellung
- [x] Auto-Post Modus: Konfigurierbar (6h, 12h, 24h, 48h, 72h Intervall)
- [x] KI-Badge bei KI-generierten Beitraegen im Admin
- [x] "Beliebte Beitraege" Sektion auf der Startseite (3 neueste Posts)
- [x] Automatische Bild-Zuweisung: Kuratierte Unsplash-Bilder nach Kategorie
- [x] Alle Posts loeschbar im Admin
- [x] 100% Tests bestanden (11/11 Backend + alle Frontend)

### SEO Pro-Optimierung (03.04.2026)
- [x] KI Content Checker (KI #2): Zweite KI prueft Qualitaet, Duplicate Content, Struktur (Score 1-10) vor Veroeffentlichung
- [x] Dynamische SEO Meta-Tags pro Blog-Post (React Helmet): Title, Description, OG-Tags, Canonical
- [x] data-rh Attribute in index.html fuer saubere Helmet-Uebernahme
- [x] Laengere Artikel: 800-1500 Woerter statt 400-600
- [x] Interne Verlinkung: KI baut automatisch 2-3 interne Links ein (/anfrage, /trucks, /blog, /kontakt, /faq)
- [x] Markdown-Links werden als klickbare React-Router Links gerendert
- [x] "Aehnliche Beitraege" Sektion am Ende jedes Blog-Posts (3 verwandte Artikel)
- [x] Meta Title + Meta Description fuer alle Seed-Beitraege hinzugefuegt
- [x] Existing-Title-Check verhindert doppelte Artikel-Themen

### Homepage CRO-Redesign (03.04.2026)
- [x] Hero-Sektion: Emotionale Headline statt Feature-Listing, "MACH DEIN EVENT UNVERGESSLICH."
- [x] Use-Cases Grid (NEU): 4 Event-Typen mit Bildern, Icons, Beschreibung (Firmenanlass, Hochzeit, Festival, Geburtstag)
- [x] Use-Cases → Anfrage mit vorausgefülltem Event-Typ (Query-Parameter ?type=0-3)
- [x] "So funktioniert's" (NEU): 3-Schritte-Prozess (Anfrage → Angebot → Event geniessen)
- [x] Trust-Zahlen Bar (NEU): Gold-Hintergrund mit 500+ Events, 98% Zufriedenheit, 24h, 6 Konzepte
- [x] Reviews nach oben verschoben (direkt nach Trust-Bar)
- [x] Alle neuen Texte in 4 Sprachen (DE/FR/IT/EN)
- [x] Mobile-responsive (Use Cases 1-Spalte, Trust 2x2, How-it-works 1-Spalte)
- [x] 100% Tests bestanden (iteration_26)

### Truck-Detailseiten Emotional Redesign (03.04.2026)
- [x] Immersiver Hero: Vollbild-Truck-Bild mit Name, Tagline & Badge-Overlay
- [x] Quick Stats Bar: Kapazität, Aufbauzeit, Strom, Event-Typen (mit Icons)
- [x] "Das Erlebnis" Story-Sektion statt technischer Beschreibung
- [x] "Perfekt für dein Event" Karten: Jeder geeignete Event-Typ als klickbare Karte → Anfrage
- [x] Menü-Sektion mit eleganten Karten-Layout
- [x] Kunden-Zitat/Testimonial Sektion
- [x] Technische Details: Klappbar (standardmässig geschlossen)
- [x] Emotionaler CTA: "DIESEN TRUCK FÜR DEIN EVENT BUCHEN" mit Subtext
- [x] Alle neuen Texte in 4 Sprachen (DE/FR/IT/EN)
- [x] 100% Tests bestanden (iteration_27)

### Truck Galerie & Video Infrastruktur (03.04.2026)
- [x] Backend: Gallery Upload Endpoint (POST /api/admin/trucks/{slug}/gallery) mit Object Storage
- [x] Backend: Gallery Delete Endpoint (DELETE /api/admin/trucks/{slug}/gallery)
- [x] Backend: video_url Feld pro Truck
- [x] Admin UI: GalleryManager Komponente (Bild hochladen + URL einfügen + Vorschau + Löschen)
- [x] Admin UI: Video-URL Feld mit Embed-Hinweis
- [x] Frontend: HeroGallery Slider mit Pfeilen, Dots, Thumbnails, Auto-Advance (5s)
- [x] Frontend: Video Play-Button → YouTube/Vimeo Embed im Hero
- [x] Graceful Fallback: Nur Hauptbild wenn keine Galerie vorhanden
- [x] 100% Tests bestanden (iteration_28)

### CRO Sharpening & Conversion-Optimierung (03.04.2026)
- [x] Hero geschärft: "EINZIGARTIGE FOODTRUCKS FÜR EVENTS, DIE IN ERINNERUNG BLEIBEN." (Ergebnis verkaufen, nicht Trucks)
- [x] Positionierung: "Auffällig & Einzigartig – Das Highlight auf jedem Event"
- [x] Pricing-Sektion (NEU): 3 Event-Grössen (Klein/Mittel/Gross), "PREIS AUF ANFRAGE", BELIEBT Badge
- [x] Kundenlogos-Sektion (NEU): "VERTRAUEN VON" mit Platzhalter-Logos (Google, UBS, SBB, Migros, Swiss, Zurich)
- [x] Truck-Taglines ergebnis-fokussiert: z.B. "Für Events mit 200+ Gästen – schnell, heiss, unvergesslich"
- [x] Alle Texte in 4 Sprachen (DE/FR/IT/EN)
- [x] 100% Tests bestanden (iteration_29)

## Remaining Tasks
- [ ] Event-Funnel (Anfrage-Formular) an CRO-Stil anpassen (P1)
- [ ] Google Search Console setup (manueller Schritt durch den Nutzer)
- [ ] Emergent LLM Key Budget auffuellen (Profil -> Universal Key -> Balance hinzufuegen)

## Test Reports
- iteration_3 bis iteration_25: Alle bestanden
- KI-Blog-Generator: Manuell getestet mit GPT-4o (Score 8/10, mit internen Links und Bild)
