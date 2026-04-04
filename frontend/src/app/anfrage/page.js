import PublicShell from "@/components/PublicShell";
import InquiryPage from "@/views/InquiryPage";

export const metadata = {
  title: "Jetzt anfragen – TRUCKSonROAD",
  description: "Individuelle Foodtruck-Anfrage für dein Event. Kostenlos und unverbindlich – Angebot innerhalb von 24h.",
};

export default function Page() {
  return <PublicShell><InquiryPage /></PublicShell>;
}
