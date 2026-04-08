import Providers from "@/components/Providers";
import { JsonLdScript } from "@/components/JsonLdScript";
import "@/index.css";
import "@/App.css";
import { buildOrganizationSchema, buildWebsiteSchema, getLayoutSeoData } from "@/lib/seo";

export const metadata = {
  title: "TRUCKSonROAD – Einzigartige Foodtrucks für Events, die in Erinnerung bleiben",
  description: "Auffällige Trucks, einzigartiges Essen, professionelle Organisation. Für Firmenevents, Hochzeiten und Festivals in der ganzen Schweiz.",
  metadataBase: new URL("https://trucksonroad.ch"),
  openGraph: {
    title: "TRUCKSonROAD – Einzigartige Foodtrucks für Events",
    description: "Auffällige Trucks, einzigartiges Essen, professionelle Organisation. Individuelles Angebot in 24h.",
    siteName: "TRUCKSonROAD",
    type: "website",
  },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
};

export default async function RootLayout({ children }) {
  const { business, events, verification } = await getLayoutSeoData();
  const seoScripts = [business, buildOrganizationSchema(business), buildWebsiteSchema(), ...events].filter(Boolean);

  return (
    <html lang="de">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet" />
        {verification ? <meta name="google-site-verification" content={verification} /> : null}
        {seoScripts.map((script, index) => (
          <JsonLdScript key={`layout-jsonld-${index}`} id={`layout-jsonld-${index}`} data={script} />
        ))}
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
