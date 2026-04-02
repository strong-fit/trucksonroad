import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Search, Save, Send, Trash2, ExternalLink, Globe, Mail, Sparkles, ChevronDown, ChevronUp, X } from 'lucide-react';

const STATUS_COLORS = {
  new: { bg: '#5ba4b520', color: '#5ba4b5', border: '#5ba4b540' },
  contacted: { bg: '#e8b93120', color: '#e8b931', border: '#e8b93140' },
  confirmed: { bg: '#22c55e20', color: '#22c55e', border: '#22c55e40' },
  rejected: { bg: '#ef444420', color: '#ef4444', border: '#ef444440' },
};

export default function AdminEventScout() {
  const { t } = useLanguage();
  const [query, setQuery] = useState('');
  const [region, setRegion] = useState('Schweiz');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [citations, setCitations] = useState([]);
  const [savedEvents, setSavedEvents] = useState([]);
  const [tab, setTab] = useState('search');
  const [applyModal, setApplyModal] = useState(null);
  const [applyEmail, setApplyEmail] = useState('');
  const [applyMessage, setApplyMessage] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => { loadSaved(); }, []);

  const loadSaved = () => api.get('/admin/event-scout/events').then(r => setSavedEvents(r.data)).catch(() => {});

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setResults([]);
    setCitations([]);
    try {
      const r = await api.post('/admin/event-scout/search', { query, region });
      setResults(r.data.events || []);
      setCitations(r.data.citations || []);
      if ((r.data.events || []).length === 0) toast.info(t('scout_no_results'));
    } catch (err) {
      const msg = err?.response?.data?.detail || t('admin_error');
      toast.error(msg);
    }
    setSearching(false);
  };

  const saveEvent = async (ev) => {
    try {
      await api.post('/admin/event-scout/events', { ...ev, source: 'perplexity' });
      toast.success(t('scout_saved_msg'));
      loadSaved();
    } catch { toast.error(t('admin_error')); }
  };

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/admin/event-scout/events/${id}`, { status });
      loadSaved();
    } catch { toast.error(t('admin_error')); }
  };

  const deleteEvent = async (id) => {
    if (!window.confirm(t('admin_delete_confirm'))) return;
    try {
      await api.delete(`/admin/event-scout/events/${id}`);
      toast.success(t('admin_deleted'));
      loadSaved();
    } catch { toast.error(t('admin_error')); }
  };

  const openApply = (ev) => {
    setApplyModal(ev);
    setApplyEmail(ev.organizer_email || '');
    setApplyMessage('');
  };

  const sendApplication = async () => {
    if (!applyEmail) { toast.error(t('scout_email_label')); return; }
    setSending(true);
    try {
      await api.post(`/admin/event-scout/events/${applyModal.id}/apply`, { email: applyEmail, message: applyMessage });
      toast.success(t('scout_apply_msg'));
      setApplyModal(null);
      loadSaved();
    } catch (err) {
      toast.error(err?.response?.data?.detail || t('admin_error'));
    }
    setSending(false);
  };

  const statusLabel = (s) => t(`scout_status_${s}`) || s;

  const REGIONS = ['Schweiz', 'Zürich', 'Bern', 'Basel', 'Luzern', 'St. Gallen', 'Aargau', 'Graubünden', 'Tessin', 'Wallis', 'Genf', 'Waadt'];

  return (
    <AdminLayout title={t('admin_event_scout')}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }} data-testid="scout-title">
          <Sparkles size={18} style={{ color: 'var(--adm-accent)' }} /> {t('scout_title')}
        </h2>
        <p style={{ color: 'var(--adm-text-muted)', fontSize: '0.82rem', marginTop: '0.25rem' }}>{t('scout_subtitle')}</p>
      </div>

      <div className="adm-filters" style={{ marginBottom: '1rem' }}>
        <button className={`adm-filter-btn ${tab === 'search' ? 'active' : ''}`} onClick={() => setTab('search')} data-testid="tab-search">
          <Search size={13} /> {t('scout_search')}
        </button>
        <button className={`adm-filter-btn ${tab === 'saved' ? 'active' : ''}`} onClick={() => setTab('saved')} data-testid="tab-saved">
          <Save size={13} /> {t('scout_saved')} ({savedEvents.length})
        </button>
      </div>

      {tab === 'search' && (
        <div>
          <div className="adm-detail" style={{ marginBottom: '1.25rem' }} data-testid="scout-search-form">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 180px auto', gap: '0.75rem', alignItems: 'end' }}>
              <div>
                <div className="adm-form-label">{t('scout_query')}</div>
                <input
                  className="adm-input"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder={t('scout_query_placeholder')}
                  onKeyDown={e => e.key === 'Enter' && handleSearch()}
                  data-testid="scout-query-input"
                />
              </div>
              <div>
                <div className="adm-form-label">{t('scout_region')}</div>
                <select className="adm-input" value={region} onChange={e => setRegion(e.target.value)} data-testid="scout-region-select">
                  {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <button
                className="adm-btn adm-btn-primary"
                onClick={handleSearch}
                disabled={searching || !query.trim()}
                style={{ height: '38px' }}
                data-testid="scout-search-btn"
              >
                {searching ? <><Sparkles size={14} className="spin" /> {t('scout_searching')}</> : <><Search size={14} /> {t('scout_search')}</>}
              </button>
            </div>
          </div>

          {results.length > 0 && (
            <div data-testid="scout-results">
              <div className="adm-table-header" style={{ marginBottom: '0.75rem' }}>
                <span className="adm-table-title">{t('scout_results')} ({results.length})</span>
              </div>
              <div style={{ display: 'grid', gap: '0.75rem' }}>
                {results.map((ev, i) => (
                  <div key={i} className="adm-detail" style={{ padding: '1rem' }} data-testid={`result-${i}`}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.25rem' }}>{ev.name}</div>
                        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.78rem', color: 'var(--adm-text-muted)', marginBottom: '0.4rem', flexWrap: 'wrap' }}>
                          {ev.date && <span>{ev.date}</span>}
                          {ev.location && <span>| {ev.location}</span>}
                          {ev.type && <span className="adm-badge adm-badge-new" style={{ fontSize: '0.68rem' }}><span className="adm-badge-dot" />{ev.type}</span>}
                        </div>
                        {ev.description && <p style={{ fontSize: '0.8rem', color: 'var(--adm-text-secondary)', margin: '0.25rem 0 0', lineHeight: 1.5 }}>{ev.description}</p>}
                        {ev.website && (
                          <a href={ev.website} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.2rem', marginTop: '0.35rem' }}>
                            <Globe size={11} /> Website
                          </a>
                        )}
                      </div>
                      <button
                        className="adm-btn adm-btn-primary adm-btn-sm"
                        onClick={() => saveEvent(ev)}
                        data-testid={`save-result-${i}`}
                        style={{ whiteSpace: 'nowrap' }}
                      >
                        <Save size={13} /> {t('scout_save')}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {citations.length > 0 && (
                <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'var(--adm-bg-card)', border: '1px solid var(--adm-border)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--adm-text-muted)', marginBottom: '0.4rem' }}>{t('scout_sources')}</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                    {citations.map((c, i) => (
                      <a key={i} href={c} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.72rem', color: 'var(--adm-accent)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <ExternalLink size={10} /> {typeof c === 'string' ? c : c.url || c}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {searching && (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--adm-text-muted)' }}>
              <Sparkles size={24} className="spin" style={{ marginBottom: '0.5rem' }} />
              <div>{t('scout_searching')}</div>
            </div>
          )}
        </div>
      )}

      {tab === 'saved' && (
        <div data-testid="scout-saved-events">
          {savedEvents.length === 0 ? (
            <div className="adm-empty" data-testid="no-saved-events">
              <div className="adm-empty-icon"><Search size={22} /></div>
              {t('scout_no_saved')}
            </div>
          ) : (
            <div className="adm-table-wrap">
              <table className="adm-table" data-testid="saved-events-table">
                <thead>
                  <tr>
                    <th>{t('admin_name')}</th>
                    <th>{t('admin_date')}</th>
                    <th>{t('location')}</th>
                    <th>{t('event_type')}</th>
                    <th>{t('status')}</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {savedEvents.map(ev => {
                    const sc = STATUS_COLORS[ev.status] || STATUS_COLORS.new;
                    return (
                      <tr key={ev.id} data-testid={`saved-event-${ev.id}`}>
                        <td style={{ fontWeight: 500 }}>
                          <div>{ev.name}</div>
                          {ev.website && (
                            <a href={ev.website} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                              <Globe size={10} /> Link
                            </a>
                          )}
                        </td>
                        <td style={{ fontSize: '0.78rem' }}>{ev.date || '–'}</td>
                        <td style={{ fontSize: '0.78rem' }}>{ev.location || '–'}</td>
                        <td><span className="adm-badge adm-badge-new" style={{ fontSize: '0.68rem' }}><span className="adm-badge-dot" />{ev.type}</span></td>
                        <td>
                          <select
                            value={ev.status}
                            onChange={e => updateStatus(ev.id, e.target.value)}
                            className="adm-input"
                            style={{ fontSize: '0.75rem', padding: '0.2rem 0.4rem', background: sc.bg, color: sc.color, border: `1px solid ${sc.border}`, borderRadius: '4px', fontWeight: 600 }}
                            data-testid={`status-select-${ev.id}`}
                          >
                            <option value="new">{t('scout_status_new')}</option>
                            <option value="contacted">{t('scout_status_contacted')}</option>
                            <option value="confirmed">{t('scout_status_confirmed')}</option>
                            <option value="rejected">{t('scout_status_rejected')}</option>
                          </select>
                        </td>
                        <td>
                          <div style={{ display: 'flex', gap: '0.3rem' }}>
                            <button className="adm-btn adm-btn-primary adm-btn-sm" onClick={() => openApply(ev)} data-testid={`apply-btn-${ev.id}`} title={t('scout_apply')}>
                              <Mail size={13} />
                            </button>
                            <button className="adm-btn adm-btn-danger adm-btn-sm" onClick={() => deleteEvent(ev.id)} data-testid={`delete-btn-${ev.id}`}>
                              <Trash2 size={13} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {applyModal && (
        <div className="adm-modal-overlay" onClick={() => setApplyModal(null)} data-testid="apply-modal">
          <div className="adm-modal" onClick={e => e.stopPropagation()}>
            <div className="adm-modal-header">
              <span style={{ fontWeight: 600 }}>{t('scout_apply')}: {applyModal.name}</span>
              <button onClick={() => setApplyModal(null)} className="adm-detail-close"><X size={16} /></button>
            </div>
            <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div>
                <div className="adm-form-label">{t('scout_email_label')} *</div>
                <input className="adm-input" type="email" value={applyEmail} onChange={e => setApplyEmail(e.target.value)} placeholder="veranstalter@event.ch" data-testid="apply-email-input" />
              </div>
              <div>
                <div className="adm-form-label">{t('scout_message_label')}</div>
                <textarea className="adm-textarea" rows={4} value={applyMessage} onChange={e => setApplyMessage(e.target.value)} placeholder="Optionale persönliche Nachricht..." data-testid="apply-message-input" />
              </div>
              <button
                className="adm-btn adm-btn-primary"
                onClick={sendApplication}
                disabled={sending || !applyEmail}
                data-testid="send-apply-btn"
              >
                <Send size={14} /> {sending ? '...' : t('scout_apply')}
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}
