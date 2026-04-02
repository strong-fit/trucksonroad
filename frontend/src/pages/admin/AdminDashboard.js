import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import {
  LayoutDashboard, FileText, CalendarDays, Truck, LogOut,
  Search, Menu, X, ExternalLink, Inbox, CheckCircle2, Clock,
  Settings, HelpCircle, Users, Download, DollarSign, MapPin, Star, Sparkles
} from 'lucide-react';

function AdminLayout({ children, title }) {
  const { logout } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { to: '/admin', icon: LayoutDashboard, label: t('admin_dashboard') },
    { to: '/admin/anfragen', icon: FileText, label: t('admin_inquiries') },
    { to: '/admin/kalender', icon: CalendarDays, label: t('admin_calendar') },
    { to: '/admin/trucks', icon: Truck, label: t('admin_trucks') },
    { to: '/admin/personal', icon: Users, label: t('admin_employees') },
    { to: '/admin/finanzen', icon: DollarSign, label: t('admin_finance') },
    { to: '/admin/routen', icon: MapPin, label: t('admin_routes') },
    { to: '/admin/bewertungen', icon: Star, label: t('admin_reviews') },
    { to: '/admin/event-scout', icon: Sparkles, label: t('admin_event_scout') },
    { to: '/admin/faqs', icon: HelpCircle, label: t('admin_faqs') },
    { to: '/admin/export', icon: Download, label: t('admin_export') },
    { to: '/admin/einstellungen', icon: Settings, label: t('admin_settings') },
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
            <span className="t">TRUCKS</span>
            <span className="on">ON</span>
            <span className="r">ROAD</span>
          </span>
          <span className="adm-sidebar-badge">Admin</span>
        </div>
        <nav className="adm-nav">
          <div className="adm-nav-section">
            <div className="adm-nav-section-label">{t('admin_navigation')}</div>
            {navItems.map(item => (
              <Link
                key={item.to}
                to={item.to}
                className={`adm-nav-link ${location.pathname === item.to ? 'active' : ''}`}
                data-testid={`admin-nav-${item.to.split('/').pop()}`}
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
            <ExternalLink size={16} className="adm-nav-icon" /> {t('admin_go_website')}
          </Link>
          <button className="adm-nav-link" onClick={handleLogout} data-testid="admin-logout-btn">
            <LogOut size={16} className="adm-nav-icon" /> {t('admin_logout')}
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
              <input type="text" placeholder={`${t('admin_search')}...`} />
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
  const { t, lang } = useLanguage();
  const [stats, setStats] = useState({ total_inquiries: 0, new_inquiries: 0, confirmed: 0, total_trucks: 0 });
  const [recentInquiries, setRecentInquiries] = useState([]);

  useEffect(() => {
    api.get('/admin/stats').then(r => setStats(r.data)).catch(() => {});
    api.get('/admin/inquiries').then(r => setRecentInquiries(r.data.slice(0, 5))).catch(() => {});
  }, []);

  const statusLabels = {
    new: t('status_new'), in_review: t('status_in_review'), offer_sent: t('status_offer_sent'),
    confirmed: t('status_confirmed'), cancelled: t('status_cancelled'), completed: t('status_completed'),
  };
  const dateFmt = (d) => d ? new Date(d).toLocaleDateString(lang === 'de' ? 'de-CH' : lang === 'fr' ? 'fr-CH' : lang === 'it' ? 'it-CH' : 'en-GB') : '–';

  return (
    <AdminLayout title={t('admin_dashboard')}>
      <div className="adm-stats" data-testid="admin-stats">
        <div className="adm-stat-card" data-testid="stat-card-total">
          <div className="adm-stat-label">{t('admin_total_inquiries')}</div>
          <div className="adm-stat-row">
            <div className="adm-stat-num" data-testid="stat-total">{stats.total_inquiries}</div>
            <div className="adm-stat-icon gold"><Inbox size={18} /></div>
          </div>
        </div>
        <div className="adm-stat-card" data-testid="stat-card-new">
          <div className="adm-stat-label">{t('admin_new_inquiries')}</div>
          <div className="adm-stat-row">
            <div className="adm-stat-num" data-testid="stat-new">{stats.new_inquiries}</div>
            <div className="adm-stat-icon blue"><Clock size={18} /></div>
          </div>
        </div>
        <div className="adm-stat-card" data-testid="stat-card-confirmed">
          <div className="adm-stat-label">{t('admin_confirmed_inquiries')}</div>
          <div className="adm-stat-row">
            <div className="adm-stat-num" data-testid="stat-confirmed">{stats.confirmed}</div>
            <div className="adm-stat-icon green"><CheckCircle2 size={18} /></div>
          </div>
        </div>
        <div className="adm-stat-card" data-testid="stat-card-trucks">
          <div className="adm-stat-label">{t('admin_active_trucks')}</div>
          <div className="adm-stat-row">
            <div className="adm-stat-num" data-testid="stat-trucks">{stats.total_trucks}</div>
            <div className="adm-stat-icon purple"><Truck size={18} /></div>
          </div>
        </div>
      </div>

      <div className="adm-table-wrap" data-testid="recent-inquiries-section">
        <div className="adm-table-header">
          <span className="adm-table-title">{t('admin_recent')}</span>
          <Link to="/admin/anfragen" className="adm-btn adm-btn-secondary adm-btn-sm" data-testid="view-all-inquiries-link">
            {t('admin_show_all')}
          </Link>
        </div>
        {recentInquiries.length === 0 ? (
          <div className="adm-empty" data-testid="no-inquiries-msg">
            <div className="adm-empty-icon"><Inbox size={22} /></div>
            {t('admin_no_inquiries')}
          </div>
        ) : (
          <table className="adm-table" data-testid="recent-inquiries-table">
            <thead>
              <tr>
                <th>{t('admin_name')}</th>
                <th>{t('admin_date')}</th>
                <th>{t('admin_event')}</th>
                <th>{t('admin_guests')}</th>
                <th>{t('status')}</th>
                <th>{t('admin_created_at')}</th>
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
                      {statusLabels[inq.status] || inq.status}
                    </span>
                  </td>
                  <td style={{ color: 'var(--adm-text-muted)' }}>{dateFmt(inq.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </AdminLayout>
  );
}
