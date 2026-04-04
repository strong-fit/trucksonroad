import PublicShell from "@/components/PublicShell";
import AboutPage from "@/views/AboutPage";

export const metadata = {
  title: "Über uns – TRUCKSonROAD",
  description: "TRUCKSonROAD steht für einzigartiges Streetfood aus der Schweiz. 6 auffällige Truck-Konzepte für Events, die in Erinnerung bleiben.",
};

export default function Page() {
  return <PublicShell><AboutPage /></PublicShell>;
}
