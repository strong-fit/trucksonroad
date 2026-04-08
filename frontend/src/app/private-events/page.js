import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, buildServiceSchema, SITE_URL } from "@/lib/seo";
import PrivateEventsPage from "@/views/PrivateEventsPage";

export const metadata = {
  title: "Private & Firmen – TRUCKSonROAD",
  description: "Foodtrucks für Hochzeiten, Geburtstage, Firmenfeiern und private Events in der ganzen Schweiz.",
  alternates: {
    canonical: `${SITE_URL}/private-events`,
  },
};

export default function Page() {
  const title = "Private & Firmen – TRUCKSonROAD";
  const description = "Foodtrucks für Hochzeiten, Geburtstage, Firmenfeiern und private Events in der ganzen Schweiz.";

  return (
    <PublicShell>
      <JsonLdScript
        id="private-events-page-jsonld"
        data={buildLandingPageSchema({ title, description, url: `${SITE_URL}/private-events` })}
      />
      <JsonLdScript
        id="private-events-service-jsonld"
        data={buildServiceSchema({
          name: "Foodtruck-Service für private und Firmenevents",
          description,
          url: `${SITE_URL}/private-events`,
          serviceType: "Privat- und Firmen-Catering",
          audienceType: "Privatkunden und Unternehmen",
        })}
      />
      <JsonLdScript
        id="private-events-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Private & Firmen", url: `${SITE_URL}/private-events` },
        ])}
      />
      <PrivateEventsPage />
    </PublicShell>
  );
}
