# TruckOnRoad - Premium Foodtruck Website

## Original Problem Statement
Premium Foodtruck Webseite für Schweizer Foodtruck-Unternehmen mit:
- Starke Startseite mit Hero, Truck-Übersicht, CTA
- Eigene Seiten für 6 Trucks (Burger, Chicken Burger, Bowl, Pocket Bowl, Empanadas, Retro Trailer)
- Für Veranstalter Seite
- Private & Firmenanlässe Seite
- Über uns & Kontakt Seiten
- Umfassendes Anfrageformular mit Kalenderverfügbarkeit
- Admin-Bereich mit Anfrageverwaltung, Kalender, Truck-Management, Einstellungen
- E-Mail-Benachrichtigungen (Gmail SMTP)
- Mehrsprachigkeit (DE/EN)
- WhatsApp-Button

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI + Custom CSS
- **Backend**: FastAPI + MongoDB (Motor async)
- **Auth**: JWT with httpOnly cookies, bcrypt password hashing
- **Email**: Gmail SMTP via Python smtplib (configurable in Admin)
- **Design**: Public site: Dark premium theme (#0a0a0a bg, Petrol #4db6ac accents). Admin: Light theme (#f4f3ef bg, #3d9189 accents)
- **Fonts**: Bebas Neue (headings), Playfair Display (italic accents), DM Sans (body)

## What's Been Implemented

### Frontend - Public Site (DONE)
- [x] Homepage with Hero "FOODTRUCKS FÜR JEDEN ANLASS", Ticker, Trucks Grid, For-Whom, Why-Us, CTA, FAQ Preview
- [x] 6 Individual Truck Detail Pages with menu, specs, CTA
- [x] Full Inquiry Form with calendar, truck selection, extras
- [x] FAQ Page with expandable accordion
- [x] Event Organizers Page with features grid and tech specs
- [x] Private Events Page with event types and 3-step process
- [x] Über uns Page with story, values, numbers (01.04.2026)
- [x] Kontakt Page with company info + contact form (01.04.2026)
- [x] Navigation with language toggle (DE/EN), Über uns, Kontakt links
- [x] WhatsApp floating button (+41 79 696 98 99)
- [x] Footer with correct address (Bahnhofstrasse 75, 8620 Wetzikon)
- [x] Responsive design
- [x] Accent color: Petrol (#4db6ac)

### Frontend - Admin Area (DONE)
- [x] Admin Login (light theme, TruckOnRoad branding)
- [x] Admin Dashboard with stat cards + recent inquiries table
- [x] Admin Inquiry Management with filter pills, detail panel, status changes, notes
- [x] Admin Calendar with truck selector, date blocking, block list
- [x] Admin Settings with Firmendaten + SMTP config + Test-E-Mail (01.04.2026)
- [x] Shared AdminLayout with sidebar (Dashboard, Anfragen, Kalender, Einstellungen), topbar

### Backend (DONE)
- [x] JWT auth with brute-force protection
- [x] Trucks CRUD + seed data (6 trucks with Unsplash images)
- [x] Inquiries CRUD (public POST + admin management)
- [x] Calendar availability (public GET + admin block/unblock)
- [x] FAQ CRUD + seed data (8 FAQs)
- [x] Admin statistics endpoint
- [x] Admin Settings endpoint (company info + SMTP config)
- [x] Public contact-info endpoint
- [x] Gmail SMTP email sending (background tasks) (01.04.2026)
- [x] Confirmation email to customer on inquiry (01.04.2026)
- [x] Notification email to admin on inquiry (01.04.2026)
- [x] Test-email endpoint (01.04.2026)

## Prioritized Backlog

### P1 (High Priority)
- [ ] SEO-Optimierung (Meta Tags, Sitemap, OG Images)
- [ ] PDF-Download für Veranstalter (Konzept-PDF)
- [ ] Admin: Truck-Bearbeitung (Bilder, Texte ändern)
- [ ] Admin: FAQ-Verwaltung (Hinzufügen, Bearbeiten, Löschen)

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
