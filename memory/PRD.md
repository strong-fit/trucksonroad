# TruckOnRoad - Premium Foodtruck Website

## Architecture
- **Frontend**: React + Tailwind + Shadcn UI + Leaflet (Maps)
- **Backend**: FastAPI + MongoDB + fpdf2 + httpx + Emergent Object Storage
- **Email**: Gmail SMTP (configurable)
- **Maps**: OpenStreetMap + OSRM (free, no API key)
- **Storage**: Emergent Object Storage (file uploads)
- **Design**: Public: Dark + Petrol. Admin: Light

## Implemented Features

### Public Site (DONE)
- Homepage (Hero, Ticker, Trucks, CTA, Testimonials, FAQ, Instagram Gallery)
- 6 Truck Detail Pages, Inquiry Form with File Upload, FAQ, Veranstalter, Private Events
- Über uns, Kontakt (with real company info)
- SEO Meta Tags, Sitemap.xml, PDF Download, JSON-LD Structured Data with aggregateRating
- DE/EN Navigation, WhatsApp Button
- Customer Login/Registration pages

### Customer Portal (DONE)
- Open registration for event customers
- Personal dashboard with inquiry tracking + status
- Invoice visibility (Offen, Gesendet, Bezahlt, Überfällig)
- File downloads (attached documents per inquiry)
- Two-way sync with Admin

### Admin Area - 11 Sections (DONE)
1. Dashboard (stats + recent inquiries)
2. Anfragen (filters, detail, status, notes, employees, offer PDF, invoice, **file upload/download**)
3. Kalender (truck selector, date blocking)
4. Trucks (edit name, desc, image, menu, capacity)
5. Personal (employee CRUD + assignment to events)
6. Finanzen (revenue, costs, profit per event/truck/month)
7. Routen (Leaflet map, geocoding, OSRM routing/optimization)
8. Bewertungen (CRUD, star ratings, auto-sync to homepage + JSON-LD)
9. FAQ (CRUD DE/EN)
10. Export (CSV/PDF for all data)
11. Einstellungen (company, SMTP, Instagram, Social Media/SEO, auto-confirmation, 6 email templates)

### Email Automation (DONE)
- 6 templates: Confirmation, Admin Notification, Status Updates (confirmed/completed/cancelled), Invoice Updates (sent/paid/overdue)
- Configurable auto-confirmation toggle

### File Upload (DONE)
- Drag & drop upload on inquiry success screen
- Max 5 files per inquiry, 10MB each, all file types
- Files visible in Admin inquiry detail (upload/download/delete)
- Files visible in Customer Portal (download only)
- Emergent Object Storage backend

## Recently Added (2026-04-01)
- [x] JSON-LD Structured Data with aggregateRating
- [x] Social Media & SEO Admin Settings
- [x] Reviews/Bewertungen System
- [x] Customer Registration & Login
- [x] Customer Portal with inquiry tracking & invoice visibility
- [x] Admin Auto-Confirmation Toggle
- [x] Admin Invoice Management
- [x] Email notifications on status changes (6 templates)
- [x] File Upload for inquiries (Emergent Object Storage)

## Backlog
- [ ] FR/IT Übersetzungen
