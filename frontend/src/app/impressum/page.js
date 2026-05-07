import { JsonLdScript } from "@/components/JsonLdScript";
import LegalRenderer from "@/components/LegalRenderer";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Impressum | TRUCKSonROAD",
  description: "Impressum von TRUCKSonROAD – Anbieterkennzeichnung und rechtliche Hinweise.",
  alternates: { canonical: `${SITE_URL}/impressum` },
};

export default async function Page() {
  const doc = await fetchPublicApi("/legal/impressum", 60);
  const title = "Impressum | TRUCKSonROAD";
  const description = "Impressum von TRUCKSonROAD – Anbieterkennzeichnung und rechtliche Hinweise.";

  return (
    <PublicShell>
      <JsonLdScript
        id="impressum-page-jsonld"
        data={buildLandingPageSchema({ title, description, url: `${SITE_URL}/impressum`, pageType: "WebPage" })}
      />
      <JsonLdScript
        id="impressum-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Impressum", url: `${SITE_URL}/impressum` },
        ])}
      />
      <LegalRenderer doc={doc} testIdPrefix="impressum" />
    </PublicShell>
  );
}
