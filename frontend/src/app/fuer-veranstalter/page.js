import PublicShell from "@/components/PublicShell";
import EventOrganizerPage from "@/views/EventOrganizersPage";

export const metadata = {
  title: "Für Veranstalter – TRUCKSonROAD",
  description: "Informationen für Veranstalter: Foodtruck-Konzepte, Logistik und Zusammenarbeit mit TRUCKSonROAD.",
};

export default function Page() { return <PublicShell><EventOrganizerPage /></PublicShell>; }
