"use client";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function PublicShell({ children }) {
  return (
    <>
      <Navbar />
      <main>{children}</main>
      <Footer />
    </>
  );
}
