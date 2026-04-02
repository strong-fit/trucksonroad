# TruckOnRoad - Premium Foodtruck Website

## Architecture
- **Frontend**: React + Tailwind + Shadcn UI + Leaflet (Maps)
- **Backend**: FastAPI + MongoDB + fpdf2 + httpx + Emergent Object Storage
- **Email**: Gmail SMTP (configurable, 8 templates)
- **Maps**: OpenStreetMap + OSRM (free, no API key)
- **Storage**: Emergent Object Storage (file uploads)
- **AI**: Perplexity API (Event Scout, configurable in Admin)
- **Design**: Public: Dark + Petrol. Admin: Light

## Implemented Features

### Public Site (DONE)
- Homepage (Hero, Ticker, Trucks, CTA, Testimonials, FAQ, Instagram Gallery)
- 6 Truck Detail Pages, Inquiry Form with File Upload, FAQ, Veranstalter, Private Events
- Über uns, Kontakt (with real company info)
- Full SEO: Meta Tags, og:image, og:url, hreflang (de/en), Sitemap.xml, robots.txt (AI-friendly)
- JSON-LD: FoodEstablishment (aggregateRating) + FAQPage
- Google Search Console verification (configurable in Admin)
- WhatsApp Button, Customer Login/Registration

### Public Agenda (DONE - April 2026)
- `/agenda` page showing upcoming confirmed events
- Displays: Date (localized), Location, Event Name, Trucks
- Data from confirmed inquiries with future dates
- Link in Navbar, responsive layout

### Multi-Language Support (DONE - April 2026)
- Full 4-language support: DE, FR, IT, EN
- Language switcher dropdown in Navbar (desktop + mobile)
- localStorage persistence (truckonroad_lang key)
- All public, customer, and admin pages translated

### Customer Portal (DONE)
- Open registration, personal dashboard, inquiry tracking + status
- Invoice visibility, file downloads, two-way sync with Admin

### Admin Area - 12 Sections (DONE)
1. Dashboard (stats + recent inquiries)
2. Anfragen (filters, detail, status, notes, employees, offer PDF, invoice, file upload/download)
3. Kalender (truck selector, date blocking)
4. Trucks (edit name, desc, image, menu, capacity)
5. Personal (employee CRUD + assignment)
6. Finanzen (revenue, costs, profit)
7. Routen (Leaflet map, geocoding, OSRM)
8. Bewertungen (CRUD, auto-sync to homepage + JSON-LD)
9. **Event-Scout** (NEW - Perplexity AI web search for events, status tracking, email application)
10. FAQ (CRUD DE/EN)
11. Export (CSV/PDF)
12. Einstellungen (company, SMTP, Instagram, Social Media/SEO, Google Verification, Perplexity API Key, auto-confirmation, event reminder days, 8 email templates)

### KI Event-Scout (DONE - April 2026)
- Perplexity API integration (sonar-pro model)
- Search for festivals, Christmas markets, street fests, corporate events in Switzerland
- Region filter (whole Switzerland or specific cantons/cities)
- Save found events with status tracking (Neu → Angefragt → Bestätigt → Abgelehnt)
- Send professional application emails to organizers with company branding
- API key configurable in Admin Settings

### Email Automation - 8 Templates (DONE)
1-8: Confirmation, Admin notification, Booking confirmed, Completed, Invoice sent, Payment received, File upload, Event reminder

### SEO & KI-Suchmaschinen (DONE)
- 13+ Meta Tags, 2 JSON-LD Schemas, robots.txt (AI-friendly), GSC verification, Sitemap.xml

## Key API Endpoints
- `GET /api/agenda` - Public upcoming events
- `POST /api/admin/event-scout/search` - AI event search (Perplexity)
- `GET/POST/PUT/DELETE /api/admin/event-scout/events` - Scouted event CRUD
- `POST /api/admin/event-scout/events/{id}/apply` - Send application email

## DB Schema (scouted_events)
`{id, name, date, location, type, description, organizer_email, website, status, notes, source, created_at}`

## Backlog
- [ ] Backend email templates/PDFs in selected language (P1)
- [ ] Google Search Console setup (manual step by user)

## 3rd Party Integrations
- Emergent Object Storage (file uploads)
- Gmail SMTP (admin configurable)
- Perplexity API (event scout, admin configurable)
