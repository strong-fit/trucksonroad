import { JsonLdScript } from "@/components/JsonLdScript";
import PublicShell from "@/components/PublicShell";
import { buildBlogPostingSchema, buildBreadcrumbSchema, fetchPublicApi, SITE_URL } from "@/lib/seo";
import BlogPostPage from "@/views/BlogPostPage";

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const post = await fetchPublicApi(`/blog/${slug}`);
  const title = post?.meta_title_de || post?.title_de || "Blog – TRUCKSonROAD";
  const description = post?.meta_description_de || post?.excerpt_de || "Blogartikel von TRUCKSonROAD rund um Foodtruck-Catering und Events in der Schweiz.";

  return {
    title,
    description,
    alternates: {
      canonical: `${SITE_URL}/blog/${slug}`,
    },
    openGraph: {
      title,
      description,
      images: post?.image ? [post.image] : [],
      siteName: "TRUCKSonROAD",
      type: "article",
    },
  };
}

export default async function Page({ params }) {
  const { slug } = await params;
  const post = await fetchPublicApi(`/blog/${slug}`);

  let relatedPosts = [];
  if (post?.category) {
    const relatedData = await fetchPublicApi(`/blog?category=${encodeURIComponent(post.category)}&limit=4`);
    relatedPosts = (relatedData?.posts || []).filter((item) => item.slug !== slug).slice(0, 3);
  }

  if (!relatedPosts.length) {
    const latestData = await fetchPublicApi("/blog?limit=4");
    relatedPosts = (latestData?.posts || []).filter((item) => item.slug !== slug).slice(0, 3);
  }

  return (
    <PublicShell>
      <JsonLdScript id={`blog-post-jsonld-${slug}`} data={buildBlogPostingSchema(post)} />
      <JsonLdScript
        id={`blog-post-breadcrumb-jsonld-${slug}`}
        data={buildBreadcrumbSchema([
          { name: "Startseite", url: SITE_URL },
          { name: "Blog", url: `${SITE_URL}/blog` },
          { name: post?.title_de || slug, url: `${SITE_URL}/blog/${slug}` },
        ])}
      />
      <BlogPostPage slug={slug} initialPost={post} initialRelatedPosts={relatedPosts} />
    </PublicShell>
  );
}
