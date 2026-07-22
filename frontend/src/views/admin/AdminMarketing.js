"use client";
import { useEffect, useState } from "react";
import { AdminLayout } from "@/views/admin/AdminDashboard";
import api from "@/lib/api";
import { toast } from "sonner";
import { Save, TrendingUp, ShieldCheck, ExternalLink } from "lucide-react";

const FIELDS = [
  {
    key: "ga4_measurement_id",
    label: "Google Analytics 4 – Measurement ID",
    placeholder: "G-XXXXXXX",
    hint: "Property > Datenstreams > Measurement-ID. Kategorie: analytics",
    docs: "https://support.google.com/analytics/answer/9539598",
    category: "analytics",
  },
  {
    key: "gtm_container_id",
    label: "Google Tag Manager – Container ID",
    placeholder: "GTM-XXXXXXX",
    hint: "Optional. Wenn gesetzt, laufen alle Tags via GTM. Kategorie: analytics",
    docs: "https://tagmanager.google.com/",
    category: "analytics",
  },
  {
    key: "clarity_project_id",
    label: "Microsoft Clarity – Project ID",
    placeholder: "xxxxxxxxxx",
    hint: "Kostenlose Heatmaps & Sitzungsaufzeichnungen. Kategorie: analytics",
    docs: "https://clarity.microsoft.com/",
    category: "analytics",
  },
  {
    key: "bing_uet_tag",
    label: "Microsoft / Bing UET Tag",
    placeholder: "1234567",
    hint: "Für Bing Ads Conversion-Tracking. Kategorie: analytics",
    docs: "https://about.ads.microsoft.com/",
    category: "analytics",
  },
  {
    key: "meta_pixel_id",
    label: "Meta Pixel ID (Facebook & Instagram)",
    placeholder: "123456789012345",
    hint: "Business Manager > Ereignismanager > Datenquellen. Kategorie: marketing",
    docs: "https://business.facebook.com/events_manager",
    category: "marketing",
  },
  {
    key: "google_ads_conversion_id",
    label: "Google Ads – Conversion ID",
    placeholder: "AW-XXXXXXX",
    hint: "Google Ads > Tools > Conversions. Kategorie: marketing",
    docs: "https://ads.google.com/",
    category: "marketing",
  },
  {
    key: "google_ads_conversion_label",
    label: "Google Ads – Conversion Label (nur der Teil nach dem /)",
    placeholder: "abcDEF123",
    hint: "Wird für Formular-Conversions verwendet. Kategorie: marketing",
    category: "marketing",
  },
  {
    key: "tiktok_pixel_id",
    label: "TikTok Pixel ID",
    placeholder: "CXXXXXXXXXXXXXXXX",
    hint: "TikTok Ads Manager > Events > Web-Events. Kategorie: marketing",
    docs: "https://ads.tiktok.com/",
    category: "marketing",
  },
  {
    key: "linkedin_partner_id",
    label: "LinkedIn Insight – Partner ID",
    placeholder: "1234567",
    hint: "Für B2B-Retargeting. Kategorie: marketing",
    docs: "https://www.linkedin.com/campaignmanager/",
    category: "marketing",
  },
  {
    key: "google_verification",
    label: "Google Search Console – Verification Code",
    placeholder: "abc123...",
    hint: "Nur der `content=` Teil des Meta-Tags. Kein Consent nötig (technisch).",
    docs: "https://search.google.com/search-console",
    category: "technical",
  },
];

const CATEGORY_LABELS = {
  analytics: {
    title: "Analyse & Statistik",
    subtitle: "Aktiv, sobald ein Besucher die Kategorie Analyse im Cookie-Banner akzeptiert.",
    color: "#4db6ac",
  },
  marketing: {
    title: "Marketing & Remarketing",
    subtitle: "Aktiv, sobald ein Besucher die Kategorie Marketing akzeptiert.",
    color: "#e8a05c",
  },
  technical: {
    title: "Technische Verifikation",
    subtitle: "Werden immer geladen (keine Cookies gesetzt).",
    color: "#8a8a80",
  },
};

export default function AdminMarketing() {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .get("/admin/settings")
      .then((r) => setSettings(r.data || {}))
      .catch(() => setSettings({}));
  }, []);

  const update = (k, v) => setSettings((s) => ({ ...s, [k]: v }));

  const save = async () => {
    setSaving(true);
    try {
      await api.put("/admin/settings", settings);
      toast.success("Marketing-Konfiguration gespeichert");
    } catch {
      toast.error("Speichern fehlgeschlagen");
    } finally {
      setSaving(false);
    }
  };

  if (!settings) {
    return (
      <AdminLayout title="Marketing & Tracking">
        <div className="adm-empty">Wird geladen...</div>
      </AdminLayout>
    );
  }

  const activeCount = FIELDS.filter((f) => (settings[f.key] || "").trim()).length;

  const grouped = ["analytics", "marketing", "technical"].map((cat) => ({
    cat,
    items: FIELDS.filter((f) => f.category === cat),
  }));

  return (
    <AdminLayout title="Marketing & Tracking">
      <div data-testid="admin-marketing">
        {/* Status header */}
        <div
          className="adm-detail"
          style={{
            marginBottom: "1.25rem",
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 12,
              background: "rgba(77,182,172,0.15)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#4db6ac",
            }}
          >
            <TrendingUp size={22} />
          </div>
          <div style={{ flex: 1, minWidth: 220 }}>
            <div style={{ fontWeight: 700, fontSize: "1.05rem" }}>Marketing & Tracking Zentrale</div>
            <div style={{ fontSize: "0.82rem", color: "var(--adm-text-muted)", marginTop: 3 }}>
              {activeCount} von {FIELDS.length} Trackern konfiguriert. Alle Scripts werden erst nach
              Cookie-Consent des Besuchers geladen (DSGVO / nDSG).
            </div>
          </div>
          <button
            className="adm-btn adm-btn-primary"
            onClick={save}
            disabled={saving}
            data-testid="marketing-save-top"
          >
            <Save size={15} /> {saving ? "Speichern..." : "Speichern"}
          </button>
        </div>

        {/* Consent hint box */}
        <div
          style={{
            display: "flex",
            gap: "0.75rem",
            padding: "1rem 1.25rem",
            borderRadius: 12,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.06)",
            marginBottom: "1.5rem",
            fontSize: "0.85rem",
            color: "var(--adm-text-muted)",
          }}
        >
          <ShieldCheck size={18} style={{ flexShrink: 0, marginTop: 2, color: "#4db6ac" }} />
          <div>
            <strong style={{ color: "var(--adm-text)" }}>DSGVO / nDSG-konform:</strong>{" "}
            Alle Analyse-Cookies werden nur nach expliziter Zustimmung im Cookie-Banner geladen.
            Marketing-Cookies (Meta, Google Ads, TikTok, LinkedIn) benoetigen die Kategorie Marketing.
            Die technische Google-Verifikation laeuft ohne Cookies und ist immer aktiv.
          </div>
        </div>

        {/* Fields grouped by category */}
        {grouped.map(({ cat, items }) => {
          const meta = CATEGORY_LABELS[cat];
          return (
            <div key={cat} className="adm-detail" style={{ marginBottom: "1.25rem" }}>
              <div
                className="adm-detail-header"
                style={{
                  borderBottom: "1px solid var(--adm-border)",
                  paddingBottom: "0.75rem",
                  marginBottom: "1rem",
                }}
              >
                <span
                  className="adm-detail-title"
                  style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
                >
                  <span
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      background: meta.color,
                    }}
                  />
                  {meta.title}
                </span>
                <div
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--adm-text-muted)",
                    marginTop: 4,
                  }}
                >
                  {meta.subtitle}
                </div>
              </div>

              <div style={{ display: "grid", gap: "1rem" }}>
                {items.map((f) => (
                  <div key={f.key} data-testid={`marketing-field-${f.key}`}>
                    <div className="adm-form-label" style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem" }}>
                      <span>{f.label}</span>
                      {f.docs && (
                        <a
                          href={f.docs}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontSize: "0.72rem",
                            color: "var(--adm-accent)",
                            display: "flex",
                            alignItems: "center",
                            gap: 3,
                          }}
                        >
                          Anleitung <ExternalLink size={11} />
                        </a>
                      )}
                    </div>
                    <input
                      className="adm-input"
                      value={settings[f.key] || ""}
                      onChange={(e) => update(f.key, e.target.value)}
                      placeholder={f.placeholder}
                      data-testid={`marketing-input-${f.key}`}
                    />
                    <div style={{ fontSize: "0.72rem", color: "var(--adm-text-muted)", marginTop: "0.3rem" }}>
                      {f.hint}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {/* Bottom save */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "1rem" }}>
          <button
            className="adm-btn adm-btn-primary"
            onClick={save}
            disabled={saving}
            data-testid="marketing-save-bottom"
          >
            <Save size={15} /> {saving ? "Speichern..." : "Alle Marketing-Einstellungen speichern"}
          </button>
        </div>
      </div>
    </AdminLayout>
  );
}
