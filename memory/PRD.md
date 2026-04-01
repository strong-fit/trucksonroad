# TruckOnRoad - Premium Foodtruck Website

## Original Problem Statement
Premium Foodtruck Webseite für Schweizer Foodtruck-Unternehmen.

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Shadcn UI + Custom CSS
- **Backend**: FastAPI + MongoDB (Motor async)
- **Auth**: JWT with httpOnly cookies, bcrypt
- **Email**: Gmail SMTP via Python smtplib (configurable in Admin)
- **PDF**: fpdf2 library (Veranstalter-PDF + Offerten-PDF)
- **Design**: Public: Dark (#0a0a0a bg, Petrol #4db6ac). Admin: Light (#f4f3ef bg)

## What's Been Implemented

### Public Site (DONE)
- [x] Homepage (Hero, Ticker, Trucks Grid, CTA, FAQ Preview, Instagram Gallery)
- [x] 6 Truck Detail Pages
- [x] Inquiry Form (calendar, truck selection, extras)
- [x] FAQ, Veranstalter, Private Events, Über uns, Kontakt Seiten
- [x] Navigation (DE/EN), WhatsApp, Footer
- [x] SEO Meta Tags + Sitemap.xml
- [x] PDF Download für Veranstalter
- [x] Instagram Gallery (admin-konfigurierbar)

### Admin Area (DONE)
- [x] Login, Dashboard, Anfragen (mit Personal-Zuweisung + Offerten-PDF)
- [x] Kalender, Trucks (Bearbeitung), FAQ (CRUD)
- [x] Personal (Mitarbeiter-CRUD + Zuweisung zu Events)
- [x] Export (CSV/PDF für Anfragen, Mitarbeiter, Kalender, Trucks, FAQs)
- [x] Einstellungen (Firma, SMTP, Instagram Feed, E-Mail-Vorschau)
- [x] Offerten-PDF (auto bei Status "Offerte gesendet" + manuell)

### Backend (DONE)
- [x] JWT Auth, Trucks/Inquiries/FAQs/Calendar CRUD
- [x] Employees CRUD + Assignment
- [x] Offer PDF Generation + Email
- [x] Export (CSV/PDF all data types)
- [x] Sitemap, Instagram Gallery, Contact Info, Settings
- [x] Gmail SMTP (background tasks)

## Backlog
- [ ] FR/IT Übersetzungen (nach Fertigstellung)
- [ ] Umsatz-Tracking pro Anlass
- [ ] Routenplanung
