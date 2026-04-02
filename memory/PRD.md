# TruckOnRoad - Premium Foodtruck Website

## Architecture
- **Frontend**: React + Tailwind + Shadcn UI + Leaflet (Maps)
- **Backend**: FastAPI + MongoDB + fpdf2 + httpx + Emergent Object Storage
- **Email**: Gmail SMTP (configurable, 8 templates)
- **Maps**: OpenStreetMap + OSRM (free, no API key)
- **Storage**: Emergent Object Storage (file uploads)
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

### Multi-Language Support (DONE - April 2026)
- Full 4-language support: DE, FR, IT, EN
- Language switcher dropdown in Navbar (desktop + mobile)
- localStorage persistence (truckonroad_lang key)
- All public pages translated via t() function
- Customer Portal (Login, Register, Dashboard) fully translated
- Admin area (sidebar, dashboard, inquiries, all page titles) fully translated
- Translation dictionary: ~500+ keys across 4 languages

### Customer Portal (DONE)
- Open registration, personal dashboard, inquiry tracking + status
- Invoice visibility, file downloads, two-way sync with Admin

### Admin Area - 11 Sections (DONE)
1. Dashboard (stats + recent inquiries)
2. Anfragen (filters, detail, status, notes, employees, offer PDF, invoice, file upload/download)
3. Kalender (truck selector, date blocking)
4. Trucks (edit name, desc, image, menu, capacity)
5. Personal (employee CRUD + assignment)
6. Finanzen (revenue, costs, profit)
7. Routen (Leaflet map, geocoding, OSRM)
8. Bewertungen (CRUD, auto-sync to homepage + JSON-LD)
9. FAQ (CRUD DE/EN)
10. Export (CSV/PDF)
11. Einstellungen (company, SMTP, Instagram, Social Media/SEO, Google Verification, auto-confirmation, event reminder days, 8 email templates preview)

### Email Automation - 8 Templates (DONE)
1. Bestätigungsmail (Anfrage erhalten)
2. Admin-Benachrichtigung (neue Anfrage)
3. Status: Buchung bestätigt
4. Status: Event abgeschlossen
5. Rechnung gesendet
6. Zahlung eingegangen
7. Datei-Upload Benachrichtigung
8. Event-Erinnerung (X Tage vor Event, konfigurierbar)

### SEO & KI-Suchmaschinen (DONE)
- 13+ Meta Tags (og:url, og:image, hreflang, twitter:image, etc.)
- 2 JSON-LD Schemas (FoodEstablishment + FAQPage)
- robots.txt erlaubt GPTBot, ClaudeBot, PerplexityBot, Google-Extended
- Google Search Console Verification (Admin-konfigurierbar)
- Sitemap.xml (13 URLs)

## Backlog
- [ ] Backend email templates/PDFs in selected language (P1)
- [ ] Google Search Console setup (manual step by user)
