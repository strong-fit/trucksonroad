"use client";

import { useState, useEffect } from "react";
import { Cookie, ShieldCheck, Settings, X } from "lucide-react";
import { useCookieConsent } from "@/contexts/CookieConsentContext";

const CATEGORIES = [
  {
    key: "necessary",
    title: "Notwendig",
    locked: true,
    description:
      "Technisch erforderlich für den Betrieb der Website und die Login-Funktion. Diese Cookies können nicht deaktiviert werden.",
  },
  {
    key: "functional",
    title: "Funktional",
    description:
      "Speichern Ihre Sprachwahl (DE/EN/FR/IT/ES) sowie persönliche UI-Präferenzen für eine bessere Nutzererfahrung.",
  },
  {
    key: "analytics",
    title: "Analyse",
    description:
      "Helfen uns zu verstehen, wie Besucher unsere Website nutzen, um sie kontinuierlich zu verbessern. Daten werden anonymisiert verarbeitet.",
  },
  {
    key: "marketing",
    title: "Marketing",
    description:
      "Ermöglichen personalisierte Werbung und Re-Targeting auf Drittplattformen. Nur mit Ihrer ausdrücklichen Einwilligung aktiv.",
  },
];

export default function CookieBanner() {
  const {
    consent,
    showBanner,
    showSettings,
    setShowSettings,
    acceptAll,
    acceptNecessary,
    savePreferences,
  } = useCookieConsent();

  const [draft, setDraft] = useState({
    necessary: true,
    functional: false,
    analytics: false,
    marketing: false,
  });

  useEffect(() => {
    if (consent) {
      setDraft(consent);
    }
  }, [consent, showSettings]);

  if (!showBanner) return null;

  const toggle = (key) => {
    if (key === "necessary") return;
    setDraft((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = () => {
    savePreferences(draft);
  };

  return (
    <>
      <div className="sf-cookie-overlay" data-testid="cookie-banner-overlay" />

      {!showSettings && (
        <div
          className="sf-cookie-banner"
          role="dialog"
          aria-labelledby="cookie-banner-title"
          aria-describedby="cookie-banner-desc"
          data-testid="cookie-banner"
        >
          <div className="sf-cookie-banner-icon">
            <Cookie size={22} />
          </div>
          <div className="sf-cookie-banner-content">
            <h2 id="cookie-banner-title" className="sf-cookie-banner-title">
              Cookies & Datenschutz
            </h2>
            <p id="cookie-banner-desc" className="sf-cookie-banner-text">
              Wir verwenden technisch notwendige Cookies für den Betrieb dieser Website. Mit
              Ihrer Einwilligung setzen wir zusätzlich funktionale, Analyse- und Marketing-Cookies
              ein. Sie können Ihre Auswahl jederzeit anpassen. Mehr in unserer{" "}
              <a href="/datenschutz" className="sf-cookie-link" data-testid="cookie-banner-privacy-link">
                Datenschutzerklärung
              </a>
              .
            </p>
            <div className="sf-cookie-banner-actions">
              <button
                type="button"
                className="sf-cookie-btn-ghost"
                onClick={() => setShowSettings(true)}
                data-testid="cookie-banner-settings-btn"
              >
                <Settings size={14} /> Einstellungen
              </button>
              <button
                type="button"
                className="sf-cookie-btn-secondary"
                onClick={acceptNecessary}
                data-testid="cookie-banner-necessary-btn"
              >
                Nur notwendige
              </button>
              <button
                type="button"
                className="sf-cookie-btn-primary"
                onClick={acceptAll}
                data-testid="cookie-banner-accept-all-btn"
              >
                <ShieldCheck size={14} /> Alle akzeptieren
              </button>
            </div>
          </div>
        </div>
      )}

      {showSettings && (
        <div
          className="sf-cookie-settings"
          role="dialog"
          aria-labelledby="cookie-settings-title"
          data-testid="cookie-settings-modal"
        >
          <div className="sf-cookie-settings-header">
            <h2 id="cookie-settings-title">Cookie-Einstellungen</h2>
            <button
              type="button"
              className="sf-cookie-settings-close"
              onClick={() => setShowSettings(false)}
              aria-label="Schliessen"
              data-testid="cookie-settings-close"
            >
              <X size={18} />
            </button>
          </div>
          <div className="sf-cookie-settings-body">
            <p className="sf-cookie-settings-intro">
              Detaillierte Kontrolle über die einzelnen Cookie-Kategorien. Ihre Wahl wird
              lokal gespeichert und gilt für 12 Monate. Sie können sie jederzeit über den
              Footer-Link <em>„Cookie-Einstellungen"</em> ändern.
            </p>
            {CATEGORIES.map((cat) => (
              <div
                key={cat.key}
                className={`sf-cookie-cat ${draft[cat.key] ? "is-on" : ""} ${cat.locked ? "is-locked" : ""}`}
                data-testid={`cookie-cat-${cat.key}`}
              >
                <div className="sf-cookie-cat-row">
                  <div>
                    <strong>{cat.title}</strong>
                    {cat.locked && (
                      <span className="sf-cookie-cat-locked">
                        <ShieldCheck size={11} /> Immer aktiv
                      </span>
                    )}
                  </div>
                  <label className="sf-cookie-toggle" aria-label={`${cat.title} aktivieren`}>
                    <input
                      type="checkbox"
                      checked={!!draft[cat.key]}
                      disabled={cat.locked}
                      onChange={() => toggle(cat.key)}
                      data-testid={`cookie-toggle-${cat.key}`}
                    />
                    <span className="sf-cookie-toggle-track" />
                  </label>
                </div>
                <p className="sf-cookie-cat-desc">{cat.description}</p>
              </div>
            ))}
          </div>
          <div className="sf-cookie-settings-footer">
            <button
              type="button"
              className="sf-cookie-btn-ghost"
              onClick={acceptNecessary}
              data-testid="cookie-settings-reject-btn"
            >
              Alle ablehnen
            </button>
            <button
              type="button"
              className="sf-cookie-btn-secondary"
              onClick={handleSave}
              data-testid="cookie-settings-save-btn"
            >
              Auswahl speichern
            </button>
            <button
              type="button"
              className="sf-cookie-btn-primary"
              onClick={acceptAll}
              data-testid="cookie-settings-accept-all-btn"
            >
              <ShieldCheck size={14} /> Alle akzeptieren
            </button>
          </div>
        </div>
      )}
    </>
  );
}
