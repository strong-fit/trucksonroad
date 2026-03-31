import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Trash2, Inbox } from 'lucide-react';

const STATUS_OPTIONS = [
  { value: 'new', label: 'Neu' },
  { value: 'in_review', label: 'In Pruefung' },
  { value: 'offer_sent', label: 'Offerte gesendet' },
  { value: 'confirmed', label: 'Bestaetigt' },
  { value: 'cancelled', label: 'Abgesagt' },
];

export default function AdminInquiries() {
  const [inquiries, setInquiries] = useState([]);
  const [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState(null);
  const [notes, setNotes] = useState('');

  const load = () => api.get('/admin/inquiries').then(r => setInquiries(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const filtered = filter === 'all' ? inquiries : inquiries.filter(i => i.status === filter);

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/admin/inquiries/${id}`, { status, internal_notes: notes });
      toast.success('Status aktualisiert');
      load();
      if (selected?.id === id) setSelected(prev => ({ ...prev, status }));
    } catch { toast.error('Fehler beim Aktualisieren'); }
  };

  const deleteInquiry = async (id) => {
    if (!window.confirm('Anfrage wirklich loeschen?')) return;
    try {
      await api.delete(`/admin/inquiries/${id}`);
      toast.success('Anfrage geloescht');
      load();
      if (selected?.id === id) setSelected(null);
    } catch { toast.error('Fehler'); }
  };

  return (
    <AdminLayout title="Anfragen">
      <div className="adm-filters" data-testid="inquiry-filters">
        <button className={`adm-filter-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')} data-testid="filter-all">
          Alle ({inquiries.length})
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
              Keine Anfragen gefunden.
            </div>
          ) : (
            <table className="adm-table" data-testid="inquiries-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Datum</th>
                  <th>Typ</th>
                  <th>Gaeste</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(inq => (
                  <tr
                    key={inq.id}
                    className={selected?.id === inq.id ? 'selected' : ''}
                    onClick={() => { setSelected(inq); setNotes(inq.internal_notes || ''); }}
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
              <span className="adm-detail-title">Anfrage Details</span>
              <button className="adm-detail-close" onClick={() => setSelected(null)} data-testid="close-detail-btn">&times;</button>
            </div>
            <div className="adm-detail-grid">
              <div>
                <div className="label">Name</div>
                <div className="value">{selected.first_name || selected.name || ''} {selected.last_name || ''}</div>
              </div>
              {selected.company && <div><div className="label">Firma</div><div className="value">{selected.company}</div></div>}
              <div><div className="label">E-Mail</div><div className="value">{selected.email || '-'}</div></div>
              <div><div className="label">Telefon</div><div className="value">{selected.phone || '-'}</div></div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                <div><div className="label">Datum</div><div className="value">{selected.event_date || '-'}</div></div>
                <div><div className="label">Uhrzeit</div><div className="value">{selected.event_time || '-'}</div></div>
              </div>
              <div><div className="label">Ort</div><div className="value">{selected.location || '-'}</div></div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                <div><div className="label">Gaeste</div><div className="value">{selected.guest_count || '-'}</div></div>
                <div><div className="label">Indoor/Outdoor</div><div className="value">{selected.indoor_outdoor || '-'}</div></div>
              </div>
              <div><div className="label">Eventtyp</div><div className="value">{selected.event_type || selected.concept || '-'}</div></div>
              {selected.selected_trucks?.length > 0 && <div><div className="label">Trucks</div><div className="value">{selected.selected_trucks.join(', ')}</div></div>}
              {selected.extras?.length > 0 && <div><div className="label">Extras</div><div className="value">{selected.extras.join(', ')}</div></div>}
              {selected.budget && <div><div className="label">Budget</div><div className="value">{selected.budget}</div></div>}
              {selected.remarks && <div><div className="label">Bemerkungen</div><div className="value">{selected.remarks}</div></div>}
              <div><div className="label">Erstellt</div><div className="value" style={{ color: 'var(--adm-text-muted)' }}>{selected.created_at ? new Date(selected.created_at).toLocaleString('de-CH') : '-'}</div></div>
            </div>

            <div style={{ marginTop: '1.25rem', borderTop: '1px solid var(--adm-border)', paddingTop: '1rem' }}>
              <div className="adm-form-label">Status aendern</div>
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
            </div>

            <div style={{ marginTop: '0.75rem' }}>
              <div className="adm-form-label">Interne Notizen</div>
              <textarea
                className="adm-textarea"
                value={notes}
                onChange={e => setNotes(e.target.value)}
                placeholder="Interne Notizen..."
                data-testid="internal-notes"
              />
              <button className="adm-btn adm-btn-primary adm-btn-sm" style={{ marginTop: '0.5rem' }} onClick={() => updateStatus(selected.id, selected.status)} data-testid="save-notes-btn">
                Notizen speichern
              </button>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
