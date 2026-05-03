import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, SITE_URL } from "@/lib/seo";
import DatenschutzPage from "@/views/DatenschutzPage";

export const metadata = {
  title: "Datenschutzerklärung | TRUCKSonROAD",
  description:
    "Datenschutzerklärung von TRUCKSonROAD – DSGVO- und nDSG-konform. Informationen zur Verarbeitung Ihrer personenbezogenen Daten.",
  alternates: {
    canonical: `${SITE_URL}/datenschutz`,
  },
};

export default function Page() {
  const title = "Datenschutzerklärung | TRUCKSonROAD";
  const description =
    "Datenschutzerklärung von TRUCKSonROAD – DSGVO- und nDSG-konform. Informationen zur Verarbeitung Ihrer personenbezogenen Daten.";

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
      <DatenschutzPage />
    </PublicShell>
  );
}
