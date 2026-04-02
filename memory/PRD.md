# TruckOnRoad - Premium Foodtruck Website

## Architecture
- **Frontend**: React + Tailwind + Shadcn UI + Leaflet (Maps)
- **Backend**: FastAPI + MongoDB + fpdf2 + httpx + Emergent Object Storage
- **Email**: Gmail SMTP (configurable, 8+ templates)
- **Maps**: OpenStreetMap + OSRM (free, no API key)
- **Storage**: Emergent Object Storage (file uploads)
- **AI**: Perplexity API sonar-pro (Event Scout, configurable in Admin)
- **Design**: Public: Dark + Petrol. Admin: Light

## Implemented Features

### Public Site (DONE)
- Homepage, 6 Truck Detail Pages, Inquiry Form, FAQ, Veranstalter, Private Events
- Über uns, Kontakt, WhatsApp Button, Customer Login/Registration
- Full SEO: Meta Tags, og:image, hreflang, Sitemap.xml, robots.txt (AI-friendly)
- JSON-LD: FoodEstablishment + FAQPage + aggregateRating

### Public Agenda (DONE - April 2026)
- `/agenda` page showing upcoming confirmed events (Date, Location, Event Name, Trucks)
- Navbar link, responsive layout, localized date formatting

### Multi-Language Support (DONE - April 2026)
- Full 4-language: DE, FR, IT, EN with Navbar dropdown + localStorage persistence

### Customer Portal (DONE)
- Registration, dashboard, inquiry tracking, invoice visibility, file uploads

### Admin Area - 12 Sections (DONE)
1. Dashboard  2. Anfragen  3. Kalender  4. Trucks  5. Personal
6. Finanzen  7. Routen  8. Bewertungen
9. **Event-Scout** (Perplexity AI - search, auto-scan, fixed sources, application emails)
10. FAQ  11. Export  12. Einstellungen

### KI Event-Scout (DONE - April 2026)
- **Manuelle Suche**: Perplexity sonar-pro durchsucht Web nach Schweizer Events
- **Automatischer Täglicher Scan**: Cronjob (24h) mit konfigurierbaren Suchbegriffen
- **Fixe Event-Webseiten**: Admin kann bekannte URLs hinterlegen (z.B. eventkalender.ch)
- **Suchbegriffe als Tags**: Festival, Weihnachtsmarkt, Strassenfest etc.
- **Status-Tracking**: Neu → Angefragt → Bestätigt → Abgelehnt
- **Bewerbungs-E-Mail**: Professionelle E-Mail mit Firmenkonzept direkt an Veranstalter
- **Admin E-Mail-Benachrichtigung**: Bei neuen Event-Funden
- **Duplikaterkennung**: Gleiche Events werden nicht doppelt gespeichert
- **NUR Schweizer Events** (systemweit erzwungen)
- API-Key konfigurierbar in Admin → Einstellungen

### Email Automation - 9 Templates (DONE)
1-8: Standard (Bestätigung, Admin, Buchung, Abschluss, Rechnung, Zahlung, Upload, Erinnerung)
9. Event-Scout Benachrichtigung (neue Events gefunden)

## Key API Endpoints
- `GET /api/agenda` - Public upcoming events
- `POST /api/admin/event-scout/search` - AI event search
- `GET/PUT /api/admin/event-scout/sources` - Config (URLs, keywords, auto-scan)
- `POST /api/admin/event-scout/scan-now` - Manual scan trigger
- `GET/POST/PUT/DELETE /api/admin/event-scout/events` - Scouted event CRUD
- `POST /api/admin/event-scout/events/{id}/apply` - Send application email

## DB Schema
- `scouted_events`: {id, name, date, location, type, description, organizer_email, website, status, notes, source, created_at}
- `settings.scout_sources`: [URLs], `settings.scout_keywords`: [strings], `settings.scout_auto_scan`: bool

## 3rd Party Integrations
- Emergent Object Storage (file uploads)
- Gmail SMTP (admin configurable)
- **Perplexity API** sonar-pro (event scout, admin configurable - user needs own key from perplexity.ai/settings/api)

## Backlog
- [ ] Backend email templates/PDFs in selected language (P1)
- [ ] Google Search Console setup (manual step by user)
