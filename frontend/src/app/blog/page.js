import PublicShell from "@/components/PublicShell";
import BlogPage from "@/views/BlogPage";

export const metadata = {
  title: "Blog – TRUCKSonROAD",
  description: "Tipps, Trends und Neuigkeiten rund um Foodtruck-Catering, Events und Streetfood in der Schweiz.",
};

export default function Page() {
  return <PublicShell><BlogPage /></PublicShell>;
}
