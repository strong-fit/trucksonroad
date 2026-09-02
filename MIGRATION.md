# Migration zu Next.js-Template (Option A) — TRUCKSonROAD

Emergent Support hat bestätigt: Das aktuelle Projekt läuft auf dem **Farm-Template** (nur
statisches React), nicht auf einem echten **Next.js-Server**. Deshalb werden `page.js`,
`layout.js` und `main-app.js` nicht ausgeliefert → leere Seite. Lösung: Neues Projekt auf dem
**Next.js-Template**, GitHub-Repo importieren. Code bleibt unverändert.

Diese Datei beschreibt, was im neuen Job neu eingerichtet werden muss (kcommt NICHT automatisch mit).

---

## 1. Environment-Variablen / Secrets neu setzen

### backend/.env
| Key | Herkunft im neuen Job |
| --- | --- |
| `MONGO_URL` | **Plattform stellt bereit** (nicht kopieren) |
| `DB_NAME` | **Plattform stellt bereit** (nicht kopieren) |
| `EMERGENT_LLM_KEY` | **Plattform stellt bereit** (nicht kopieren) |
| `JWT_SECRET` | manuell neu setzen (beliebiger langer Zufallsstring) |
| `ADMIN_EMAIL` | manuell setzen (aktuell: `admin@truckonroad.ch`) |
| `ADMIN_PASSWORD` | manuell setzen (siehe `/app/memory/test_credentials.md`) |
| `CORS_ORIGINS` | manuell setzen (neue Live-URL + Custom Domain) |
| `FRONTEND_URL` | manuell setzen (neue Live-URL) |

### frontend/.env
| Key | Herkunft im neuen Job |
| --- | --- |
| `REACT_APP_BACKEND_URL` | **Plattform stellt bereit** (neue Preview/Prod-URL) |
| `NEXT_PUBLIC_BACKEND_URL` | = gleicher Wert wie `REACT_APP_BACKEND_URL` |
| `WDS_SOCKET_PORT` | wie bisher |
| `ENABLE_HEALTH_CHECK` | wie bisher |

> Zusätzlich in der **Admin-Oberfläche** neu hinterlegen (liegt in der DB `settings`, wird per
> DB-Restore mit übernommen — nur ggf. SMTP-App-Passwort neu eintragen): GA4-ID, Meta-Pixel,
> Clarity, Infomaniak-S3-Keys, SMTP-Passwort.

---

## 2. Datenbank übernehmen (MongoDB)

Der komplette Datenbestand wurde exportiert nach:

    /app/migration/trucksonroad_db.archive   (gzip-Archiv, ~81 KB)

Enthält u. a.: trucks (7), inquiries (22), blog_posts (13), legal_versions (10), settings (2),
users (6), faqs (8), reviews (4), calendar_blocks (5), files (14), menu_categories (4) …

**Im neuen Job wiederherstellen** (Agent/Terminal):

```bash
# Datei liegt nach GitHub-Import unter /app/migration/trucksonroad_db.archive
mongorestore --uri="$MONGO_URL" \
  --nsFrom='test_database.*' --nsTo="${DB_NAME}.*" \
  --gzip --archive=/app/migration/trucksonroad_db.archive
```

> Hinweis: `--nsFrom/--nsTo` mappt die alte DB `test_database` auf den neuen `DB_NAME`.

---

## 3. Ablauf (Kurzfassung)

1. Emergent-Startseite → **Neues Projekt** → App-Typ **Next.js** wählen.
2. Bestehendes **GitHub-Repo importieren** (kein Rewrite).
3. Env-Variablen aus Tabelle oben setzen.
4. DB per `mongorestore` (Schritt 2) einspielen.
5. Deployen → App läuft jetzt auf echtem Next.js-Server (SSR/SEO wie gebaut).

Uploads/Bilder liegen bereits im Emergent Object Storage (als URLs in der DB) und funktionieren
nach dem Restore direkt weiter.
