"use client";
import { Suspense } from "react";
import PublicShell from "@/components/PublicShell";
import BookingWizard from "@/views/BookingWizard";

export default function Page() {
  return (
    <PublicShell>
      <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="sf-spinner" /></div>}>
        <BookingWizard />
      </Suspense>
    </PublicShell>
  );
}
