# TrucksOnRoad - Premium Foodtruck Website (PRD)

## Problem Statement
Premium, professionelle Website fuer "TRUCKSonROAD" – Foodtruck-Unternehmen fuer Festivals, Firmenanlaesse und Private Events in der Schweiz. Conversion-optimiert mit SSR fuer beste SEO-Performance.

## Tech Stack
- **Frontend:** Next.js 16 (App Router, Production Build), React 19, Tailwind CSS
- **Backend:** FastAPI, Motor (async MongoDB), JWT Auth
- **Database:** MongoDB
- **3rd Party:** Emergent Object Storage, Perplexity API (Event Scout), LiteLLM, Gmail SMTP, Leaflet/OpenStreetMap

## Architecture
```
/app/backend/
  server.py, database.py, auth.py, models.py, seed.py
  services/ (email.py, pdf.py, storage.py, event_scout.py)
  routes/ (admin.py, auth_routes.py, customer.py, public.py)
/app/frontend/
  next.config.js, package.json
  src/app/ (Next.js App Router: 34 routes incl. /trucks)
  src/views/ (React components with "use client")
  src/components/ (Navbar, Footer, Providers, PublicShell, UI)
  src/contexts/ (AuthContext, LanguageContext)
  src/lib/ (api.js, translations.js)
```

## Completed Features

### Public Website
- [x] Homepage mit CRO-optimiertem Layout: Hero -> Use Cases -> So funktioniert's -> Pricing -> Trust -> Logos -> Reviews -> Trucks -> Quick Inquiry Widget -> CTA -> FAQ -> Blog -> Instagram
- [x] **Schnellanfrage-Widget** ("Rueckruf anfordern") auf Homepage mit Name + Telefon/E-Mail (NEU 08.04.2026)
- [x] Dedicated Truck-Seiten + Trucks-Uebersichtsseite (/trucks)
- [x] Anfrage-Formular mit Fortschrittsbalken und Inline-Validierung
- [x] Ueber uns, Kontakt, FAQ, Blog, Agenda, Veranstalter Seiten
- [x] WhatsApp Button
- [x] **5-Sprachen-Support komplett: DE, EN, FR, IT, ES** (ES NEU 08.04.2026)

### Offerte-Bestaetigungsseite
- [x] 2-Schritt-Flow: Event-Details anzeigen -> Zahlungsart waehlen -> Bestaetigen
- [x] Zahlungsart: Rechnung (30 Tage) oder Barzahlung (vor Ort)

### Admin Dashboard
- [x] Anfragen-Management mit Offerte-senden-Dialog (Betrag + Event-Vorschau)
- [x] Kalender, Truck-Bearbeitung, FAQ-Verwaltung, Mitarbeiter, Bewertungen
- [x] Finanzen, Routen (Leaflet), Export, KI Event-Scout, Blog mit Auto-Generator

### Kundenportal
- [x] Login/Registrierung, Anfragen, Datei-Upload, Profil

### SEO & SSR
- [x] Server-Side Rendering fuer alle oeffentlichen Seiten
- [x] JSON-LD Structured Data, Meta-Tags, OpenGraph, Sitemap.xml
- [x] **Erweiterte SSR-SEO-Ausgabe**: Canonical Tags + serverseitige JSON-LD-Skripte fuer Layout, /trucks, /faq und Truck-Detailseiten (NEU 08.04.2026)
- [x] **Landingpage-SEO erweitert**: Blog-, ContactPage-, AboutPage-, Service- und Breadcrumb-JSON-LD fuer /blog, /kontakt, /ueber-uns, /fuer-veranstalter und /private-events (NEU 08.04.2026)
- [x] **FAQ-Interaktion verbessert**: FAQ-Toggles als echte Buttons mit data-testid und aria-expanded (NEU 08.04.2026)
- [x] **Sicheres CSS-Aufraeumen**: doppelte Font-Einbindung entfernt, mehrere `transition: all` auf gezielte Properties reduziert (NEU 08.04.2026)

## Remaining Tasks
- [ ] Impressum-Seite mit MWST/UID (wartet auf Nutzerdaten) (P2)
- [x] Google Search Console setup (laut Nutzer bereits erledigt)
- [ ] Emergent LLM Key Budget auffuellen (P3)

## Latest Update - 10.04.2026
- **Homepage Premium Visual Upgrade** (8 Verbesserungen):
  1. Hero-Section: Ghost-Akzentbild entfernt, Hauptbild mit Gradient-Mask, Stats unterhalb der CTA-Buttons als Glassmorphism-Cards
  2. Section-Titel: Groesse reduziert von clamp(3rem,6vw,5.5rem) auf clamp(2.4rem,4.5vw,3.8rem) fuer bessere Balance
  3. Visuelle Abwechslung: CTA mit anthrazit-Hintergrund, Pricing mit Gradient-Background, Section-Divider
  4. So funktioniert's: Groessere Nummern (3.5rem), Hintergrund-Nummer-Effekt, verbindende Linie zwischen Steps
  5. Pricing: Featured-Card mit Glow/Shadow-Effekt, prominenteres BELIEBT-Badge mit Schatten
  6. Micro-Animationen: Cubic-bezier Transitions, Hover-Box-Shadows auf allen Cards, Button-Glow
  7. Kundenlogos: Frosted-Glass-Pill-Styling mit Border und Backdrop-Blur
  8. Trust-Bar: Gradient-Hintergrund, Count-Up-Animation fuer Zahlen (500+, 98%, 24H, 6)
- Frontend-Build aktualisiert und neu gestartet
- Testing-Agent bestaetigt: 100% Erfolgsrate, alle 13 Frontend-Features verifiziert

## Bugfix - 19.04.2026
- **KRITISCH: Weisse Live-Seite behoben** — Alte Create React App `public/index.html` entfernt, die Next.js App Router blockierte
  - Ursache: `public/index.html` (CRA-Relikt) wurde als statische Datei vor dem App Router ausgeliefert — leere Seite ohne React/JS-Bundles
  - Fix: Datei geloescht, Frontend neu gebaut. Alle Routen werden jetzt korrekt vom Next.js App Router bedient
  - `/admin/login` war nicht betroffen, da kein entsprechendes Static File existierte

## Feature - 29.04.2026: Admin Buchung akzeptieren + Bestaetigungsmail
- **Prominenter "Buchung akzeptieren" Button** (gruen, volle Breite) in Anfragen-Detail bei Status Neu/In Prüfung
- **Beim Akzeptieren passiert automatisch:**
  1. Status wird auf "confirmed" gesetzt
  2. Truck-Kalender wird fuer die gebuchten Tage (inkl. mehrtaegig) blockiert
  3. Detaillierte Bestaetigungs-E-Mail an Kunden gesendet (Truck, Catering-Typ, Menü, Gaeste, Datum/Uhrzeit, Standort, Lieferkosten)
- **Backend:** POST /api/admin/inquiries/{id}/accept (setzt Status, erstellt calendar_blocks, sendet E-Mail)
- **E-Mail-Template:** Gebrandetes HTML mit gruener "BESTAETIGT" Badge, alle Buchungsdetails in Tabelle, TrucksOnRoad Footer
- Curl-Test bestaetigt: Status→confirmed, Kalender-Blocks erstellt, E-Mail-Funktion aufgerufen
- **Alter Anfrage-Flow ersetzt** durch 6-Schritte Buchungs-Wizard:
  1. Truck auswaehlen (Grid mit Bildern)
  2. Catering-Art (Eigenes / Unser) + Menü-Kategorie + Gaeste-Anzahl
  3. Standort (Adresse) + automatische Lieferkosten-Berechnung (PLZ → km × CHF/km)
  4. Kalender (Truck-Verfuegbarkeit) + Datum Von-Bis + Uhrzeit Von-Bis
  5. Kundendaten (vorausgefuellt wenn eingeloggt)
  6. Zusammenfassung & Absenden
- **Lieferkosten:** Nominatim OpenStreetMap API (gratis) fuer Geocoding, Haversine-Distanz × Road-Factor × Preis/km
- **Admin:** Menü-Kategorien CRUD unter /admin/menu-kategorien, Lieferpreis/km + Firmen-PLZ in Einstellungen
- **Backend:** /api/truck-availability/{slug}, /api/menu-categories, /api/calculate-delivery, /api/admin/menu-categories CRUD
- Testing-Agent bestaetigt: 100% (15/15 Backend + Frontend alle 6 Wizard-Steps verifiziert)
- **Neuer Auth-Flow ohne Passwort** — Kunden melden sich per E-Mail + 6-stelligem Bestaetigungscode an
  - Schritt 1: E-Mail eingeben → Code wird per E-Mail gesendet
  - Schritt 2: 6-stelligen Code eingeben (Auto-Verify wenn alle 6 Felder ausgefuellt)
  - Schritt 3: (Nur neue Kunden) Profil vervollstaendigen: Vorname, Name, Strasse, PLZ, Ort, Mobile (Pflicht), Firma (optional)
  - Bestehende Kunden: Direkt zum Konto nach Code-Verifikation
- **Sicherheit:** Rate-Limiting (max 3 Codes/10min), max 5 Fehlversuche pro Code, Code 10min gueltig, Admin-Emails blockiert
- **Backend-Endpoints:** POST /api/auth/send-code, POST /api/auth/verify-code, POST /api/auth/complete-profile
- **DB:** Neue Collection 'verification_codes', User-Felder erweitert (street, plz, city, mobile, profile_complete, email_verified)
- Testing-Agent bestaetigt: 100% (12/12 Backend, Frontend UI verifiziert)

## Test Reports
- iteration_32: 100% (13/13 Backend, Frontend komplett)
- iteration_33: **100%** (9/9 Backend, alle 5 Sprachen + Quick Inquiry Widget)
- 08.04.2026: Frontend Smoke-Test auf Preview erfolgreich (/trucks, /faq, /trucks/burger-truck)
- 08.04.2026: Frontend-Testagent erfolgreich - Canonical + JSON-LD + FAQ-Toggles ohne Layout-Regression
- 08.04.2026: Backend-Testagent erfolgreich - API-/SEO-Endpunkte 11/11 bestanden
- 08.04.2026: Frontend Smoke-Test erfolgreich (/blog) inkl. visueller Kontrolle der neuen SEO-Landingpage-Ausgabe
- 08.04.2026: Frontend-Testagent erfolgreich - /blog, /kontakt, /ueber-uns, /fuer-veranstalter, /private-events mit Canonical + JSON-LD 5/5 bestanden
- 08.04.2026: Backend-Testagent erfolgreich - /api/blog, /api/seo/structured-data, /api/seo/events-schema, /api/seo/google-verification, /api/trucks 5/5 bestanden
- iteration_34: **100%** Frontend-Visual-Upgrade (13/13 Features verifiziert, alle 8 Verbesserungen bestanden)
- iteration_35: **100%** Passwortlose Kunden-Auth (12/12 Backend, Frontend UI verifiziert)
- iteration_36: **100%** Buchungs-Wizard (15/15 Backend, 6 Frontend-Steps + Admin Menu-Kategorien verifiziert)
- iteration_37: **Manueller Curl-Test** Accept-Booking-Flow: Status→confirmed, Kalender-Block erstellt, E-Mail-Template generiert


## 03.02.2026 — Rechtsseiten + GmbH-Entfernung
- **AGB** (`/agb`): 16 Paragraphen, Schweizer-Recht-konform, Foodtruck-Catering spezifisch
  (Geltungsbereich, Buchung, Preise/MWST, Anzahlung, Stornierung-Staffelung, Höhere Gewalt,
  HACCP/Lebensmittel, Haftung, Bildrechte, Reklamationen, Gerichtsstand Wetzikon)
- **Datenschutzerklärung** (`/datenschutz`): DSGVO + nDSG (Schweiz) konform, 17 Sektionen
  (Verantwortliche Stelle, Datenkategorien, Rechtsgrundlagen, Cookies, OTP-Login,
  Drittanbieter, Speicherdauer, Betroffenenrechte, EDÖB-Beschwerderecht)
- **Impressum** (`/impressum`): Anbieterkennzeichnung, Haftungsausschluss, Urheberrechte
- Footer-Links auf alle 3 Legal-Pages aktiv (`/agb`, `/datenschutz`, `/impressum`)
- Eigenes CSS-Modul `.sf-legal` für Long-Form-Typografie (Heading-Hierarchie, Bullet-Lists,
  goldene Akzent-Boxen, Mobile-Responsive)
- Alle Seiten SSR mit JSON-LD (WebPage Schema + BreadcrumbList) + Canonical-Tags
- **GmbH überall entfernt:** Footer, Kontakt-Page, ContactPage-Default, PDF-Generator (3
  Stellen), Settings-DB-Eintrag (`company_name: TRUCKSonROAD`) – verifiziert, dass kein
  einziges "GmbH" mehr im öffentlichen HTML serviert wird (außer Test-Mock)
- Verifizierung: HTTP 200 für alle 3 Seiten, Build erfolgreich, Smoke-Test grün


## 07.05.2026 — Legal-Editor + Versions-/Audit-Log (revDSG/DSGVO-konform)
- **Backend** (`routes/legal.py`, `legal_seed.py`):
  - 7 neue API-Endpoints: GET /api/legal/{type} (public), GET/PUT /api/admin/legal,
    GET /api/admin/legal/{type}/versions, GET .../{version_id}, POST .../restore/{version_id}
  - 2 neue Collections: `legal_documents` (current state), `legal_versions` (audit log)
  - Auto-Seed v1 beim Startup für AGB/Datenschutz/Impressum aus `legal_seed.py`
  - Unified Diff-Berechnung pro Speicherung (added/removed lines + diff_text bis 500 lines)
- **Frontend Public** (`/agb`, `/datenschutz`, `/impressum`):
  - Force-dynamic SSR — fetcht jeweils aktuelle Version aus DB
  - Neuer `LegalRenderer.js` mit Markdown-light: Bullet-Listen (`- `), Bold (`**…**`),
    Links (`[text](url)`), automatische Absatz-Splittung
  - Footer-Meta zeigt "Letzte Aktualisierung: TT. Monat JJJJ · Version N"
- **Admin Editor** (`/admin/legal`, `/admin/legal/{type}`):
  - Index-Page mit 3 Cards (AGB/Datenschutz/Impressum) + Versions-Badges
  - Editor mit Titel, Untertitel, frei sortierbaren Sektionen (Add/Move/Remove),
    Pro-Section: Heading-Input + Markdown-Textarea, Format-Hilfe inline
  - Sticky Save-Bar mit "Änderungsnotiz"-Feld (für Audit-Log)
  - Historie-Modal: Timeline aller Versionen mit Diff-Badge (+X/−Y), Admin, Datum,
    Notes; "Wiederherstellen"-Button erstellt neue Version mit `restored_from_version`
  - Diff-Modal: Unified-Diff-Anzeige im Terminal-Style
  - Sidebar-Eintrag "Rechtliches" mit Scale-Icon
- **Compliance-Wert:** Bei revDSG-/DSGVO-Audit kann jederzeit nachgewiesen werden,
  welche Fassung der Rechtstexte zwischen welchen Datums-Werten gültig war. Ein Klick
  reicht für Rollback ohne Verlust der Audit-Historie.
- **Test-Status:** iteration_37 — 100% Backend (10/10 pytest) + 100% Frontend
  (alle Flows: Card-Grid, Editor, Historie-Modal, Diff-Modal, Restore)
- DB nach Test-Cleanup zurück auf v1 für alle 3 Dokumente


## 09.05.2026 — Umlaut-Fix + DSGVO Cookie-Consent-Banner
- **P0 Umlaut-Fix:** `auth_routes.py` build_verification_code_email + subject_map
  korrigiert für DE (Bestätigungscode/gültig), FR (vérification/à TrucksOnRoad),
  IT (è valido). EN bleibt korrekt.
- **P2 Cookie-Banner (DSGVO + Schweizer nDSG konform):**
  - `CookieConsentContext.js`: Provider mit useState+useEffect, localStorage-Persistenz,
    Versionierung (COOKIE_VERSION='1'), Storage-Key `trucksonroad-consent-v1`
  - `CookieBanner.js`: 2-stufiges UI – kompakter Bottom-Banner (3 Buttons:
    "Einstellungen" / "Nur notwendige" / "Alle akzeptieren") + ausführliches
    Settings-Modal mit 4 Kategorien (Notwendig/Funktional/Analyse/Marketing)
  - 4 Kategorien als iOS-Style Toggle-Switches; "Notwendig" ist immer aktiv (golden)
  - Footer-Link "Cookie-Einstellungen" (Cookie-Icon) öffnet Modal jederzeit erneut
  - Premium-Design im Brand-Theme (dunkles Glas, gold/teal Akzente, slide-up Animation)
  - Datenschutzerklärung Section 6 automatisch auf v2 aktualisiert mit Hinweis auf
    die 4 Kategorien + den "Cookie-Einstellungen"-Footer-Link
- **Compliance:**
  - Opt-In Standard (alle nicht-notwendigen Cookies initial OFF)
  - "Alle ablehnen" gleich prominent wie "Alle akzeptieren"
  - Granulare Kontrolle, jederzeit änderbar, Versions-Re-Consent möglich
  - Verlinkt auf Datenschutzerklärung
- **Test-Status:** iteration_38 — 100% Backend (10/10 pytest umlauts + send-code +
  datenschutz section) + 100% Frontend (Banner-Visibility, Accept-All, Necessary-Only,
  Settings-Modal, selective Save, Footer-Reopen, Datenschutz-Render)

## 12.05.2026 — DB-Backup-System mit Infomaniak Swiss Backup S3
- **Backend Services:**
  - `services/db_backup.py` – mongodump → tar.gz, lokale Rotation (14 Tage default)
  - `services/cloud_backup.py` – boto3 S3-Client (Infomaniak Swiss Backup),
    upload/list/prune/delete + test_connection
  - `services/frontend_url.py` – Helper für externe URLs
- **9 Admin-Endpoints in `routes/backups.py`:**
  - GET/POST/DELETE `/api/admin/backups` (local list, run, delete)
  - GET `/api/admin/backups/download/{filename}`
  - GET/PUT `/api/admin/backups/cloud/config` (secret_key MASKED in response)
  - POST `/api/admin/backups/cloud/test` (Verbindungstest)
  - GET `/api/admin/backups/cloud/list` + DELETE `/api/admin/backups/cloud/{key}`
- **Cron-Loop `_db_backup_loop` in server.py:** täglich 03:00 Europe/Zurich,
  mongodump → tar.gz → Infomaniak Upload → Cloud-Retention-Pruning
- **Settings (`type:"cloud_backup"`):** enabled, endpoint, access_key, secret_key,
  bucket, prefix (**`truck`** für App-Trennung), region, retention_days (default 30)
- **Frontend Admin UI** (`/admin/backups`):
  - DB-Backup-System Card mit "Backup jetzt starten"-Button
  - Infomaniak S3 Config-Card mit allen 8 Feldern, Secret-Key-Mask mit Show/Hide,
    Aktivieren-Toggle, "Verbindung testen" + "Speichern"
  - Lokale Backups Liste mit Download/Delete pro Eintrag, Rotations-Hinweis
  - Cloud-Backups Liste mit Key-Anzeige + Delete (Infomaniak)
  - Sidebar-Eintrag "Backups" mit Database-Icon
- **UX-Verbesserung:** Cookie-Consent-Banner ist auf `/admin/*` Routes deaktiviert
  (via usePathname Check) — Admins sind interne Nutzer
- **Pakete:** boto3==1.42.75, mongodump (system binary) bereits vorhanden
- **Test-Status:** iteration_39 — 12/12 Backend pytest gegen REAL Infomaniak Bucket
  `emergent-apps-backup` mit Prefix `truck/` + 16 Frontend-Flows (alle 100%)
- **Live verifiziert:** mongodump (68 KB) erstellt + zu Infomaniak hochgeladen
  unter `s3://emergent-apps-backup/truck/mongodump-20260512T073215Z.tar.gz`
- **Backlog (Testing Agent Code Review):**
  - Optional: access_key in GET /cloud/config maskieren (defense-in-depth)
  - Optional: role=='admin' Check in routes/backups.py (konsistent mit Rest:
    aktuell nur Login-Pflicht via get_current_user)



## 12.05.2026 — Backup: Preview/Production-Trennung
- **Auto-Disable Cloud-Upload in Preview:** Cloud-Upload (Infomaniak) läuft nur,
  wenn `ENVIRONMENT=production` in `backend/.env` gesetzt ist. Andernfalls werden
  lokale Backups weiterhin erstellt, aber NICHT in den Bucket hochgeladen.
- **Sichtbar im Admin-UI:** Goldener Warn-Banner *"Cloud-Upload in „preview"-Umgebung
  blockiert"* mit Erklärung. data-testid: `admin-backups-env-warning`
- **Backend-Helper:** `get_environment()` + `is_production()` + `cloud_upload_allowed(cfg)`
  in `routes/backups.py`. Cron-Loop und manuelles "Backup jetzt starten" wenden
  beide den Check an.
- **API-Response Erweiterung:** GET `/admin/backups/cloud/config` liefert jetzt
  zusätzlich `environment`, `is_production`, `cloud_upload_blocked`.
  POST `/admin/backups` liefert `cloud: {ok:false, skipped:true, reason:"..."}`
  wenn Upload geskippt wurde.
- **Test-Bucket bereinigt:** alle `truck/mongodump-*` aus Preview-Tests gelöscht.
- **Production-Deploy-Hinweis:** Vor dem Live-Schalten muss `ENVIRONMENT=production`
  in der Production-`.env` gesetzt sein, sonst läuft auch dort kein Cloud-Upload.

## 14.05.2026 — Google OAuth Customer Login
- **Eigenes Google Cloud Projekt** (Client ID 589307861900-...) — kein Emergent-managed Auth
- **Backend** `routes/google_auth.py`:
  - GET `/api/auth/google/login` — 302 zu Google mit CSRF-State + `next`-Cookie
  - GET `/api/auth/google/callback` — Code-Exchange, Userinfo, User-Lookup/Create, JWT-Cookie, 302 zur App
  - Dynamische `redirect_uri` aus Request (X-Forwarded-Host/Proto) — funktioniert in Preview & Production ohne Hardcoding
  - Auto-Create Customer wenn E-Mail neu, sonst Link via E-Mail. Felder: `auth_provider="google"`, `google_sub`, `google_picture`
  - Neue User → Redirect zu `/konto/profil-vervollstaendigen`, bestehende → `/konto`
  - Error-Handling: state_mismatch / token_exchange_failed / email_not_verified → 302 zu `/konto/login?error=...`
- **Frontend** `CustomerLogin.js`:
  - "ODER"-Divider + "Mit Google anmelden"-Button mit 4-Farben Google-G-Logo
  - Error-Toast bei `?error=` Query-Param (lokalisierte Meldungen)
  - `useSearchParams` benötigt Suspense — 3 Konto-Pages mit `dynamic="force-dynamic"` + `<Suspense>` umhüllt
- **Pakete:** `authlib==1.7.2`, `itsdangerous==2.2.0` (installiert für künftige Erweiterungen)
- **Credentials in `backend/.env`:** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- **Test-Status:** Manuell verifiziert — 302-Redirect zu Google korrekt, State-Cookie HttpOnly/Secure/lax gesetzt, Build erfolgreich, UI rendert sauber
- **Production-Hinweis:** Vor Deploy müssen `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` in Production-.env vorhanden sein. Google Cloud Console enthält bereits beide Redirect-URIs (Preview + trucksonroad.ch)

