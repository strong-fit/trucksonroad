"use client";
import dynamic from "next/dynamic";

const AdminRoutes = dynamic(() => import("@/views/admin/AdminRoutes"), { ssr: false });

export default function Page() { return <AdminRoutes />; }
