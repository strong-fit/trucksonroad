# TruckOnRoad - Premium Foodtruck Website

## Architecture
- **Frontend**: React + Tailwind + Shadcn UI + Leaflet (Maps)
- **Backend**: FastAPI + MongoDB + fpdf2 + httpx + Emergent Object Storage
- **Email**: Gmail SMTP (configurable, 9 templates, 4 languages)
- **Maps**: OpenStreetMap + OSRM (free)
- **Storage**: Emergent Object Storage
- **AI**: Perplexity API sonar-pro (Event Scout, admin configurable)
- **Design**: Public: Dark + Petrol. Admin: Light

## Implemented Features

### Public Site (DONE)
- Homepage, Truck Details, Inquiry Form, FAQ, Veranstalter, Private Events
- Über uns, Kontakt, WhatsApp Button, Customer Login/Registration
- SEO: Meta Tags, JSON-LD, Sitemap, robots.txt

### Public Agenda (DONE)
- `/agenda` showing upcoming confirmed events

### Multi-Language (DONE)
- Full 4-language: DE, FR, IT, EN – Frontend + Backend Emails + PDFs
- Language switcher + localStorage persistence
- Customer's language saved with inquiry, used for all emails/PDFs

### Customer Portal (DONE)
- Registration, dashboard, inquiry tracking, invoices, file uploads

### Admin Area - 12 Sections (DONE)
1. Dashboard  2. Anfragen  3. Kalender  4. Trucks  5. Personal
6. Finanzen  7. Routen  8. Bewertungen  9. Event-Scout
10. FAQ  11. Export  12. Einstellungen

### KI Event-Scout (DONE)
- Perplexity API search + auto-scan + fixed sources + application emails

### Multilingual Email Templates (DONE - April 2026)
- **EMAIL_I18N** dictionary with DE/EN/FR/IT translations for all email content
- 9 email templates fully translated: Confirmation, Admin Notification, Offer, Status Updates (4), Invoice (4), File Upload, Event Reminder
- **Offer PDF** fully translated (labels, disclaimer, filename)
- Language stored per inquiry (`lang` field), used for all communications
- Email preview endpoint supports `?lang=` parameter
- Admin notifications always in German (internal)

### Email Automation - 9 Templates (DONE)
All in 4 languages: Confirmation, Admin Notification, Offer, Booking Confirmed, Completed, Cancelled, Invoice (4 states), File Upload, Event Reminder, Event Scout

## 3rd Party Integrations
- Emergent Object Storage
- Gmail SMTP (admin configurable)
- Perplexity API (event scout, admin configurable)

## Backlog
- [ ] Google Search Console setup (manual step by user)
