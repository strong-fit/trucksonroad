import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { LayoutDashboard, FileText, CalendarDays, Truck, LogOut } from 'lucide-react';

function AdminLayout({ children, title }) {
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    { to: '/admin', icon: <LayoutDashboard size={18} />, label: 'Dashboard' },
    { to: '/admin/anfragen', icon: <FileText size={18} />, label: 'Anfragen' },
    { to: '/admin/kalender', icon: <CalendarDays size={18} />, label: 'Kalender' },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/admin/login');
  };

  return (
    <div className="sf-admin" data-testid="admin-layout">
      <aside className="sf-admin-sidebar">
        <div className="sf-admin-sidebar-logo">
          <span className="sf-logo-text">STRONG</span>
          <span className="sf-logo-accent">FOOD</span>
        </div>
        {navItems.map(item => (
          <Link key={item.to} to={item.to} className={`sf-admin-nav-link ${location.pathname === item.to ? 'active' : ''}`} data-testid={`admin-nav-${item.label.toLowerCase()}`}>
            {item.icon} {item.label}
          </Link>
        ))}
        <div style={{ flex: 1 }} />
        <button className="sf-admin-nav-link" onClick={handleLogout} data-testid="admin-logout-btn">
          <LogOut size={18} /> Abmelden
        </button>
        <Link to="/" className="sf-admin-nav-link" style={{ borderTop: '1px solid var(--sf-border)', marginTop: '0.5rem', paddingTop: '1rem' }}>
          <Truck size={18} /> Zur Webseite
        </Link>
      </aside>
      <main className="sf-admin-main">
        <div className="sf-admin-header">
          <h1 className="sf-admin-title">{title}</h1>
        </div>
        {children}
      </main>
    </div>
  );
}

export { AdminLayout };

export default function AdminDashboard() {
  const [stats, setStats] = useState({ total_inquiries: 0, new_inquiries: 0, confirmed: 0, total_trucks: 0 });
  const [recentInquiries, setRecentInquiries] = useState([]);

  useEffect(() => {
    api.get('/admin/stats').then(r => setStats(r.data)).catch(() => {});
    api.get('/admin/inquiries').then(r => setRecentInquiries(r.data.slice(0, 5))).catch(() => {});
  }, []);

  const statusMap = { new: 'Neu', in_review: 'In Pr\u00fcfung', offer_sent: 'Offerte', confirmed: 'Best\u00e4tigt', cancelled: 'Abgesagt' };

  return (
    <AdminLayout title="Dashboard">
      <div className="sf-stats-grid" data-testid="admin-stats">
        <div className="sf-stat-card">
          <div className="sf-stat-card-label">Anfragen Gesamt</div>
          <div className="sf-stat-card-num" data-testid="stat-total">{stats.total_inquiries}</div>
        </div>
        <div className="sf-stat-card">
          <div className="sf-stat-card-label">Neue Anfragen</div>
          <div className="sf-stat-card-num" data-testid="stat-new">{stats.new_inquiries}</div>
        </div>
        <div className="sf-stat-card">
          <div className="sf-stat-card-label">Best\u00e4tigt</div>
          <div className="sf-stat-card-num" data-testid="stat-confirmed">{stats.confirmed}</div>
        </div>
        <div className="sf-stat-card">
          <div className="sf-stat-card-label">Aktive Trucks</div>
          <div className="sf-stat-card-num" data-testid="stat-trucks">{stats.total_trucks}</div>
        </div>
      </div>

      <h3 style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, marginBottom: '1rem' }}>Letzte Anfragen</h3>
      {recentInquiries.length === 0 ? (
        <p style={{ color: 'var(--sf-gray)' }}>Noch keine Anfragen vorhanden.</p>
      ) : (
        <table className="sf-admin-table" data-testid="recent-inquiries-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Datum</th>
              <th>Event</th>
              <th>G\u00e4ste</th>
              <th>Status</th>
              <th>Erstellt</th>
            </tr>
          </thead>
          <tbody>
            {recentInquiries.map(inq => (
              <tr key={inq.id} data-testid={`inquiry-row-${inq.id}`}>
                <td>{inq.first_name || inq.name || ''} {inq.last_name || ''}</td>
                <td>{inq.event_date || '-'}</td>
                <td>{inq.event_type || inq.concept || '-'}</td>
                <td>{inq.guest_count || '-'}</td>
                <td><span className={`sf-status-badge sf-status-${inq.status}`}>{statusMap[inq.status] || inq.status}</span></td>
                <td>{inq.created_at ? new Date(inq.created_at).toLocaleDateString('de-CH') : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </AdminLayout>
  );
}
