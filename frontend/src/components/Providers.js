"use client";
import { AuthProvider } from "@/contexts/AuthContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { CookieConsentProvider } from "@/contexts/CookieConsentContext";
import CookieBanner from "@/components/CookieBanner";
import { Toaster } from "sonner";

export default function Providers({ children }) {
  return (
    <AuthProvider>
      <LanguageProvider>
        <CookieConsentProvider>
          <Toaster position="top-right" theme="dark" richColors />
          {children}
          <CookieBanner />
        </CookieConsentProvider>
      </LanguageProvider>
    </AuthProvider>
  );
}
