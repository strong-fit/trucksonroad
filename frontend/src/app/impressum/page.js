import { JsonLdScript } from "@/components/JsonLdScript";
import LegalPageClient from "@/components/LegalPageClient";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, SITE_URL } from "@/lib/seo";

export const metadata = {
  title: "Impressum | TRUCKSonROAD",
  description: "Impressum von TRUCKSonROAD – Anbieterkennzeichnung und rechtliche Hinweise.",
  alternates: { canonical: `${SITE_URL}/impressum` },
};

export default function Page() {
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
      <LegalPageClient docType="impressum" testIdPrefix="impressum" />
    </PublicShell>
  );
}
