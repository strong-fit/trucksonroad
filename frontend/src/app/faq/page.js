import PublicShell from "@/components/PublicShell";
import FAQPage from "@/views/FAQPage";

export const metadata = {
  title: "FAQ – Häufige Fragen | TRUCKSonROAD",
  description: "Häufig gestellte Fragen zu TRUCKSonROAD Foodtruck-Catering. Preise, Buchung, Ablauf und mehr.",
};

export default function Page() {
  return <PublicShell><FAQPage /></PublicShell>;
}
