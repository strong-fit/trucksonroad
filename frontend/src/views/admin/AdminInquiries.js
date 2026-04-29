"use client";
import { useState, useEffect } from 'react';
import { AdminLayout } from '@/views/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Trash2, Inbox, FileDown, Users, Receipt, Paperclip, Send, X, CheckCircle2 } from 'lucide-react';
import FileUpload from '@/components/FileUpload';

export default function AdminInquiries() {
  const { t, lang } = useLanguage();
  const [inquiries, setInquiries] = useState([]);
  const [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState(null);
  const [notes, setNotes] = useState('');
  const [employees, setEmployees] = useState([]);
  const [assignedEmps, setAssignedEmps] = useState([]);
  const [inquiryFiles, setInquiryFiles] = useState([]);
  const [offerDialog, setOfferDialog] = useState(null);

  const STATUS_OPTIONS = [
    { value: 'new', label: t('status_new') },
    { value: 'in_review', label: t('status_in_review') },
    { value: 'offer_sent', label: t('status_offer_sent') },
    { value: 'confirmed', label: t('status_confirmed') },
    { value: 'completed', label: t('status_completed') },
    { value: 'cancelled', label: t('status_cancelled') },
  ];

  const INVOICE_OPTIONS = [
    { value: 'none', label: t('admin_invoice_none') },
    { value: 'pending', label: t('admin_invoice_pending') },
    { value: 'sent', label: t('admin_invoice_sent') },
    { value: 'paid', label: t('admin_invoice_paid') },
    { value: 'overdue', label: t('admin_invoice_overdue') },
  ];

  const load = () => api.get('/admin/inquiries').then(r => setInquiries(r.data)).catch(() => {});
  useEffect(() => {
    load();
    api.get('/admin/employees').then(r => setEmployees(r.data)).catch(() => {});
  }, []);

  const filtered = filter === 'all' ? inquiries : inquiries.filter(i => i.status === filter);

  const updateStatus = async (id, status) => {
    if (status === 'offer_sent' && selected) {
      setOfferDialog({ id, amount: selected.invoice_amount || 0 });
      return;
    }
    try {
      await api.put(`/admin/inquiries/${id}`, { status, internal_notes: notes, assigned_employees: assignedEmps });
      toast.success(status === 'offer_sent' ? t('admin_offer_sent_msg') : t('admin_status_update'));
      load();
      if (selected?.id === id) setSelected(prev => ({ ...prev, status, assigned_employees: assignedEmps }));
    } catch { toast.error(t('admin_update_error')); }
  };

  const sendOffer = async () => {
    if (!offerDialog) return;
    try {
      if (offerDialog.amount > 0) {
        await api.put(`/admin/inquiries/${offerDialog.id}/invoice`, { invoice_amount: offerDialog.amount });
      }
      await api.put(`/admin/inquiries/${offerDialog.id}`, { status: 'offer_sent', internal_notes: notes, assigned_employees: assignedEmps });
      toast.success(t('admin_offer_sent_msg'));
      load();
      if (selected?.id === offerDialog.id) setSelected(prev => ({ ...prev, status: 'offer_sent', invoice_amount: offerDialog.amount }));
      setOfferDialog(null);
    } catch { toast.error(t('admin_update_error')); }
  };

  const deleteInquiry = async (id) => {
    if (!window.confirm(t('admin_delete_confirm'))) return;
    try {
      await api.delete(`/admin/inquiries/${id}`);
      toast.success(t('admin_deleted'));
      load();
      if (selected?.id === id) setSelected(null);
    } catch { toast.error(t('admin_error')); }
  };

  const dateFmt = (d) => d ? new Date(d).toLocaleString(lang === 'de' ? 'de-CH' : lang === 'fr' ? 'fr-CH' : lang === 'it' ? 'it-CH' : 'en-GB') : '–';

  return (
    <AdminLayout title={t('admin_inquiries')}>
      <div className="adm-filters" data-testid="inquiry-filters">
        <button className={`adm-filter-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')} data-testid="filter-all">
          {t('admin_total')} ({inquiries.length})
        </button>
        {STATUS_OPTIONS.map(s => {
          const count = inquiries.filter(i => i.status === s.value).length;
          return (
            <button key={s.value} className={`adm-filter-btn ${filter === s.value ? 'active' : ''}`} onClick={() => setFilter(s.value)} data-testid={`filter-${s.value}`}>
              {s.label} ({count})
            </button>
          );
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 380px' : '1fr', gap: '1.25rem', alignItems: 'start' }}>
        <div className="adm-table-wrap" data-testid="inquiries-table-wrap">
          {filtered.length === 0 ? (
            <div className="adm-empty" data-testid="no-inquiries-msg">
              <div className="adm-empty-icon"><Inbox size={22} /></div>
              {t('admin_no_inquiries')}
            </div>
          ) : (
            <table className="adm-table" data-testid="inquiries-table">
              <thead>
                <tr>
                  <th>{t('admin_name')}</th>
                  <th>{t('admin_date')}</th>
                  <th>{t('event_type')}</th>
                  <th>{t('admin_guests')}</th>
                  <th>{t('status')}</th>
                  <th>{t('invoice')}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(inq => (
                  <tr
                    key={inq.id}
                    className={selected?.id === inq.id ? 'selected' : ''}
                    onClick={() => { setSelected(inq); setNotes(inq.internal_notes || ''); setAssignedEmps(inq.assigned_employees || []); api.get(`/inquiries/${inq.id}/files`).then(r => setInquiryFiles(r.data)).catch(() => setInquiryFiles([])); }}
                    data-testid={`inquiry-row-${inq.id}`}
                  >
                    <td style={{ fontWeight: 500 }}>{inq.first_name || inq.name || ''} {inq.last_name || ''}</td>
                    <td>{inq.event_date || '-'}</td>
                    <td style={{ fontSize: '0.78rem' }}>{inq.event_type || inq.concept || '-'}</td>
                    <td>{inq.guest_count || '-'}</td>
                    <td>
                      <span className={`adm-badge adm-badge-${inq.status}`}>
                        <span className="adm-badge-dot" />
                        {STATUS_OPTIONS.find(s => s.value === inq.status)?.label || inq.status}
                      </span>
                    </td>
                    <td>
                      {inq.invoice_status && inq.invoice_status !== 'none' && (
                        <span className={`adm-badge adm-badge-${inq.invoice_status === 'paid' ? 'confirmed' : inq.invoice_status === 'overdue' ? 'cancelled' : 'new'}`}>
                          <span className="adm-badge-dot" />
                          {INVOICE_OPTIONS.find(o => o.value === inq.invoice_status)?.label || '–'}
                          {inq.invoice_amount > 0 && ` CHF ${inq.invoice_amount}`}
                        </span>
                      )}
                    </td>
                    <td>
                      <button
                        className="adm-btn adm-btn-danger adm-btn-sm"
                        onClick={(e) => { e.stopPropagation(); deleteInquiry(inq.id); }}
                        data-testid={`delete-inquiry-${inq.id}`}
                        style={{ padding: '0.25rem 0.4rem' }}
                      >
                        <Trash2 size={13} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {selected && (
          <div className="adm-detail" data-testid="inquiry-detail">
            <div className="adm-detail-header">
              <span className="adm-detail-title">{t('admin_inquiries')} – {t('admin_edit')}</span>
              <button className="adm-detail-close" onClick={() => setSelected(null)} data-testid="close-detail-btn">&times;</button>
            </div>
            <div className="adm-detail-grid">
              <div>
                <div className="label">{t('admin_name')}</div>
                <div className="value">{selected.first_name || selected.name || ''} {selected.last_name || ''}</div>
              </div>
              {selected.company && <div><div className="label">{t('auth_company')}</div><div className="value">{selected.company}</div></div>}
              <div><div className="label">{t('auth_email')}</div><div className="value">{selected.email || '-'}</div></div>
              <div><div className="label">{t('auth_phone')}</div><div className="value">{selected.phone || '-'}</div></div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                <div><div className="label">{t('admin_date')}</div><div className="value">{selected.event_date || '-'}</div></div>
                <div><div className="label">{t('time')}</div><div className="value">{selected.event_time || '-'}</div></div>
              </div>
              <div><div className="label">{t('location')}</div><div className="value">{selected.location || '-'}</div></div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                <div><div className="label">{t('admin_guests')}</div><div className="value">{selected.guest_count || '-'}</div></div>
                <div><div className="label">{t('indoor_outdoor')}</div><div className="value">{selected.indoor_outdoor || '-'}</div></div>
              </div>
              <div><div className="label">{t('event_type')}</div><div className="value">{selected.event_type || selected.concept || '-'}</div></div>
              {selected.selected_trucks?.length > 0 && <div><div className="label">Trucks</div><div className="value">{selected.selected_trucks.join(', ')}</div></div>}
              {selected.extras?.length > 0 && <div><div className="label">Extras</div><div className="value">{selected.extras.join(', ')}</div></div>}
              {selected.budget && <div><div className="label">{t('form_budget')}</div><div className="value">{selected.budget}</div></div>}
              {selected.remarks && <div><div className="label">{t('remarks')}</div><div className="value">{selected.remarks}</div></div>}
              <div><div className="label">{t('admin_created_at')}</div><div className="value" style={{ color: 'var(--adm-text-muted)' }}>{dateFmt(selected.created_at)}</div></div>
            </div>

            <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="adm-form-label" style={{ margin: 0 }}>E-Mail-Sprache:</div>
              <select
                className="adm-input"
                value={selected.lang || 'de'}
                onChange={async (e) => {
                  try {
                    await api.put(`/admin/inquiries/${selected.id}/lang`, { lang: e.target.value });
                    setSelected(prev => ({ ...prev, lang: e.target.value }));
                    load();
                    toast.success(t('admin_status_update'));
                  } catch { toast.error(t('admin_error')); }
                }}
                style={{ width: 'auto', fontSize: '0.78rem', padding: '0.25rem 0.5rem' }}
                data-testid="inquiry-lang-select"
              >
                <option value="de">DE</option>
                <option value="en">EN</option>
                <option value="fr">FR</option>
                <option value="it">IT</option>
              </select>
            </div>

            <div style={{ marginTop: '1rem', borderTop: '1px solid var(--adm-border)', paddingTop: '1rem' }}>
              <div className="adm-form-label">{t('status')}</div>
              <div className="adm-filters" style={{ marginBottom: '0.75rem' }}>
                {STATUS_OPTIONS.map(s => (
                  <button
                    key={s.value}
                    className={`adm-filter-btn ${selected.status === s.value ? 'active' : ''}`}
                    onClick={() => updateStatus(selected.id, s.value)}
                    data-testid={`set-status-${s.value}`}
                    style={{ fontSize: '0.68rem', padding: '0.3rem 0.65rem' }}
                  >
                    {s.label}
                  </button>
                ))}
              </div>

              {/* Prominent Accept Button for new/in_review bookings */}
              {(selected.status === 'new' || selected.status === 'in_review') && (
                <button
                  className="adm-btn adm-btn-primary"
                  onClick={async () => {
                    try {
                      await api.post(`/admin/inquiries/${selected.id}/accept`);
                      toast.success('Buchung akzeptiert! Bestätigung wird gesendet.');
                      setSelected(prev => ({ ...prev, status: 'confirmed' }));
                      load();
                    } catch { toast.error('Fehler beim Akzeptieren'); }
                  }}
                  data-testid="accept-booking-btn"
                  style={{
                    width: '100%', padding: '0.65rem', fontSize: '0.85rem',
                    background: '#22c55e', fontWeight: 600, display: 'flex',
                    alignItems: 'center', justifyContent: 'center', gap: '0.4rem'
                  }}
                >
                  <CheckCircle2 size={16} /> Buchung akzeptieren & Kunde benachrichtigen
                </button>
              )}
            </div>

            <div style={{ marginTop: '0.75rem' }}>
              <div className="adm-form-label">{t('remarks')}</div>
              <textarea
                className="adm-textarea"
                value={notes}
                onChange={e => setNotes(e.target.value)}
                placeholder={`${t('remarks')}...`}
                data-testid="internal-notes"
              />
              <button className="adm-btn adm-btn-primary adm-btn-sm" style={{ marginTop: '0.5rem' }} onClick={() => updateStatus(selected.id, selected.status)} data-testid="save-notes-btn">
                {t('admin_save')}
              </button>
            </div>

            {employees.length > 0 && (
              <div style={{ marginTop: '1rem', borderTop: '1px solid var(--adm-border)', paddingTop: '0.75rem' }}>
                <div className="adm-form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Users size={12} /> {t('admin_employees')}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', marginTop: '0.3rem' }}>
                  {employees.filter(e => e.is_active !== false).map(emp => (
                    <label key={emp.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', cursor: 'pointer', padding: '0.25rem 0' }}>
                      <input
                        type="checkbox"
                        checked={assignedEmps.includes(emp.name)}
                        onChange={e => {
                          if (e.target.checked) setAssignedEmps(prev => [...prev, emp.name]);
                          else setAssignedEmps(prev => prev.filter(n => n !== emp.name));
                        }}
                      />
                      <span>{emp.name}</span>
                      {emp.role && <span style={{ color: 'var(--adm-text-muted)', fontSize: '0.7rem' }}>({emp.role})</span>}
                    </label>
                  ))}
                </div>
                <button className="adm-btn adm-btn-secondary adm-btn-sm" style={{ marginTop: '0.4rem' }} onClick={() => updateStatus(selected.id, selected.status)} data-testid="save-assignment-btn">
                  {t('admin_save')}
                </button>
              </div>
            )}

            <div style={{ marginTop: '1rem', borderTop: '1px solid var(--adm-border)', paddingTop: '0.75rem' }}>
              <div className="adm-form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Receipt size={12} /> {t('invoice')}</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px auto', gap: '0.5rem', marginTop: '0.3rem', alignItems: 'center' }}>
                <select
                  className="adm-input"
                  value={selected.invoice_status || 'none'}
                  onChange={async (e) => {
                    try {
                      await api.put(`/admin/inquiries/${selected.id}/invoice`, { invoice_status: e.target.value });
                      toast.success(t('admin_status_update'));
                      load();
                      setSelected(prev => ({ ...prev, invoice_status: e.target.value }));
                    } catch { toast.error(t('admin_error')); }
                  }}
                  data-testid="invoice-status-select"
                >
                  {INVOICE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
                <input
                  className="adm-input"
                  type="number"
                  placeholder="CHF"
                  value={selected.invoice_amount || ''}
                  onChange={(e) => setSelected(prev => ({ ...prev, invoice_amount: parseFloat(e.target.value) || 0 }))}
                  onBlur={async () => {
                    try {
                      await api.put(`/admin/inquiries/${selected.id}/invoice`, { invoice_amount: selected.invoice_amount || 0 });
                      load();
                    } catch {}
                  }}
                  data-testid="invoice-amount-input"
                />
                {selected.invoice_status && selected.invoice_status !== 'none' && (
                  <button
                    className="adm-btn adm-btn-sm"
                    style={{ color: '#dc2626', border: '1px solid #dc2626', background: 'transparent' }}
                    onClick={async () => {
                      if (!confirm('Rechnung wirklich löschen?')) return;
                      try {
                        await api.delete(`/admin/inquiries/${selected.id}/invoice`);
                        toast.success('Rechnung gelöscht');
                        load();
                        setSelected(prev => ({ ...prev, invoice_status: 'none', invoice_amount: 0 }));
                      } catch { toast.error('Fehler'); }
                    }}
                    data-testid="delete-invoice-btn"
                  >
                    <Trash2 size={12} />
                  </button>
                )}
              </div>
              {selected.payment_method && (
                <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', color: 'var(--adm-text-muted)' }}>
                  Zahlungsart: <strong>{selected.payment_method === 'cash' ? 'Bar' : 'Rechnung'}</strong>
                  {selected.confirmed_at && <span> (bestätigt am {new Date(selected.confirmed_at).toLocaleDateString('de-CH')})</span>}
                </div>
              )}
            </div>

            <div style={{ marginTop: '1rem', borderTop: '1px solid var(--adm-border)', paddingTop: '0.75rem' }}>
              <div className="adm-form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.5rem' }}>
                <Paperclip size={12} /> {t('portal_files')} ({inquiryFiles.length})
              </div>
              <div className="adm-file-list">
                <FileUpload inquiryId={selected.id} files={inquiryFiles} onFilesChange={setInquiryFiles} readOnly={false} />
              </div>
            </div>

            <div style={{ marginTop: '1rem', borderTop: '1px solid var(--adm-border)', paddingTop: '0.75rem', display: 'flex', gap: '0.5rem' }}>
              <a
                href={`/api/admin/inquiries/${selected.id}/offer-pdf`}
                target="_blank" rel="noopener noreferrer"
                className="adm-btn adm-btn-secondary adm-btn-sm"
                style={{ textDecoration: 'none' }}
                data-testid="download-offer-pdf"
              >
                <FileDown size={13} /> PDF
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Offer Send Dialog */}
      {offerDialog && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }} data-testid="offer-dialog-overlay">
          <div style={{ background: 'var(--adm-card)', border: '1px solid var(--adm-border)', borderRadius: 12, padding: '1.75rem', maxWidth: 420, width: '90%' }} data-testid="offer-dialog">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ color: 'var(--adm-text)', margin: 0, fontSize: '1.05rem' }}>Offerte senden</h3>
              <button onClick={() => setOfferDialog(null)} style={{ background: 'none', border: 'none', color: 'var(--adm-text-muted)', cursor: 'pointer' }} data-testid="close-offer-dialog"><X size={18} /></button>
            </div>

            {selected && (
              <div style={{ background: 'var(--adm-bg)', border: '1px solid var(--adm-border)', borderRadius: 8, padding: '0.85rem', marginBottom: '1rem', fontSize: '0.82rem' }}>
                <div style={{ color: 'var(--adm-text)', fontWeight: 600, marginBottom: '0.4rem' }}>{selected.first_name} {selected.last_name}</div>
                <div style={{ color: 'var(--adm-text-muted)' }}>{selected.event_type} · {selected.event_date} · {selected.guest_count} Gäste</div>
                <div style={{ color: 'var(--adm-text-muted)' }}>{selected.location}</div>
                {selected.selected_trucks?.length > 0 && (
                  <div style={{ color: 'var(--adm-text-muted)', marginTop: '0.2rem' }}>Trucks: {selected.selected_trucks.join(', ')}</div>
                )}
              </div>
            )}

            <div className="adm-form-label">Offerte-Betrag (CHF)</div>
            <input
              className="adm-input"
              type="number"
              step="0.01"
              min="0"
              placeholder="z.B. 3500.00"
              value={offerDialog.amount || ''}
              onChange={e => setOfferDialog(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
              style={{ marginBottom: '0.5rem', fontSize: '1.1rem', fontWeight: 600 }}
              data-testid="offer-amount-input"
              autoFocus
            />
            <p style={{ color: 'var(--adm-text-muted)', fontSize: '0.72rem', marginBottom: '1rem' }}>
              Der Kunde erhält eine E-Mail mit den Event-Details, dem Betrag und einem Bestätigungslink.
            </p>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button onClick={() => setOfferDialog(null)} className="adm-btn adm-btn-secondary" style={{ flex: 1 }} data-testid="cancel-offer-btn">Abbrechen</button>
              <button onClick={sendOffer} className="adm-btn adm-btn-primary" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }} data-testid="send-offer-btn">
                <Send size={14} /> Offerte senden
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}
