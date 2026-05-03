import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, SITE_URL } from "@/lib/seo";
import ImpressumPage from "@/views/ImpressumPage";

export const metadata = {
  title: "Impressum | TRUCKSonROAD",
  description:
    "Impressum von TRUCKSonROAD – Anbieterkennzeichnung, Kontakt und rechtliche Hinweise.",
  alternates: {
    canonical: `${SITE_URL}/impressum`,
  },
};

export default function Page() {
  const title = "Impressum | TRUCKSonROAD";
  const description = "Impressum von TRUCKSonROAD – Anbieterkennzeichnung, Kontakt und rechtliche Hinweise.";

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
      <ImpressumPage />
    </PublicShell>
  );
}
