import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { LogOut, FileText, Clock, CheckCircle2, Send, XCircle, Receipt, Plus, ChevronDown, ChevronUp, User, Paperclip } from 'lucide-react';
import FileUpload from '@/components/FileUpload';

const STATUS_MAP = {
  new: { label: 'Neu', color: '#5ba4b5', icon: Clock },
  in_progress: { label: 'In Bearbeitung', color: '#e8b931', icon: Clock },
  offer_sent: { label: 'Angebot gesendet', color: '#8b5cf6', icon: Send },
  confirmed: { label: 'Bestätigt', color: '#22c55e', icon: CheckCircle2 },
  completed: { label: 'Abgeschlossen', color: '#6b7280', icon: CheckCircle2 },
  cancelled: { label: 'Storniert', color: '#ef4444', icon: XCircle },
};

const INVOICE_MAP = {
  none: { label: 'Keine Rechnung', color: '#6b7280' },
  pending: { label: 'Offen', color: '#e8b931' },
  sent: { label: 'Gesendet', color: '#8b5cf6' },
  paid: { label: 'Bezahlt', color: '#22c55e' },
  overdue: { label: 'Überfällig', color: '#ef4444' },
};

export default function CustomerPortal() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [inquiries, setInquiries] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);
  const [inquiryFiles, setInquiryFiles] = useState({});

  useEffect(() => {
    api.get('/customer/inquiries').then(r => { setInquiries(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const toggleExpand = (id) => {
    const newId = expanded === id ? null : id;
    setExpanded(newId);
    if (newId && !inquiryFiles[newId]) {
      api.get(`/inquiries/${newId}/files`).then(r => setInquiryFiles(prev => ({ ...prev, [newId]: r.data }))).catch(() => {});
    }
  };

  return (
    <div className="sf-portal" data-testid="customer-portal">
      {/* Header */}
      <header className="sf-portal-header" data-testid="portal-header">
        <div className="sf-portal-header-inner">
          <Link to="/" className="sf-auth-logo" style={{ textDecoration: 'none' }}>
            <span className="t">TRUCK</span><span className="on">ON</span><span className="r">ROAD</span>
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ color: 'var(--sf-gray)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <User size={14} /> {user?.name || user?.email}
            </span>
            <button onClick={handleLogout} className="sf-portal-logout" data-testid="portal-logout-btn">
              <LogOut size={14} /> Abmelden
            </button>
          </div>
        </div>
      </header>

      <div className="sf-portal-content">
        <div className="sf-portal-welcome">
          <h1 data-testid="portal-title">Mein Kundenportal</h1>
          <p>Hier siehst du alle deine Anfragen, den aktuellen Status und Rechnungen.</p>
        </div>

        {/* Stats */}
        <div className="sf-portal-stats" data-testid="portal-stats">
          <div className="sf-portal-stat">
            <div className="sf-portal-stat-num">{inquiries.length}</div>
            <div className="sf-portal-stat-label">Anfragen</div>
          </div>
          <div className="sf-portal-stat">
            <div className="sf-portal-stat-num">{inquiries.filter(i => i.status === 'confirmed').length}</div>
            <div className="sf-portal-stat-label">Bestätigt</div>
          </div>
          <div className="sf-portal-stat">
            <div className="sf-portal-stat-num">{inquiries.filter(i => i.invoice_status === 'paid').length}</div>
            <div className="sf-portal-stat-label">Bezahlt</div>
          </div>
        </div>

        {/* New Inquiry CTA */}
        <div style={{ marginBottom: '1.5rem' }}>
          <Link to="/anfrage" className="sf-btn-primary" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }} data-testid="new-inquiry-btn">
            <Plus size={16} /> Neue Anfrage erstellen
          </Link>
        </div>

        {/* Inquiries List */}
        {loading ? (
          <div className="sf-portal-empty">Laden...</div>
        ) : inquiries.length === 0 ? (
          <div className="sf-portal-empty" data-testid="portal-empty">
            <FileText size={40} style={{ opacity: 0.3, marginBottom: '1rem' }} />
            <p>Noch keine Anfragen vorhanden.</p>
            <Link to="/anfrage" className="sf-btn-primary" style={{ marginTop: '1rem', textDecoration: 'none' }}>Jetzt Anfrage stellen</Link>
          </div>
        ) : (
          <div className="sf-portal-inquiries" data-testid="portal-inquiries">
            {inquiries.map(inq => {
              const st = STATUS_MAP[inq.status] || STATUS_MAP.new;
              const inv = INVOICE_MAP[inq.invoice_status] || INVOICE_MAP.none;
              const isOpen = expanded === inq.id;
              const StIcon = st.icon;
              return (
                <div key={inq.id} className={`sf-portal-inquiry ${isOpen ? 'expanded' : ''}`} data-testid={`inquiry-${inq.id}`}>
                  <div className="sf-portal-inquiry-header" onClick={() => toggleExpand(inq.id)}>
                    <div className="sf-portal-inquiry-main">
                      <div className="sf-portal-inquiry-title">
                        {inq.event_type || 'Anfrage'} – {inq.location}
                      </div>
                      <div className="sf-portal-inquiry-meta">
                        {inq.event_date} | {inq.guest_count} Gäste
                        {inq.selected_trucks?.length > 0 && ` | ${inq.selected_trucks.join(', ')}`}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span className="sf-portal-badge" style={{ background: `${st.color}20`, color: st.color, border: `1px solid ${st.color}40` }}>
                        <StIcon size={12} /> {st.label}
                      </span>
                      {inq.invoice_status && inq.invoice_status !== 'none' && (
                        <span className="sf-portal-badge" style={{ background: `${inv.color}20`, color: inv.color, border: `1px solid ${inv.color}40` }}>
                          <Receipt size={12} /> {inv.label}
                          {inq.invoice_amount > 0 && ` CHF ${inq.invoice_amount.toLocaleString()}`}
                        </span>
                      )}
                      {isOpen ? <ChevronUp size={16} style={{ color: 'var(--sf-gray)' }} /> : <ChevronDown size={16} style={{ color: 'var(--sf-gray)' }} />}
                    </div>
                  </div>
                  {isOpen && (
                    <div className="sf-portal-inquiry-detail">
                      <div className="sf-portal-detail-grid">
                        <div><span className="sf-portal-detail-label">Event-Datum</span><span>{inq.event_date}</span></div>
                        <div><span className="sf-portal-detail-label">Uhrzeit</span><span>{inq.event_time || '–'}</span></div>
                        <div><span className="sf-portal-detail-label">Ort</span><span>{inq.location}</span></div>
                        <div><span className="sf-portal-detail-label">Gäste</span><span>{inq.guest_count}</span></div>
                        <div><span className="sf-portal-detail-label">Event-Typ</span><span>{inq.event_type}</span></div>
                        <div><span className="sf-portal-detail-label">Indoor/Outdoor</span><span>{inq.indoor_outdoor || '–'}</span></div>
                        <div><span className="sf-portal-detail-label">Budget</span><span>{inq.budget || '–'}</span></div>
                        <div><span className="sf-portal-detail-label">Status</span><span style={{ color: st.color, fontWeight: 600 }}>{st.label}</span></div>
                      </div>
                      {inq.selected_trucks?.length > 0 && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <span className="sf-portal-detail-label">Trucks</span>
                          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.3rem' }}>
                            {inq.selected_trucks.map(t => (
                              <span key={t} className="sf-portal-truck-tag">{t}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {inq.remarks && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <span className="sf-portal-detail-label">Bemerkungen</span>
                          <p style={{ marginTop: '0.25rem', fontSize: '0.85rem', color: 'var(--sf-cream)', opacity: 0.8 }}>{inq.remarks}</p>
                        </div>
                      )}
                      {/* Invoice Section */}
                      {inq.invoice_status && inq.invoice_status !== 'none' && (
                        <div className="sf-portal-invoice" style={{ marginTop: '1rem' }}>
                          <div className="sf-portal-detail-label">Rechnung</div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.3rem' }}>
                            <span className="sf-portal-badge" style={{ background: `${inv.color}20`, color: inv.color, border: `1px solid ${inv.color}40` }}>
                              <Receipt size={12} /> {inv.label}
                            </span>
                            {inq.invoice_amount > 0 && (
                              <span style={{ fontWeight: 600, color: 'var(--sf-cream)' }}>CHF {inq.invoice_amount.toLocaleString()}</span>
                            )}
                          </div>
                        </div>
                      )}
                      {/* Files */}
                      {(inquiryFiles[inq.id] || []).length > 0 && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <span className="sf-portal-detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                            <Paperclip size={12} /> Dateien
                          </span>
                          <div style={{ marginTop: '0.3rem' }}>
                            <FileUpload files={inquiryFiles[inq.id] || []} readOnly />
                          </div>
                        </div>
                      )}
                      <div style={{ marginTop: '0.75rem', fontSize: '0.72rem', color: 'var(--sf-gray)' }}>
                        Erstellt: {new Date(inq.created_at).toLocaleDateString('de-CH')} | Aktualisiert: {new Date(inq.updated_at).toLocaleDateString('de-CH')}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
