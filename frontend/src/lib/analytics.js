"use client";

/**
 * Lightweight analytics helper for TrucksOnRoad.
 *
 * All tracking is only fired if the user has given the corresponding
 * cookie consent (analytics / marketing) — see CookieConsentContext.
 * Calling these helpers before consent or before scripts have loaded is safe
 * (they become a no-op).
 *
 * Usage:
 *   import { trackEvent, trackConversion } from '@/lib/analytics';
 *   trackEvent('rueckruf_submit', { location: 'home_hero' });
 *   trackConversion('inquiry_submit', { value: 1 });
 */

function safe(fn) {
  try {
    fn();
  } catch {
    /* never break the UI because of tracking */
  }
}

/** Fire a generic event to GA4 / GTM / Meta Pixel / TikTok. */
export function trackEvent(eventName, params = {}) {
  if (typeof window === "undefined") return;
  // GA4 / GTM
  safe(() => {
    if (typeof window.gtag === "function") {
      window.gtag("event", eventName, params);
    }
  });
  safe(() => {
    if (Array.isArray(window.dataLayer)) {
      window.dataLayer.push({ event: eventName, ...params });
    }
  });
  // Meta Pixel — map common events, fall back to trackCustom
  safe(() => {
    if (typeof window.fbq === "function") {
      const metaMap = {
        rueckruf_submit: "Lead",
        inquiry_submit: "Lead",
        booking_complete: "Schedule",
        phone_click: "Contact",
        whatsapp_click: "Contact",
        pdf_download: "ViewContent",
        newsletter_signup: "Subscribe",
      };
      const mapped = metaMap[eventName];
      if (mapped) {
        window.fbq("track", mapped, params);
      } else {
        window.fbq("trackCustom", eventName, params);
      }
    }
  });
  // TikTok
  safe(() => {
    if (window.ttq && typeof window.ttq.track === "function") {
      window.ttq.track(eventName, params);
    }
  });
  // LinkedIn
  safe(() => {
    if (typeof window.lintrk === "function") {
      window.lintrk("track", { conversion_id: eventName, ...params });
    }
  });
}

/**
 * Marks a Google Ads conversion (uses conversion id + label from settings,
 * injected into window by MarketingScripts).
 */
export function trackConversion(eventName, params = {}) {
  trackEvent(eventName, params);
  if (typeof window === "undefined") return;
  const conv = window.__TOR_ADS_CONVERSION__;
  if (conv && conv.id && conv.label && typeof window.gtag === "function") {
    safe(() => {
      window.gtag("event", "conversion", {
        send_to: `${conv.id}/${conv.label}`,
        ...params,
      });
    });
  }
}
