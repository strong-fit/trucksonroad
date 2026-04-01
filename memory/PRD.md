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

### Admin Area - 11 Sections (DONE)
1. Dashboard (stats + recent inquiries)
2. Anfragen (filters, detail, status, notes, employee assignment, offer PDF)
3. Kalender (truck selector, date blocking)
4. Trucks (edit name, desc, image, menu, capacity)
5. Personal (employee CRUD + assignment to events)
6. Finanzen (revenue, costs, profit per event/truck/month)
7. Routen (Leaflet map, geocoding, OSRM routing/optimization)
8. Bewertungen (CRUD, star ratings, event type, toggle visibility, auto-sync to homepage + JSON-LD)
9. FAQ (CRUD DE/EN)
10. Export (CSV/PDF for all data)
11. Einstellungen (company, SMTP, Instagram gallery, Social Media/SEO links, email preview)

### Backend APIs (DONE)
- Auth, Trucks, Inquiries, FAQs, Calendar, Employees CRUD
- Finance tracking, Offer PDF, Export (CSV/PDF)
- Geocoding (Nominatim), Routing (OSRM), Route optimization
- Sitemap, Instagram gallery, Contact info, Settings
- Gmail SMTP email (confirmation + admin notification + offer)
- Reviews CRUD, Public reviews, SEO Structured Data with aggregateRating

## Recently Added (2026-04-01)
- [x] JSON-LD Structured Data (Schema.org FoodEstablishment) for AI Search Engines
- [x] Social Media & SEO Admin Settings (Google Business, Instagram, Facebook, TikTok, LinkedIn)
- [x] Dynamic JSON-LD API endpoint `/api/seo/structured-data` with aggregateRating
- [x] Reviews/Bewertungen System: Admin CRUD, Homepage Testimonials, JSON-LD aggregateRating

## Backlog
- [ ] FR/IT Übersetzungen
