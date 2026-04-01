import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import {
  LayoutDashboard, FileText, CalendarDays, Truck, LogOut,
  Search, Menu, X, ExternalLink, Inbox, CheckCircle2, Clock,
  Settings, HelpCircle, Users, Download, DollarSign, MapPin
} from 'lucide-react';

function AdminLayout({ children, title }) {
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { to: '/admin', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/admin/anfragen', icon: FileText, label: 'Anfragen' },
    { to: '/admin/kalender', icon: CalendarDays, label: 'Kalender' },
    { to: '/admin/trucks', icon: Truck, label: 'Trucks' },
    { to: '/admin/personal', icon: Users, label: 'Personal' },
    { to: '/admin/finanzen', icon: DollarSign, label: 'Finanzen' },
    { to: '/admin/routen', icon: MapPin, label: 'Routen' },
    { to: '/admin/faqs', icon: HelpCircle, label: 'FAQ' },
    { to: '/admin/export', icon: Download, label: 'Export' },
    { to: '/admin/einstellungen', icon: Settings, label: 'Einstellungen' },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/admin/login');
  };

  return (
    <div className="adm" data-testid="admin-layout">
      <div className={`adm-overlay ${sidebarOpen ? 'open' : ''}`} onClick={() => setSidebarOpen(false)} />
      <aside className={`adm-sidebar ${sidebarOpen ? 'open' : ''}`} data-testid="admin-sidebar">
        <div className="adm-sidebar-logo">
          <span className="adm-sidebar-logo-text">
            <span className="t">TRUCK</span>
            <span className="on">ON</span>
            <span className="r">ROAD</span>
          </span>
          <span className="adm-sidebar-badge">Admin</span>
        </div>
        <nav className="adm-nav">
          <div className="adm-nav-section">
            <div className="adm-nav-section-label">Navigation</div>
            {navItems.map(item => (
              <Link
                key={item.to}
                to={item.to}
                className={`adm-nav-link ${location.pathname === item.to ? 'active' : ''}`}
                data-testid={`admin-nav-${item.label.toLowerCase()}`}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon size={18} className="adm-nav-icon" />
                {item.label}
              </Link>
            ))}
          </div>
        </nav>
        <div className="adm-sidebar-footer">
          <Link to="/" className="adm-nav-link" data-testid="admin-nav-website" onClick={() => setSidebarOpen(false)}>
            <ExternalLink size={16} className="adm-nav-icon" /> Zur Webseite
          </Link>
          <button className="adm-nav-link" onClick={handleLogout} data-testid="admin-logout-btn">
            <LogOut size={16} className="adm-nav-icon" /> Abmelden
          </button>
        </div>
      </aside>

      <div className="adm-main">
        <header className="adm-topbar" data-testid="admin-topbar">
          <div className="adm-topbar-left">
            <button className="adm-mobile-toggle" onClick={() => setSidebarOpen(!sidebarOpen)} data-testid="admin-mobile-toggle">
              {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
            <h1 className="adm-topbar-title">{title}</h1>
          </div>
          <div className="adm-topbar-right">
            <div className="adm-search" data-testid="admin-search">
              <Search size={14} />
              <input type="text" placeholder="Suchen..." />
            </div>
            <div className="adm-user-pill" data-testid="admin-user-pill">
              <div className="adm-user-avatar">TR</div>
              <span>Admin</span>
            </div>
          </div>
        </header>
        <div className="adm-content">
          {children}
        </div>
      </div>
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

  const statusMap = { new: 'Neu', in_review: 'In Pruefung', offer_sent: 'Offerte', confirmed: 'Bestaetigt', cancelled: 'Abgesagt' };

  return (
    <AdminLayout title="Dashboard">
      <div className="adm-stats" data-testid="admin-stats">
        <div className="adm-stat-card" data-testid="stat-card-total">
          <div className="adm-stat-label">Anfragen Gesamt</div>
          <div className="adm-stat-row">
            <div className="adm-stat-num" data-testid="stat-total">{stats.total_inquiries}</div>
            <div className="adm-stat-icon gold"><Inbox size={18} /></div>
          </div>
        </div>
        <div className="adm-stat-card" data-testid="stat-card-new">
          <div className="adm-stat-label">Neue Anfragen</div>
          <div className="adm-stat-row">
            <div className="adm-stat-num" data-testid="stat-new">{stats.new_inquiries}</div>
            <div className="adm-stat-icon blue"><Clock size={18} /></div>
          </div>
        </div>
        <div className="adm-stat-card" data-testid="stat-card-confirmed">
          <div className="adm-stat-label">Bestaetigt</div>
          <div className="adm-stat-row">
            <div className="adm-stat-num" data-testid="stat-confirmed">{stats.confirmed}</div>
            <div className="adm-stat-icon green"><CheckCircle2 size={18} /></div>
          </div>
        </div>
        <div className="adm-stat-card" data-testid="stat-card-trucks">
          <div className="adm-stat-label">Aktive Trucks</div>
          <div className="adm-stat-row">
            <div className="adm-stat-num" data-testid="stat-trucks">{stats.total_trucks}</div>
            <div className="adm-stat-icon purple"><Truck size={18} /></div>
          </div>
        </div>
      </div>

      <div className="adm-table-wrap" data-testid="recent-inquiries-section">
        <div className="adm-table-header">
          <span className="adm-table-title">Letzte Anfragen</span>
          <Link to="/admin/anfragen" className="adm-btn adm-btn-secondary adm-btn-sm" data-testid="view-all-inquiries-link">
            Alle anzeigen
          </Link>
        </div>
        {recentInquiries.length === 0 ? (
          <div className="adm-empty" data-testid="no-inquiries-msg">
            <div className="adm-empty-icon"><Inbox size={22} /></div>
            Noch keine Anfragen vorhanden.
          </div>
        ) : (
          <table className="adm-table" data-testid="recent-inquiries-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Datum</th>
                <th>Event</th>
                <th>Gaeste</th>
                <th>Status</th>
                <th>Erstellt</th>
              </tr>
            </thead>
            <tbody>
              {recentInquiries.map(inq => (
                <tr key={inq.id} data-testid={`inquiry-row-${inq.id}`}>
                  <td style={{ fontWeight: 500 }}>{inq.first_name || inq.name || ''} {inq.last_name || ''}</td>
                  <td>{inq.event_date || '-'}</td>
                  <td>{inq.event_type || inq.concept || '-'}</td>
                  <td>{inq.guest_count || '-'}</td>
                  <td>
                    <span className={`adm-badge adm-badge-${inq.status}`}>
                      <span className="adm-badge-dot" />
                      {statusMap[inq.status] || inq.status}
                    </span>
                  </td>
                  <td style={{ color: 'var(--adm-text-muted)' }}>{inq.created_at ? new Date(inq.created_at).toLocaleDateString('de-CH') : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </AdminLayout>
  );
}
