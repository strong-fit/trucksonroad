import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildLandingPageSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";
import ContactPage from "@/views/ContactPage";

export const metadata = {
  title: "Kontakt – TRUCKSonROAD GmbH",
  description: "Kontaktiere TRUCKSonROAD für dein nächstes Event. Bahnhofstrasse 75, 8620 Wetzikon. +41 79 696 98 99.",
  alternates: {
    canonical: `${SITE_URL}/kontakt`,
  },
};

export default async function Page() {
  const info = await fetchPublicApi("/contact-info");
  const title = "Kontakt – TRUCKSonROAD GmbH";
  const description = "Kontaktiere TRUCKSonROAD für dein nächstes Event. Bahnhofstrasse 75, 8620 Wetzikon. +41 79 696 98 99.";

  return (
    <PublicShell>
      <JsonLdScript
        id="contact-page-jsonld"
        data={buildLandingPageSchema({ title, description, url: `${SITE_URL}/kontakt`, pageType: "ContactPage" })}
      />
      <JsonLdScript
        id="contact-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Kontakt", url: `${SITE_URL}/kontakt` },
        ])}
      />
      <ContactPage initialInfo={info} />
    </PublicShell>
  );
}
