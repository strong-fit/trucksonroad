import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBlogSchema, buildBreadcrumbSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";
import BlogPage from "@/views/BlogPage";

export const metadata = {
  title: "Blog – TRUCKSonROAD",
  description: "Tipps, Trends und Neuigkeiten rund um Foodtruck-Catering, Events und Streetfood in der Schweiz.",
  alternates: {
    canonical: `${SITE_URL}/blog`,
  },
};

export default async function Page() {
  const blogData = await fetchPublicApi("/blog?limit=20");
  const posts = blogData?.posts || [];
  const categories = blogData?.categories || {};

  return (
    <PublicShell>
      <JsonLdScript id="blog-jsonld" data={buildBlogSchema(posts)} />
      <JsonLdScript
        id="blog-breadcrumb-jsonld"
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Blog", url: `${SITE_URL}/blog` },
        ])}
      />
      <BlogPage initialPosts={posts} initialCategories={categories} />
    </PublicShell>
  );
}
