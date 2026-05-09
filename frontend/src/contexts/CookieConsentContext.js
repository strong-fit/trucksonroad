"use client";

/**
 * Cookie Consent — DSGVO + Schweizer nDSG konform.
 *
 * Storage key: trucksonroad-consent-v{COOKIE_VERSION}
 * Version inkrementieren, wenn sich die Cookie-Kategorien materiell ändern → Banner erscheint
 * automatisch erneut (re-consent).
 *
 * Categories:
 *   - necessary: immer true (technisch nötig, z.B. Login-Session)
 *   - functional: Sprache, UI-Präferenzen
 *   - analytics: Statistik-Tools (z.B. Google Analytics)
 *   - marketing: Werbe- / Re-Targeting-Cookies
 */
import { createContext, useContext, useEffect, useState, useCallback } from "react";

export const COOKIE_VERSION = "1";
const STORAGE_KEY = `trucksonroad-consent-v${COOKIE_VERSION}`;

const DEFAULT_CONSENT = {
  necessary: true,
  functional: false,
  analytics: false,
  marketing: false,
};

const CookieConsentContext = createContext({
  consent: null,
  showBanner: false,
  showSettings: false,
  setShowSettings: () => {},
  acceptAll: () => {},
  acceptNecessary: () => {},
  savePreferences: () => {},
  openBanner: () => {},
});

export function CookieConsentProvider({ children }) {
  const [consent, setConsent] = useState(null);
  const [hydrated, setHydrated] = useState(false);
  const [showBanner, setShowBanner] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    setHydrated(true);
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === "object" && parsed.version === COOKIE_VERSION) {
          setConsent({ ...DEFAULT_CONSENT, ...parsed.consent });
          return;
        }
      }
    } catch {
      /* ignore */
    }
    setShowBanner(true);
  }, []);

  const persist = useCallback((next) => {
    const payload = {
      version: COOKIE_VERSION,
      consent: next,
      decided_at: new Date().toISOString(),
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch {
      /* ignore quota errors */
    }
    setConsent(next);
    setShowBanner(false);
    setShowSettings(false);
  }, []);

  const acceptAll = useCallback(() => {
    persist({ necessary: true, functional: true, analytics: true, marketing: true });
  }, [persist]);

  const acceptNecessary = useCallback(() => {
    persist({ ...DEFAULT_CONSENT });
  }, [persist]);

  const savePreferences = useCallback(
    (preferences) => {
      persist({ ...DEFAULT_CONSENT, ...preferences, necessary: true });
    },
    [persist]
  );

  const openBanner = useCallback(() => {
    setShowSettings(true);
    setShowBanner(true);
  }, []);

  return (
    <CookieConsentContext.Provider
      value={{
        consent,
        showBanner: hydrated && showBanner,
        showSettings,
        setShowSettings,
        acceptAll,
        acceptNecessary,
        savePreferences,
        openBanner,
      }}
    >
      {children}
    </CookieConsentContext.Provider>
  );
}

export function useCookieConsent() {
  return useContext(CookieConsentContext);
}
