import { JsonLdScript } from "@/components/JsonLdScript";
import LegalPageClient from "@/components/LegalPageClient";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, SITE_URL } from "@/lib/seo";

export const metadata = {
  title: "Datenschutzerklärung | TRUCKSonROAD",
  description: "DSGVO- und nDSG-konforme Datenschutzerklärung von TRUCKSonROAD.",
  alternates: { canonical: `${SITE_URL}/datenschutz` },
};

export default function Page() {
  const title = "Datenschutzerklärung | TRUCKSonROAD";
  const description = "DSGVO- und nDSG-konforme Datenschutzerklärung von TRUCKSonROAD.";

  return (
    <PublicShell>
      <JsonLdScript
        id="datenschutz-page-jsonld"
        data={buildLandingPageSchema({ title, description, url: `${SITE_URL}/datenschutz`, pageType: "WebPage" })}
      />
      <JsonLdScript
        id="datenschutz-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Datenschutz", url: `${SITE_URL}/datenschutz` },
        ])}
      />
      <LegalPageClient docType="datenschutz" testIdPrefix="datenschutz" />
    </PublicShell>
  );
}
