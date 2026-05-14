import { Suspense } from "react";
import CustomerLogin from "@/views/customer/CustomerLogin";

export const dynamic = "force-dynamic";

export default function Page() {
  return (
    <Suspense fallback={null}>
      <CustomerLogin />
    </Suspense>
  );
}
