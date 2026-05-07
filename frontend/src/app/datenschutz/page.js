import { JsonLdScript } from "@/components/JsonLdScript";
import LegalRenderer from "@/components/LegalRenderer";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Datenschutzerklärung | TRUCKSonROAD",
  description: "DSGVO- und nDSG-konforme Datenschutzerklärung von TRUCKSonROAD.",
  alternates: { canonical: `${SITE_URL}/datenschutz` },
};

export default async function Page() {
  const doc = await fetchPublicApi("/legal/datenschutz", 60);
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
      <LegalRenderer doc={doc} testIdPrefix="datenschutz" />
    </PublicShell>
  );
}
