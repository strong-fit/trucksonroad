import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, SITE_URL } from "@/lib/seo";
import AboutPage from "@/views/AboutPage";

export const metadata = {
  title: "Über uns – TRUCKSonROAD",
  description: "TRUCKSonROAD steht für einzigartiges Streetfood aus der Schweiz. 6 auffällige Truck-Konzepte für Events, die in Erinnerung bleiben.",
  alternates: {
    canonical: `${SITE_URL}/ueber-uns`,
  },
};

export default function Page() {
  const title = "Über uns – TRUCKSonROAD";
  const description = "TRUCKSonROAD steht für einzigartiges Streetfood aus der Schweiz. 6 auffällige Truck-Konzepte für Events, die in Erinnerung bleiben.";

  return (
    <PublicShell>
      <JsonLdScript
        id="about-page-jsonld"
        data={buildLandingPageSchema({ title, description, url: `${SITE_URL}/ueber-uns`, pageType: "AboutPage" })}
      />
      <JsonLdScript
        id="about-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Über uns", url: `${SITE_URL}/ueber-uns` },
        ])}
      />
      <AboutPage />
    </PublicShell>
  );
}
