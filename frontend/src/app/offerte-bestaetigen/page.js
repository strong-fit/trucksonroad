"use client";
import { Suspense } from "react";
import OfferConfirmPage from "@/views/OfferConfirmPage";

export default function Page() {
  return (
    <Suspense fallback={<div style={{ minHeight: '100vh', background: '#0a0a08', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f5f0e8' }}>Laden...</div>}>
      <OfferConfirmPage />
    </Suspense>
  );
}
