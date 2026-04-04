import PublicShell from "@/components/PublicShell";
import ContactPage from "@/views/ContactPage";

export const metadata = {
  title: "Kontakt – TRUCKSonROAD GmbH",
  description: "Kontaktiere TRUCKSonROAD für dein nächstes Event. Bahnhofstrasse 75, 8620 Wetzikon. +41 79 696 98 99.",
};

export default function Page() {
  return <PublicShell><ContactPage /></PublicShell>;
}
