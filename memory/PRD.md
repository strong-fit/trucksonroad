# TruckOnRoad - Premium Foodtruck Website

## Original Problem Statement
Premium Foodtruck Webseite für Schweizer Foodtruck-Unternehmen mit starker Startseite, Truck-Seiten, Anfrageformular, Admin-Dashboard, E-Mail-Automatisierung, und mehr.

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI + Custom CSS
- **Backend**: FastAPI + MongoDB (Motor async)
- **Auth**: JWT with httpOnly cookies, bcrypt
- **Email**: Gmail SMTP via Python smtplib (configurable in Admin)
- **PDF**: fpdf2 library
- **Design**: Public: Dark (#0a0a0a bg, Petrol #4db6ac accents). Admin: Light (#f4f3ef bg)
- **Fonts**: Bebas Neue, Playfair Display, DM Sans

## What's Been Implemented

### Public Site (DONE)
- [x] Homepage (Hero "FOODTRUCKS FÜR JEDEN ANLASS", Ticker, Trucks Grid, CTA, FAQ)
- [x] 6 Truck Detail Pages
- [x] Inquiry Form (calendar, truck selection, extras)
- [x] FAQ Page
- [x] Event Organizers Page + PDF Download Link
- [x] Private Events Page
- [x] Über uns Page (story, values, numbers)
- [x] Kontakt Page (address, form)
- [x] Navigation (DE/EN, Über uns, Kontakt)
- [x] WhatsApp Button, Footer with real contact info
- [x] SEO Meta Tags (OG, Twitter, canonical)
- [x] Sitemap.xml endpoint

### Admin Area (DONE)
- [x] Login (light theme)
- [x] Dashboard (stats + recent inquiries)
- [x] Inquiry Management (filters, detail panel, status, notes)
- [x] Calendar (truck selector, blocking)
- [x] Truck Editing (name, description, image, capacity, menu)
- [x] FAQ Management (CRUD with DE/EN)
- [x] Settings (company info, SMTP config, test email)
- [x] Email Preview (confirmation + notification templates)
- [x] PDF Download for Veranstalter

### Backend (DONE)
- [x] JWT auth + brute-force protection
- [x] Trucks, Inquiries, FAQs, Calendar CRUD
- [x] Gmail SMTP email (background tasks)
- [x] Sitemap.xml, PDF generation, Email preview
- [x] Admin stats, settings, contact-info endpoints

## Prioritized Backlog

### P2 (Nice to Have)
- [ ] Offerten-PDF automatisch erstellen
- [ ] Personalplanung pro Event
- [ ] Umsatz-Tracking
- [ ] Instagram-Feed Integration
- [ ] Französisch/Italienisch
- [ ] Image Upload im Anfrageformular
- [ ] Admin: Export (CSV/PDF)
