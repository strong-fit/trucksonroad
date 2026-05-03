import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, SITE_URL } from "@/lib/seo";
import AgbPage from "@/views/AgbPage";

export const metadata = {
  title: "AGB – Allgemeine Geschäftsbedingungen | TRUCKSonROAD",
  description:
    "Allgemeine Geschäftsbedingungen von TRUCKSonROAD – Foodtruck-Catering und Eventverpflegung in der Schweiz. Buchung, Stornierung, Zahlungsbedingungen.",
  alternates: {
    canonical: `${SITE_URL}/agb`,
  },
};

export default function Page() {
  const title = "AGB – Allgemeine Geschäftsbedingungen | TRUCKSonROAD";
  const description =
    "Allgemeine Geschäftsbedingungen von TRUCKSonROAD – Foodtruck-Catering und Eventverpflegung in der Schweiz.";

  return (
    <PublicShell>
      <JsonLdScript
        id="agb-page-jsonld"
        data={buildLandingPageSchema({ title, description, url: `${SITE_URL}/agb`, pageType: "WebPage" })}
      />
      <JsonLdScript
        id="agb-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "AGB", url: `${SITE_URL}/agb` },
        ])}
      />
      <AgbPage />
    </PublicShell>
  );
}
