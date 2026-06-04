"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import LegalRenderer from "@/components/LegalRenderer";

/**
 * Client-side fetcher for legal documents.
 * Used by /agb, /datenschutz, /impressum to avoid relying on
 * Next.js force-dynamic SSR on production hosting where dynamic
 * routes may not be properly built / served.
 */
export default function LegalPageClient({ docType, testIdPrefix }) {
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .get(`/legal/${docType}`)
      .then((r) => {
        if (!cancelled) setDoc(r.data);
      })
      .catch(() => {
        if (!cancelled) setDoc(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [docType]);

  if (loading) {
    return (
      <div
        className="sf-page sf-legal"
        data-testid={`${testIdPrefix}-loading`}
        style={{ minHeight: "60vh", display: "flex", alignItems: "center", justifyContent: "center" }}
      >
        <div style={{ color: "var(--sf-gray)", fontSize: "0.95rem" }}>Wird geladen …</div>
      </div>
    );
  }

  return <LegalRenderer doc={doc} testIdPrefix={testIdPrefix} />;
}
