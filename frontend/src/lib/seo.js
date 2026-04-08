export const SITE_URL = "https://trucksonroad.ch";

const SUPPORTED_LANGUAGES = ["de", "en", "fr", "it", "es"];

function getBackendUrl() {
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  if (!backendUrl) {
    throw new Error("Missing REACT_APP_BACKEND_URL");
  }

  return backendUrl.replace(/\/$/, "");
}

export async function fetchPublicApi(path, revalidate = 3600) {
  try {
    const response = await fetch(`${getBackendUrl()}/api${path}`, {
      headers: { Accept: "application/json" },
      next: { revalidate },
    });

    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function getLayoutSeoData() {
  const [business, events, verification] = await Promise.all([
    fetchPublicApi("/seo/structured-data"),
    fetchPublicApi("/seo/events-schema"),
    fetchPublicApi("/seo/google-verification"),
  ]);

  return {
    business,
    events: Array.isArray(events) ? events : [],
    verification: verification?.code || "",
  };
}

export function buildWebsiteSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": `${SITE_URL}/#website`,
    url: SITE_URL,
    name: "TRUCKSonROAD",
    description: "Premium Foodtrucks für Events, Firmenanlässe und Festivals in der ganzen Schweiz.",
    inLanguage: SUPPORTED_LANGUAGES,
    publisher: { "@id": `${SITE_URL}/#organization` },
  };
}

export function buildOrganizationSchema(business) {
  if (!business) return null;

  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": `${SITE_URL}/#organization`,
    name: business.name || "TRUCKSonROAD",
    url: SITE_URL,
    email: business.email,
    telephone: business.telephone,
    sameAs: business.sameAs || [],
    address: business.address,
    contactPoint: business.telephone
      ? [
          {
            "@type": "ContactPoint",
            contactType: "sales",
            telephone: business.telephone,
            email: business.email,
            areaServed: "CH",
            availableLanguage: SUPPORTED_LANGUAGES,
          },
        ]
      : undefined,
  };
}

export function buildBreadcrumbSchema(items = []) {
  if (!items.length) return null;

  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

export function buildTruckListSchema(trucks = []) {
  if (!trucks.length) return null;

  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: "TRUCKSonROAD Foodtruck-Flotte",
    url: `${SITE_URL}/trucks`,
    numberOfItems: trucks.length,
    itemListElement: trucks.map((truck, index) => ({
      "@type": "ListItem",
      position: index + 1,
      url: `${SITE_URL}/trucks/${truck.slug}`,
      name: truck.name_de || truck.name_en || truck.slug,
      description: truck.tagline_de || truck.description_de || "",
      image: truck.image,
    })),
  };
}

export function buildTruckDetailSchema(truck) {
  if (!truck) return null;

  const menu = Array.isArray(truck.menu_de) ? truck.menu_de : [];
  const gallery = [truck.image, ...(truck.gallery || [])].filter(Boolean);
  const suitableFor = Array.isArray(truck.suitable_for_de) ? truck.suitable_for_de : [];

  return {
    "@context": "https://schema.org",
    "@type": "FoodEstablishment",
    "@id": `${SITE_URL}/trucks/${truck.slug}#truck`,
    name: truck.name_de || truck.slug,
    description: truck.description_de || truck.tagline_de || "",
    url: `${SITE_URL}/trucks/${truck.slug}`,
    image: gallery,
    additionalType: "https://schema.org/FoodTruck",
    servesCuisine: menu.length ? menu : [truck.name_de || truck.slug],
    areaServed: { "@type": "Country", name: "Switzerland" },
    slogan: truck.tagline_de || "",
    knowsAbout: suitableFor,
    isPartOf: { "@id": `${SITE_URL}/#organization` },
    subjectOf: truck.video_url
      ? {
          "@type": "VideoObject",
          name: `${truck.name_de || truck.slug} Video`,
          contentUrl: truck.video_url,
        }
      : undefined,
  };
}

export function buildFaqSchema(faqs = []) {
  if (!faqs.length) return null;

  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((faq) => ({
      "@type": "Question",
      name: faq.question_de,
      acceptedAnswer: {
        "@type": "Answer",
        text: faq.answer_de,
      },
    })),
  };
}

export function buildLandingPageSchema({
  title,
  description,
  url,
  pageType = "WebPage",
}) {
  return {
    "@context": "https://schema.org",
    "@type": pageType,
    name: title,
    description,
    url,
    isPartOf: { "@id": `${SITE_URL}/#website` },
    about: { "@id": `${SITE_URL}/#organization` },
    inLanguage: SUPPORTED_LANGUAGES,
  };
}

export function buildServiceSchema({
  name,
  description,
  url,
  serviceType,
  audienceType,
}) {
  return {
    "@context": "https://schema.org",
    "@type": "Service",
    name,
    description,
    url,
    serviceType,
    provider: { "@id": `${SITE_URL}/#organization` },
    areaServed: { "@type": "Country", name: "Switzerland" },
    audience: audienceType
      ? {
          "@type": "Audience",
          audienceType,
        }
      : undefined,
    availableChannel: {
      "@type": "ServiceChannel",
      serviceUrl: `${SITE_URL}/anfrage`,
    },
  };
}

export function buildBlogSchema(posts = []) {
  if (!posts.length) return null;

  return {
    "@context": "https://schema.org",
    "@type": "Blog",
    "@id": `${SITE_URL}/blog#blog`,
    name: "TRUCKSonROAD Blog",
    description: "Tipps, Trends und Neuigkeiten rund um Foodtruck-Catering, Events und Streetfood in der Schweiz.",
    url: `${SITE_URL}/blog`,
    publisher: { "@id": `${SITE_URL}/#organization` },
    blogPost: posts.map((post) => ({
      "@type": "BlogPosting",
      headline: post.title_de || post.slug,
      url: `${SITE_URL}/blog/${post.slug}`,
      datePublished: post.created_at,
      image: post.image,
      articleSection: post.category,
      author: {
        "@type": "Person",
        name: post.author || "TRUCKSonROAD Team",
      },
    })),
  };
}

export function buildBlogPostingSchema(post) {
  if (!post) return null;

  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title_de || post.slug,
    description: post.meta_description_de || post.excerpt_de || "",
    image: post.image ? [post.image] : [],
    datePublished: post.created_at,
    dateModified: post.updated_at || post.created_at,
    mainEntityOfPage: `${SITE_URL}/blog/${post.slug}`,
    articleSection: post.category,
    keywords: (post.tags || []).join(", "),
    inLanguage: ["de", "en", "fr", "it"],
    author: {
      "@type": "Person",
      name: post.author || "TRUCKSonROAD Team",
    },
    publisher: { "@id": `${SITE_URL}/#organization` },
  };
}