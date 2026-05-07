import AdminLegalEditor from "@/views/admin/AdminLegalEditor";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

const VALID_TYPES = new Set(["agb", "datenschutz", "impressum"]);

export default async function Page({ params }) {
  const { type } = await params;
  if (!VALID_TYPES.has(type)) notFound();
  return <AdminLegalEditor docType={type} />;
}
