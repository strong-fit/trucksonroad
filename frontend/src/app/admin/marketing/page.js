"use client";
import dynamic from "next/dynamic";
const AdminMarketing = dynamic(() => import("@/views/admin/AdminMarketing"), { ssr: false });
export default function Page() {
  return <AdminMarketing />;
}
