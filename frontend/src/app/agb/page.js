import { JsonLdScript } from "@/components/JsonLdScript";
import LegalRenderer from "@/components/LegalRenderer";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "AGB – Allgemeine Geschäftsbedingungen | TRUCKSonROAD",
  description:
    "Allgemeine Geschäftsbedingungen von TRUCKSonROAD – Foodtruck-Catering und Eventverpflegung in der Schweiz.",
  alternates: { canonical: `${SITE_URL}/agb` },
};

export default async function Page() {
  const doc = await fetchPublicApi("/legal/agb", 60);
  const title = "AGB – Allgemeine Geschäftsbedingungen | TRUCKSonROAD";
  const description = "Allgemeine Geschäftsbedingungen von TRUCKSonROAD – Foodtruck-Catering und Eventverpflegung.";

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
      <LegalRenderer doc={doc} testIdPrefix="agb" />
    </PublicShell>
  );
}
