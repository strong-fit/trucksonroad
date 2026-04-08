import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildFaqSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";
import FAQPage from "@/views/FAQPage";

export const metadata = {
  title: "FAQ – Häufige Fragen | TRUCKSonROAD",
  description: "Häufig gestellte Fragen zu TRUCKSonROAD Foodtruck-Catering. Preise, Buchung, Ablauf und mehr.",
  alternates: {
    canonical: `${SITE_URL}/faq`,
  },
};

export default async function Page() {
  const faqs = (await fetchPublicApi("/faqs")) || [];

  return (
    <PublicShell>
      <JsonLdScript id="faq-jsonld" data={buildFaqSchema(faqs)} />
      <JsonLdScript
        id="faq-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "FAQ", url: `${SITE_URL}/faq` },
        ])}
      />
      <FAQPage initialFaqs={faqs} />
    </PublicShell>
  );
}
