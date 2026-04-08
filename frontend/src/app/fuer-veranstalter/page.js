import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, buildServiceSchema, SITE_URL } from "@/lib/seo";
import EventOrganizerPage from "@/views/EventOrganizersPage";

export const metadata = {
  title: "Für Veranstalter – TRUCKSonROAD",
  description: "Informationen für Veranstalter: Foodtruck-Konzepte, Logistik und Zusammenarbeit mit TRUCKSonROAD.",
  alternates: {
    canonical: `${SITE_URL}/fuer-veranstalter`,
  },
};

export default function Page() {
  const title = "Für Veranstalter – TRUCKSonROAD";
  const description = "Informationen für Veranstalter: Foodtruck-Konzepte, Logistik und Zusammenarbeit mit TRUCKSonROAD.";

  return (
    <PublicShell>
      <JsonLdScript
        id="organizers-page-jsonld"
        data={buildLandingPageSchema({ title, description, url: `${SITE_URL}/fuer-veranstalter` })}
      />
      <JsonLdScript
        id="organizers-service-jsonld"
        data={buildServiceSchema({
          name: "Foodtruck-Service für Veranstalter",
          description,
          url: `${SITE_URL}/fuer-veranstalter`,
          serviceType: "Festival- und Event-Catering",
          audienceType: "Veranstalter",
        })}
      />
      <JsonLdScript
        id="organizers-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Für Veranstalter", url: `${SITE_URL}/fuer-veranstalter` },
        ])}
      />
      <EventOrganizerPage />
    </PublicShell>
  );
}
