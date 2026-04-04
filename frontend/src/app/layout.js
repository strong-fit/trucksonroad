import Providers from "@/components/Providers";
import "@/App.css";

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

export default function RootLayout({ children }) {
  return (
    <html lang="de">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "FoodEstablishment",
              name: "TRUCKSonROAD GmbH",
              alternateName: "TRUCKSonROAD - Einzigartige Foodtrucks für Events",
              description: "Einzigartige Foodtrucks für Events, die in Erinnerung bleiben. Firmenanlässe, Hochzeiten, Festivals und private Feiern in der ganzen Schweiz.",
              url: "https://trucksonroad.ch",
              telephone: "+41 79 696 98 99",
              address: {
                "@type": "PostalAddress",
                streetAddress: "Bahnhofstrasse 75",
                addressLocality: "Wetzikon",
                postalCode: "8620",
                addressCountry: "CH",
              },
              geo: { "@type": "GeoCoordinates", latitude: 47.3236, longitude: 8.7976 },
              servesCuisine: ["Burger", "Bowls", "Empanadas", "Streetfood"],
              priceRange: "$$",
              areaServed: { "@type": "Country", name: "Switzerland" },
            }),
          }}
        />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
