import PublicShell from "@/components/PublicShell";
import TrucksListPage from "@/views/TrucksListPage";

export const metadata = {
  title: "Unsere Foodtrucks – TRUCKSonROAD",
  description: "Entdecke unsere 6 einzigartigen Foodtruck-Konzepte: Burger, Bowls, Empanadas, Pocket Bowls und mehr. Premium Streetfood für dein Event in der ganzen Schweiz.",
  openGraph: {
    title: "Unsere Foodtrucks – TRUCKSonROAD",
    description: "6 einzigartige Foodtruck-Konzepte für Firmenevents, Hochzeiten und Festivals.",
    siteName: "TRUCKSonROAD",
  },
};

export default function Page() {
  return (
    <PublicShell>
      <TrucksListPage />
    </PublicShell>
  );
}
