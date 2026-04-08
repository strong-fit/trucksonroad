import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildTruckListSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";
import TrucksListPage from "@/views/TrucksListPage";

export const metadata = {
  title: "Unsere Foodtrucks – TRUCKSonROAD",
  description: "Entdecke unsere 6 einzigartigen Foodtruck-Konzepte: Burger, Bowls, Empanadas, Pocket Bowls und mehr. Premium Streetfood für dein Event in der ganzen Schweiz.",
  alternates: {
    canonical: `${SITE_URL}/trucks`,
  },
  openGraph: {
    title: "Unsere Foodtrucks – TRUCKSonROAD",
    description: "6 einzigartige Foodtruck-Konzepte für Firmenevents, Hochzeiten und Festivals.",
    siteName: "TRUCKSonROAD",
  },
};

export default async function Page() {
  const trucks = (await fetchPublicApi("/trucks")) || [];

  return (
    <PublicShell>
      <JsonLdScript id="trucks-list-jsonld" data={buildTruckListSchema(trucks)} />
      <JsonLdScript
        id="trucks-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Foodtrucks", url: `${SITE_URL}/trucks` },
        ])}
      />
      <TrucksListPage initialTrucks={trucks} />
    </PublicShell>
  );
}
