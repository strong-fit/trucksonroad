# TruckOnRoad - Premium Foodtruck Website

## Architecture
- **Frontend**: React + Tailwind + Shadcn UI + Leaflet (Maps)
- **Backend**: FastAPI + MongoDB + fpdf2 + httpx
- **Email**: Gmail SMTP (configurable)
- **Maps**: OpenStreetMap + OSRM (free, no API key)
- **Design**: Public: Dark + Petrol. Admin: Light

## Implemented Features

### Public Site (DONE)
- Homepage (Hero, Ticker, Trucks, CTA, Testimonials, FAQ, Instagram Gallery)
- 6 Truck Detail Pages, Inquiry Form, FAQ, Veranstalter, Private Events
- Über uns, Kontakt (with real company info)
- SEO Meta Tags, Sitemap.xml, PDF Download, JSON-LD Structured Data with aggregateRating
- DE/EN Navigation, WhatsApp Button
- Customer Login/Registration pages

### Customer Portal (DONE)
- Open registration for event customers
- Personal dashboard with inquiry tracking + status
- Invoice visibility (Offen, Gesendet, Bezahlt, Überfällig)
- Two-way sync with Admin
- Post-inquiry CTA to create account

### Admin Area - 11 Sections (DONE)
1. Dashboard (stats + recent inquiries)
2. Anfragen (filters, detail, status, notes, employee assignment, offer PDF, invoice management)
3. Kalender (truck selector, date blocking)
4. Trucks (edit name, desc, image, menu, capacity)
5. Personal (employee CRUD + assignment to events)
6. Finanzen (revenue, costs, profit per event/truck/month)
7. Routen (Leaflet map, geocoding, OSRM routing/optimization)
8. Bewertungen (CRUD, star ratings, event type, auto-sync to homepage + JSON-LD)
9. FAQ (CRUD DE/EN)
10. Export (CSV/PDF for all data)
11. Einstellungen (company, SMTP, Instagram, Social Media/SEO, auto-confirmation, email preview with 6 templates)

### Email Automation (DONE)
- Confirmation email on inquiry submission
- Admin notification on new inquiry
- Offer email when status → offer_sent
- Status notification: in_review, confirmed, completed, cancelled
- Invoice notification: pending, sent, paid, overdue
- All 6 templates previewable in Admin Settings
- Configurable auto-confirmation toggle (manual vs automatic)

### Backend APIs (DONE)
- Auth (admin + customer registration + login + JWT cookies)
- Customer Portal (profile, own inquiries)
- Trucks, Inquiries, FAQs, Calendar, Employees CRUD
- Invoice management (status + amount per inquiry + email notification)
- Finance tracking, Offer PDF, Export (CSV/PDF)
- Geocoding, Routing, Route optimization
- Reviews CRUD, SEO Structured Data, Sitemap

## Recently Added (2026-04-01)
- [x] JSON-LD Structured Data with aggregateRating
- [x] Social Media & SEO Admin Settings
- [x] Reviews/Bewertungen System
- [x] Customer Registration & Login
- [x] Customer Portal with inquiry tracking & invoice visibility
- [x] Admin Auto-Confirmation Toggle
- [x] Admin Invoice Management
- [x] Email notifications on status changes (6 templates)
- [x] Email preview in Admin Settings (6 template tabs)

## Backlog
- [ ] FR/IT Übersetzungen
