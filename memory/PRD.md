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
- Open registration for event customers (email, name, company, phone)
- Personal dashboard showing all own inquiries with status tracking
- Invoice visibility (Offen, Gesendet, Bezahlt, Überfällig)
- Two-way sync: changes in admin instantly visible in customer portal
- Link to create new inquiry from portal
- Post-inquiry CTA to create account

### Admin Area - 11 Sections (DONE)
1. Dashboard (stats + recent inquiries)
2. Anfragen (filters, detail, status, notes, employee assignment, offer PDF, **invoice management**)
3. Kalender (truck selector, date blocking)
4. Trucks (edit name, desc, image, menu, capacity)
5. Personal (employee CRUD + assignment to events)
6. Finanzen (revenue, costs, profit per event/truck/month)
7. Routen (Leaflet map, geocoding, OSRM routing/optimization)
8. Bewertungen (CRUD, star ratings, event type, toggle visibility, auto-sync to homepage + JSON-LD)
9. FAQ (CRUD DE/EN)
10. Export (CSV/PDF for all data)
11. Einstellungen (company, SMTP, Instagram, Social Media/SEO, **auto-confirmation toggle**)

### Backend APIs (DONE)
- Auth (admin + customer registration + login + JWT cookies)
- Customer Portal (profile, own inquiries)
- Trucks, Inquiries, FAQs, Calendar, Employees CRUD
- Invoice management (status + amount per inquiry)
- Finance tracking, Offer PDF, Export (CSV/PDF)
- Geocoding (Nominatim), Routing (OSRM), Route optimization
- Sitemap, Instagram gallery, Contact info, Settings
- Gmail SMTP email (confirmation + admin notification + offer)
- Reviews CRUD, Public reviews, SEO Structured Data with aggregateRating

## Recently Added (2026-04-01)
- [x] JSON-LD Structured Data with aggregateRating
- [x] Social Media & SEO Admin Settings
- [x] Reviews/Bewertungen System
- [x] Customer Registration & Login (open for all event customers)
- [x] Customer Portal with inquiry tracking & invoice visibility
- [x] Admin Auto-Confirmation Toggle (manual vs automatic booking confirmation)
- [x] Admin Invoice Management (status + amount per inquiry)
- [x] Two-way sync between Admin and Customer Portal
- [x] Navbar "Anmelden" link for non-logged-in users

## Backlog
- [ ] FR/IT Übersetzungen
