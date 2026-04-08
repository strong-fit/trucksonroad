import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBreadcrumbSchema, buildTruckDetailSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";
import TruckDetailPage from "@/views/TruckDetailPage";

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const truck = await fetchPublicApi(`/trucks/${slug}`);
  const truckName = truck?.name_de || truck?.name_en || "Foodtruck";
  const truckDescription = truck?.description_de || truck?.tagline_de || "Foodtruck-Konzept von TRUCKSonROAD für Premium Events in der Schweiz.";

  return {
    title: `${truckName} – TRUCKSonROAD`,
    description: truckDescription,
    alternates: {
      canonical: `${SITE_URL}/trucks/${slug}`,
    },
    openGraph: {
      title: `${truckName} – TRUCKSonROAD`,
      description: truckDescription,
      images: truck?.image ? [truck.image] : [],
    },
  };
}

export default async function Page({ params }) {
  const { slug } = await params;
  const truck = await fetchPublicApi(`/trucks/${slug}`);

  return (
    <PublicShell>
      <JsonLdScript id={`truck-detail-jsonld-${slug}`} data={buildTruckDetailSchema(truck)} />
      <JsonLdScript
        id={`truck-breadcrumb-jsonld-${slug}`}
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Foodtrucks", url: `${SITE_URL}/trucks` },
          { name: truck?.name_de || slug, url: `${SITE_URL}/trucks/${slug}` },
        ])}
      />
      <TruckDetailPage slug={slug} initialTruck={truck} />
    </PublicShell>
  );
}
