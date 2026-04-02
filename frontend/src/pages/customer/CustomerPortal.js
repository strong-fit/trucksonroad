import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { LogOut, FileText, Clock, CheckCircle2, Send, XCircle, Receipt, Plus, ChevronDown, ChevronUp, User, Paperclip, Lock } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import { toast } from 'sonner';

export default function CustomerPortal() {
  const { user, logout } = useAuth();
  const { t, lang, setLang, SUPPORTED_LANGS } = useLanguage();
  const navigate = useNavigate();
  const [inquiries, setInquiries] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);
  const [inquiryFiles, setInquiryFiles] = useState({});
  const [showPwChange, setShowPwChange] = useState(false);
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', confirm: '' });
  const [pwLoading, setPwLoading] = useState(false);

  const STATUS_MAP = {
    new: { label: t('status_new'), color: '#5ba4b5', icon: Clock },
    in_progress: { label: t('status_in_progress'), color: '#e8b931', icon: Clock },
    offer_sent: { label: t('status_offer_sent'), color: '#8b5cf6', icon: Send },
    confirmed: { label: t('status_confirmed'), color: '#22c55e', icon: CheckCircle2 },
    completed: { label: t('status_completed'), color: '#6b7280', icon: CheckCircle2 },
    cancelled: { label: t('status_cancelled'), color: '#ef4444', icon: XCircle },
  };

  const INVOICE_MAP = {
    none: { label: t('admin_invoice_none'), color: '#6b7280' },
    pending: { label: t('admin_invoice_pending'), color: '#e8b931' },
    sent: { label: t('admin_invoice_sent'), color: '#8b5cf6' },
    paid: { label: t('admin_invoice_paid'), color: '#22c55e' },
    overdue: { label: t('admin_invoice_overdue'), color: '#ef4444' },
  };

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

  const dateFmt = (d) => d ? new Date(d).toLocaleDateString(lang === 'de' ? 'de-CH' : lang === 'fr' ? 'fr-CH' : lang === 'it' ? 'it-CH' : 'en-GB') : '–';

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (pwForm.new_password !== pwForm.confirm) { toast.error(t('change_mismatch')); return; }
    setPwLoading(true);
    try {
      await api.put('/auth/change-password', { old_password: pwForm.old_password, new_password: pwForm.new_password });
      toast.success(t('change_success'));
      setPwForm({ old_password: '', new_password: '', confirm: '' });
      setShowPwChange(false);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('change_wrong_old'));
    }
    setPwLoading(false);
  };

  return (
    <div className="sf-portal" data-testid="customer-portal">
      <header className="sf-portal-header" data-testid="portal-header">
        <div className="sf-portal-header-inner">
          <Link to="/" className="sf-auth-logo" style={{ textDecoration: 'none' }}>
            <span className="t">TRUCKS</span><span className="on">ON</span><span className="r">ROAD</span>
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <select
              value={lang}
              onChange={async (e) => {
                setLang(e.target.value);
                try { await api.put('/customer/profile', { lang: e.target.value }); } catch {}
              }}
              style={{ background: 'transparent', border: '1px solid var(--sf-border-subtle)', color: 'var(--sf-cream)', padding: '0.25rem 0.5rem', borderRadius: '3px', fontSize: '0.75rem', cursor: 'pointer' }}
              data-testid="portal-lang-select"
            >
              {SUPPORTED_LANGS.map(l => <option key={l} value={l} style={{ background: '#1a1a18' }}>{l.toUpperCase()}</option>)}
            </select>
            <span style={{ color: 'var(--sf-gray)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <User size={14} /> {user?.name || user?.email}
            </span>
            <button onClick={() => setShowPwChange(!showPwChange)} className="sf-portal-logout" style={{ background: 'transparent' }} data-testid="portal-change-pw-btn">
              <Lock size={14} /> {t('change_password')}
            </button>
            <button onClick={handleLogout} className="sf-portal-logout" data-testid="portal-logout-btn">
              <LogOut size={14} /> {t('portal_logout')}
            </button>
          </div>
        </div>
      </header>

      <div className="sf-portal-content">
        <div className="sf-portal-welcome">
          <h1 data-testid="portal-title">{t('portal_title')}</h1>
          <p>{t('portal_subtitle')}</p>
        </div>

        {showPwChange && (
          <div className="sf-portal-section" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--sf-border-subtle)', borderRadius: '8px', padding: '1.5rem', marginBottom: '2rem' }} data-testid="change-password-section">
            <h3 style={{ color: 'var(--sf-cream)', margin: '0 0 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Lock size={18} /> {t('change_password')}</h3>
            <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxWidth: '400px' }}>
              <input type="password" required placeholder={t('change_old')} value={pwForm.old_password} onChange={e => setPwForm({...pwForm, old_password: e.target.value})} className="sf-auth-input" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--sf-border-subtle)', color: 'var(--sf-cream)', padding: '0.6rem 0.8rem', borderRadius: '6px' }} data-testid="change-old-pw" />
              <input type="password" required minLength={6} placeholder={t('change_new')} value={pwForm.new_password} onChange={e => setPwForm({...pwForm, new_password: e.target.value})} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--sf-border-subtle)', color: 'var(--sf-cream)', padding: '0.6rem 0.8rem', borderRadius: '6px' }} data-testid="change-new-pw" />
              <input type="password" required minLength={6} placeholder={t('change_confirm')} value={pwForm.confirm} onChange={e => setPwForm({...pwForm, confirm: e.target.value})} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--sf-border-subtle)', color: 'var(--sf-cream)', padding: '0.6rem 0.8rem', borderRadius: '6px' }} data-testid="change-confirm-pw" />
              <button type="submit" className="sf-auth-btn" style={{ maxWidth: '200px' }} disabled={pwLoading} data-testid="change-pw-submit">{pwLoading ? '...' : t('change_submit')}</button>
            </form>
          </div>
        )}

        <div className="sf-portal-stats" data-testid="portal-stats">
          <div className="sf-portal-stat">
            <div className="sf-portal-stat-num">{inquiries.length}</div>
            <div className="sf-portal-stat-label">{t('portal_total')}</div>
          </div>
          <div className="sf-portal-stat">
            <div className="sf-portal-stat-num">{inquiries.filter(i => i.status === 'confirmed').length}</div>
            <div className="sf-portal-stat-label">{t('portal_confirmed')}</div>
          </div>
          <div className="sf-portal-stat">
            <div className="sf-portal-stat-num">{inquiries.filter(i => i.invoice_status === 'paid').length}</div>
            <div className="sf-portal-stat-label">{t('portal_paid')}</div>
          </div>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <Link to="/anfrage" className="sf-btn-primary" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }} data-testid="new-inquiry-btn">
            <Plus size={16} /> {t('portal_new_inquiry')}
          </Link>
        </div>

        {loading ? (
          <div className="sf-portal-empty">{t('loading')}</div>
        ) : inquiries.length === 0 ? (
          <div className="sf-portal-empty" data-testid="portal-empty">
            <FileText size={40} style={{ opacity: 0.3, marginBottom: '1rem' }} />
            <p>{t('portal_empty')}</p>
            <Link to="/anfrage" className="sf-btn-primary" style={{ marginTop: '1rem', textDecoration: 'none' }}>{t('portal_empty_cta')}</Link>
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
                        {inq.event_type || t('nav_inquiry')} – {inq.location}
                      </div>
                      <div className="sf-portal-inquiry-meta">
                        {inq.event_date} | {inq.guest_count} {t('guests')}
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
                        <div><span className="sf-portal-detail-label">{t('event_date')}</span><span>{inq.event_date}</span></div>
                        <div><span className="sf-portal-detail-label">{t('time')}</span><span>{inq.event_time || '–'}</span></div>
                        <div><span className="sf-portal-detail-label">{t('location')}</span><span>{inq.location}</span></div>
                        <div><span className="sf-portal-detail-label">{t('guests')}</span><span>{inq.guest_count}</span></div>
                        <div><span className="sf-portal-detail-label">{t('event_type')}</span><span>{inq.event_type}</span></div>
                        <div><span className="sf-portal-detail-label">{t('indoor_outdoor')}</span><span>{inq.indoor_outdoor || '–'}</span></div>
                        <div><span className="sf-portal-detail-label">{t('form_budget')}</span><span>{inq.budget || '–'}</span></div>
                        <div><span className="sf-portal-detail-label">{t('status')}</span><span style={{ color: st.color, fontWeight: 600 }}>{st.label}</span></div>
                      </div>
                      {inq.selected_trucks?.length > 0 && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <span className="sf-portal-detail-label">Trucks</span>
                          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.3rem' }}>
                            {inq.selected_trucks.map(tr => (
                              <span key={tr} className="sf-portal-truck-tag">{tr}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {inq.remarks && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <span className="sf-portal-detail-label">{t('remarks')}</span>
                          <p style={{ marginTop: '0.25rem', fontSize: '0.85rem', color: 'var(--sf-cream)', opacity: 0.8 }}>{inq.remarks}</p>
                        </div>
                      )}
                      {inq.invoice_status && inq.invoice_status !== 'none' && (
                        <div className="sf-portal-invoice" style={{ marginTop: '1rem' }}>
                          <div className="sf-portal-detail-label">{t('invoice')}</div>
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
                      {(inquiryFiles[inq.id] || []).length > 0 && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <span className="sf-portal-detail-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                            <Paperclip size={12} /> {t('portal_files')}
                          </span>
                          <div style={{ marginTop: '0.3rem' }}>
                            <FileUpload files={inquiryFiles[inq.id] || []} readOnly />
                          </div>
                        </div>
                      )}
                      <div style={{ marginTop: '0.75rem', fontSize: '0.72rem', color: 'var(--sf-gray)' }}>
                        {t('portal_created')}: {dateFmt(inq.created_at)} | {t('portal_updated')}: {dateFmt(inq.updated_at)}
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
