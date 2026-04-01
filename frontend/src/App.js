import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider, ProtectedRoute, CustomerProtectedRoute } from "@/contexts/AuthContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { Toaster } from "sonner";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import HomePage from "@/pages/HomePage";
import TruckDetailPage from "@/pages/TruckDetailPage";
import InquiryPage from "@/pages/InquiryPage";
import FAQPage from "@/pages/FAQPage";
import EventOrganizersPage from "@/pages/EventOrganizersPage";
import PrivateEventsPage from "@/pages/PrivateEventsPage";
import AdminLogin from "@/pages/admin/AdminLogin";
import AdminDashboard from "@/pages/admin/AdminDashboard";
import AdminInquiries from "@/pages/admin/AdminInquiries";
import AdminCalendar from "@/pages/admin/AdminCalendar";
import AdminSettings from "@/pages/admin/AdminSettings";
import AdminTrucks from "@/pages/admin/AdminTrucks";
import AdminFAQs from "@/pages/admin/AdminFAQs";
import AdminEmployees from "@/pages/admin/AdminEmployees";
import AdminExport from "@/pages/admin/AdminExport";
import AdminFinance from "@/pages/admin/AdminFinance";
import AdminRoutes from "@/pages/admin/AdminRoutes";
import AdminReviews from "@/pages/admin/AdminReviews";
import CustomerLogin from "@/pages/customer/CustomerLogin";
import CustomerRegister from "@/pages/customer/CustomerRegister";
import CustomerPortal from "@/pages/customer/CustomerPortal";
import AboutPage from "@/pages/AboutPage";
import ContactPage from "@/pages/ContactPage";
import "@/App.css";
import SeoJsonLd from "@/components/SeoJsonLd";

function PublicLayout({ children }) {
  return (
    <>
      <SeoJsonLd />
      <Navbar />
      {children}
      <Footer />
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <BrowserRouter>
          <Toaster position="top-right" theme="dark" richColors />
          <Routes>
            <Route path="/" element={<PublicLayout><HomePage /></PublicLayout>} />
            <Route path="/trucks/:slug" element={<PublicLayout><TruckDetailPage /></PublicLayout>} />
            <Route path="/anfrage" element={<PublicLayout><InquiryPage /></PublicLayout>} />
            <Route path="/faq" element={<PublicLayout><FAQPage /></PublicLayout>} />
            <Route path="/fuer-veranstalter" element={<PublicLayout><EventOrganizersPage /></PublicLayout>} />
            <Route path="/private-events" element={<PublicLayout><PrivateEventsPage /></PublicLayout>} />
            <Route path="/ueber-uns" element={<PublicLayout><AboutPage /></PublicLayout>} />
            <Route path="/kontakt" element={<PublicLayout><ContactPage /></PublicLayout>} />
            <Route path="/konto/login" element={<PublicLayout><CustomerLogin /></PublicLayout>} />
            <Route path="/konto/registrieren" element={<PublicLayout><CustomerRegister /></PublicLayout>} />
            <Route path="/konto" element={<CustomerProtectedRoute><CustomerPortal /></CustomerProtectedRoute>} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
            <Route path="/admin/anfragen" element={<ProtectedRoute><AdminInquiries /></ProtectedRoute>} />
            <Route path="/admin/kalender" element={<ProtectedRoute><AdminCalendar /></ProtectedRoute>} />
            <Route path="/admin/einstellungen" element={<ProtectedRoute><AdminSettings /></ProtectedRoute>} />
            <Route path="/admin/trucks" element={<ProtectedRoute><AdminTrucks /></ProtectedRoute>} />
            <Route path="/admin/faqs" element={<ProtectedRoute><AdminFAQs /></ProtectedRoute>} />
            <Route path="/admin/personal" element={<ProtectedRoute><AdminEmployees /></ProtectedRoute>} />
            <Route path="/admin/export" element={<ProtectedRoute><AdminExport /></ProtectedRoute>} />
            <Route path="/admin/finanzen" element={<ProtectedRoute><AdminFinance /></ProtectedRoute>} />
            <Route path="/admin/routen" element={<ProtectedRoute><AdminRoutes /></ProtectedRoute>} />
            <Route path="/admin/bewertungen" element={<ProtectedRoute><AdminReviews /></ProtectedRoute>} />
          </Routes>
        </BrowserRouter>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
