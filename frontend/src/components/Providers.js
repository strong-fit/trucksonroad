"use client";
import { AuthProvider } from "@/contexts/AuthContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { Toaster } from "sonner";

export default function Providers({ children }) {
  return (
    <AuthProvider>
      <LanguageProvider>
        <Toaster position="top-right" theme="dark" richColors />
        {children}
      </LanguageProvider>
    </AuthProvider>
  );
}
