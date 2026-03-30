import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider, ProtectedRoute } from "@/contexts/AuthContext";
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
import "@/App.css";

function PublicLayout({ children }) {
  return (
    <>
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
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
            <Route path="/admin/anfragen" element={<ProtectedRoute><AdminInquiries /></ProtectedRoute>} />
            <Route path="/admin/kalender" element={<ProtectedRoute><AdminCalendar /></ProtectedRoute>} />
          </Routes>
        </BrowserRouter>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
