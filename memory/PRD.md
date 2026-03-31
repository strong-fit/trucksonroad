# StrongFood - Premium Foodtruck Website

## Original Problem Statement
Premium Foodtruck Webseite für Schweizer Foodtruck-Unternehmen mit:
- Starke Startseite mit Hero, Truck-Übersicht, CTA
- Eigene Seiten für 6 Trucks (Burger, Chicken Burger, Bowl, Pocket Bowl, Empanadas, Retro Trailer)
- Für Veranstalter Seite
- Private & Firmenanlässe Seite
- Umfassendes Anfrageformular mit Kalenderverfügbarkeit
- Admin-Bereich mit Anfrageverwaltung, Kalender, Truck-Management
- Mehrsprachigkeit (DE/EN)
- WhatsApp-Button
- Automatische E-Mails (für spätere Phase)

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI + Custom Dark Theme CSS
- **Backend**: FastAPI + MongoDB (Motor async)
- **Auth**: JWT with httpOnly cookies, bcrypt password hashing
- **Design**: Dark premium theme (#0a0a0a bg, #e8b84b gold accents)
- **Fonts**: Bebas Neue (headings), Playfair Display (italic accents), DM Sans (body)

## User Personas
1. **Festival-Veranstalter** - Sucht zuverlässige Trucks für Grossevents
2. **Privatkunde** - Will Foodtruck für Geburtstag/Hochzeit buchen
3. **Firmen** - Teambuilding, Firmenfeier, Kundenevent
4. **Admin** - Verwaltet Anfragen, Kalender, Trucks

## Core Requirements (Static)
- Premium Dark Design matching reference HTML
- 6 Truck-Konzepte mit eigenem Profil
- Umfassendes Anfrageformular (kein automatisches Buchen)
- Kalender-Verfügbarkeit pro Truck
- Admin-Dashboard mit Statistiken
- Anfrage-Management (Status: Neu → In Prüfung → Offerte → Bestätigt/Abgesagt)
- Mehrsprachig DE/EN

## What's Been Implemented

### Frontend (DONE)
- [x] Homepage with Hero (2 floating truck images), Ticker, Trucks Grid, For-Whom, Why-Us (gold bg), CTA, FAQ Preview
- [x] CSS/DOM structure aligned with user's HTML reference (sf-trucks-wrap, sf-why-section, sf-hero-truck-main/accent, sf-nav-cta)
- [x] 6 Individual Truck Detail Pages with menu, specs, CTA
- [x] Full Inquiry Form with calendar, truck selection, extras
- [x] FAQ Page with expandable accordion
- [x] Event Organizers Page with features grid and tech specs
- [x] Private Events Page with event types and 3-step process
- [x] Admin Login with JWT auth
- [x] Admin Dashboard with stats and recent inquiries
- [x] Admin Inquiry Management with filtering, detail view, status updates, notes
- [x] Admin Calendar with per-truck blocking
- [x] Navigation with language toggle (DE/EN) and sf-nav-cta gold button
- [x] WhatsApp floating button
- [x] Footer with 4-column direct grid (Brand, Trucks, Events, Kontakt) + footer-bottom
- [x] Responsive design

### Backend (DONE)
- [x] JWT auth with brute-force protection
- [x] Trucks CRUD + seed data (6 trucks)
- [x] Inquiries CRUD (public POST + admin management)
- [x] Calendar availability (public GET + admin block/unblock)
- [x] FAQ CRUD + seed data (8 FAQs)
- [x] Admin statistics endpoint
- [x] Settings endpoint
- [x] Admin user seed on startup

## Prioritized Backlog

### P0 (Critical - Next Sprint)
- [ ] Email-Automatisierung (Gmail SMTP) - Bestätigungsmail bei Anfrage
- [ ] Über uns Seite
- [ ] Kontakt Seite

### P1 (High Priority)
- [ ] SEO-Optimierung (Meta Tags, Sitemap)
- [ ] PDF-Download für Veranstalter (Konzept-PDF)
- [ ] Admin: Truck-Bearbeitung (Bilder, Texte ändern)
- [ ] Admin: FAQ-Verwaltung (Hinzufügen, Bearbeiten, Löschen)
- [ ] Admin: Einstellungen (E-Mail, WhatsApp-Nummer, Firmenname)

### P2 (Nice to Have)
- [ ] Offerten automatisch erstellen (PDF)
- [ ] Personalplanung pro Event
- [ ] Routenplanung
- [ ] Umsatz-Tracking pro Anlass
- [ ] Instagram-Feed Integration
- [ ] Französisch/Italienisch Übersetzung
- [ ] Schnellanfrage-Widget auf Homepage
- [ ] Image Upload in Anfrageformular (Lageplan)
- [ ] Admin: Export-Funktion (CSV/PDF)

## Next Tasks
1. E-Mail-Benachrichtigungen implementieren (Gmail SMTP konfigurierbar im Admin)
2. SEO-Tags und Sitemap
3. Admin FAQ-Verwaltung UI
4. Über uns & Kontakt Seiten
5. PDF-Download für Veranstalter
