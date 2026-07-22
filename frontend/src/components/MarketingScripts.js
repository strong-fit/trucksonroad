"use client";
/**
 * Injects marketing / tracking scripts into the site, gated by cookie consent.
 * IDs come from /api/marketing/config (public endpoint, filled by admin).
 *
 * Categories:
 *   - analytics: GA4, GTM, Microsoft Clarity, Bing UET
 *   - marketing: Meta Pixel, TikTok Pixel, LinkedIn Insight, Google Ads
 */
import Script from "next/script";
import { useEffect, useState } from "react";
import { useCookieConsent } from "@/contexts/CookieConsentContext";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "";

export default function MarketingScripts() {
  const { consent } = useCookieConsent();
  const [cfg, setCfg] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const url = `${BACKEND_URL}/api/marketing/config`;
    fetch(url)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (!cancelled) setCfg(data || null);
      })
      .catch(() => {
        if (!cancelled) setCfg(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    // Expose Google Ads conversion IDs globally for lib/analytics.js
    if (cfg && typeof window !== "undefined") {
      window.__TOR_ADS_CONVERSION__ = {
        id: cfg.google_ads_conversion_id || "",
        label: cfg.google_ads_conversion_label || "",
      };
    }
  }, [cfg]);

  if (!cfg || !consent) return null;

  const analyticsOk = !!consent.analytics;
  const marketingOk = !!consent.marketing;

  return (
    <>
      {/* --- GA4 (analytics) --- */}
      {analyticsOk && cfg.ga4_measurement_id && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${cfg.ga4_measurement_id}`}
            strategy="afterInteractive"
          />
          <Script id="ga4-init" strategy="afterInteractive">
            {`window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);} window.gtag = gtag;
              gtag('js', new Date());
              gtag('config', '${cfg.ga4_measurement_id}', { anonymize_ip: true });`}
          </Script>
        </>
      )}

      {/* --- Google Ads (marketing) --- */}
      {marketingOk && cfg.google_ads_conversion_id && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${cfg.google_ads_conversion_id}`}
            strategy="afterInteractive"
          />
          <Script id="google-ads-init" strategy="afterInteractive">
            {`window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);} window.gtag = window.gtag || gtag;
              gtag('js', new Date());
              gtag('config', '${cfg.google_ads_conversion_id}');`}
          </Script>
        </>
      )}

      {/* --- GTM (analytics) --- */}
      {analyticsOk && cfg.gtm_container_id && (
        <Script id="gtm-init" strategy="afterInteractive">
          {`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            })(window,document,'script','dataLayer','${cfg.gtm_container_id}');`}
        </Script>
      )}

      {/* --- Microsoft Clarity (analytics) --- */}
      {analyticsOk && cfg.clarity_project_id && (
        <Script id="clarity-init" strategy="afterInteractive">
          {`(function(c,l,a,r,i,t,y){
            c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
          })(window, document, "clarity", "script", "${cfg.clarity_project_id}");`}
        </Script>
      )}

      {/* --- Bing UET (analytics) --- */}
      {analyticsOk && cfg.bing_uet_tag && (
        <Script id="bing-uet" strategy="afterInteractive">
          {`(function(w,d,t,r,u){var f,n,i;w[u]=w[u]||[],f=function(){var o={ti:"${cfg.bing_uet_tag}"};
            o.q=w[u],w[u]=new UET(o),w[u].push("pageLoad")},n=d.createElement(t),n.src=r,n.async=1,
            n.onload=n.onreadystatechange=function(){var s=this.readyState;s&&s!=="loaded"&&s!=="complete"||(f(),n.onload=n.onreadystatechange=null)},
            i=d.getElementsByTagName(t)[0],i.parentNode.insertBefore(n,i)})(window,document,"script","//bat.bing.com/bat.js","uetq");`}
        </Script>
      )}

      {/* --- Meta Pixel (marketing) --- */}
      {marketingOk && cfg.meta_pixel_id && (
        <Script id="meta-pixel" strategy="afterInteractive">
          {`!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
            n.callMethod.apply(n,arguments):n.queue.push(arguments)};
            if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];
            t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];
            s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
            fbq('init', '${cfg.meta_pixel_id}');
            fbq('track', 'PageView');`}
        </Script>
      )}

      {/* --- TikTok Pixel (marketing) --- */}
      {marketingOk && cfg.tiktok_pixel_id && (
        <Script id="tiktok-pixel" strategy="afterInteractive">
          {`!function (w, d, t) {
            w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];
            ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"];
            ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};
            for (var i=0;i<ttq.methods.length;i++) ttq.setAndDefer(ttq,ttq.methods[i]);
            ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++) ttq.setAndDefer(e,ttq.methods[n]); return e};
            ttq.load=function(e,n){var i="https://analytics.tiktok.com/i18n/pixel/events.js";
            ttq._i=ttq._i||{},ttq._i[e]=[],ttq._i[e]._u=i,ttq._t=ttq._t||{},ttq._t[e]=+new Date,ttq._o=ttq._o||{},ttq._o[e]=n||{};
            var o=document.createElement("script");o.type="text/javascript",o.async=!0,o.src=i+"?sdkid="+e+"&lib="+t;
            var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(o,a)};
            ttq.load('${cfg.tiktok_pixel_id}');
            ttq.page();
          }(window, document, 'ttq');`}
        </Script>
      )}

      {/* --- LinkedIn Insight (marketing) --- */}
      {marketingOk && cfg.linkedin_partner_id && (
        <Script id="linkedin-insight" strategy="afterInteractive">
          {`_linkedin_partner_id = "${cfg.linkedin_partner_id}";
            window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
            window._linkedin_data_partner_ids.push(_linkedin_partner_id);
            (function(l) { if (!l){window.lintrk = function(a,b){window.lintrk.q.push([a,b])};
            window.lintrk.q=[]} var s = document.getElementsByTagName("script")[0];
            var b = document.createElement("script"); b.type = "text/javascript"; b.async = true;
            b.src = "https://snap.licdn.com/li.lms-analytics/insight.min.js";
            s.parentNode.insertBefore(b, s);})(window.lintrk);`}
        </Script>
      )}
    </>
  );
}
