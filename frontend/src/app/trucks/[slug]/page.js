import PublicShell from "@/components/PublicShell";
import TruckDetailPage from "@/views/TruckDetailPage";

export default async function Page({ params }) {
  const { slug } = await params;
  return (
    <PublicShell>
      <TruckDetailPage slug={slug} />
    </PublicShell>
  );
}
