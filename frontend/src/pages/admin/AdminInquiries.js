import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Trash2, Eye } from 'lucide-react';

const STATUS_OPTIONS = [
  { value: 'new', label: 'Neu', class: 'sf-status-new' },
  { value: 'in_review', label: 'In Pr\u00fcfung', class: 'sf-status-in_review' },
  { value: 'offer_sent', label: 'Offerte gesendet', class: 'sf-status-offer_sent' },
  { value: 'confirmed', label: 'Best\u00e4tigt', class: 'sf-status-confirmed' },
  { value: 'cancelled', label: 'Abgesagt', class: 'sf-status-cancelled' },
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
    if (!window.confirm('Anfrage wirklich l\u00f6schen?')) return;
    try {
      await api.delete(`/admin/inquiries/${id}`);
      toast.success('Anfrage gel\u00f6scht');
      load();
      if (selected?.id === id) setSelected(null);
    } catch { toast.error('Fehler'); }
  };

  return (
    <AdminLayout title="Anfragen">
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <button className={`sf-truck-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')} data-testid="filter-all">
          Alle ({inquiries.length})
        </button>
        {STATUS_OPTIONS.map(s => {
          const count = inquiries.filter(i => i.status === s.value).length;
          return (
            <button key={s.value} className={`sf-truck-btn ${filter === s.value ? 'active' : ''}`} onClick={() => setFilter(s.value)} data-testid={`filter-${s.value}`}>
              {s.label} ({count})
            </button>
          );
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 1fr' : '1fr', gap: '1.5rem' }}>
        <div>
          {filtered.length === 0 ? (
            <p style={{ color: 'var(--sf-gray)' }}>Keine Anfragen gefunden.</p>
          ) : (
            <table className="sf-admin-table" data-testid="inquiries-table">
              <thead>
                <tr><th>Name</th><th>Datum</th><th>Typ</th><th>G\u00e4ste</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {filtered.map(inq => (
                  <tr key={inq.id} style={{ cursor: 'pointer', background: selected?.id === inq.id ? 'rgba(200,168,78,0.05)' : '' }} onClick={() => { setSelected(inq); setNotes(inq.internal_notes || ''); }}>
                    <td>{inq.first_name || inq.name || ''} {inq.last_name || ''}</td>
                    <td>{inq.event_date || '-'}</td>
                    <td style={{ fontSize: '0.8rem' }}>{inq.event_type || inq.concept || '-'}</td>
                    <td>{inq.guest_count || '-'}</td>
                    <td><span className={`sf-status-badge sf-status-${inq.status}`}>{STATUS_OPTIONS.find(s => s.value === inq.status)?.label || inq.status}</span></td>
                    <td>
                      <button onClick={(e) => { e.stopPropagation(); deleteInquiry(inq.id); }} style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }} data-testid={`delete-inquiry-${inq.id}`}>
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {selected && (
          <div style={{ background: 'var(--sf-surface)', border: '1px solid var(--sf-border)', borderRadius: '8px', padding: '1.5rem' }} data-testid="inquiry-detail">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700 }}>Anfrage Details</h3>
              <button onClick={() => setSelected(null)} style={{ background: 'none', border: 'none', color: 'var(--sf-gray)', cursor: 'pointer' }}>&times;</button>
            </div>
            <div style={{ display: 'grid', gap: '0.8rem', fontSize: '0.85rem' }}>
              <div><strong>Name:</strong> {selected.first_name || selected.name || ''} {selected.last_name || ''}</div>
              {selected.company && <div><strong>Firma:</strong> {selected.company}</div>}
              <div><strong>E-Mail:</strong> {selected.email || '-'}</div>
              <div><strong>Telefon:</strong> {selected.phone || '-'}</div>
              <div><strong>Datum:</strong> {selected.event_date || '-'}</div>
              <div><strong>Uhrzeit:</strong> {selected.event_time || '-'}</div>
              <div><strong>Ort:</strong> {selected.location || '-'}</div>
              <div><strong>G\u00e4ste:</strong> {selected.guest_count || '-'}</div>
              <div><strong>Eventtyp:</strong> {selected.event_type || selected.concept || '-'}</div>
              <div><strong>Indoor/Outdoor:</strong> {selected.indoor_outdoor || '-'}</div>
              {selected.selected_trucks?.length > 0 && <div><strong>Trucks:</strong> {selected.selected_trucks.join(', ')}</div>}
              {selected.extras?.length > 0 && <div><strong>Extras:</strong> {selected.extras.join(', ')}</div>}
              {selected.budget && <div><strong>Budget:</strong> {selected.budget}</div>}
              {selected.remarks && <div><strong>Bemerkungen:</strong> {selected.remarks}</div>}
              <div><strong>Erstellt:</strong> {selected.created_at ? new Date(selected.created_at).toLocaleString('de-CH') : '-'}</div>
            </div>

            <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--sf-border)', paddingTop: '1rem' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--sf-gray)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Status \u00e4ndern</label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                {STATUS_OPTIONS.map(s => (
                  <button key={s.value} className={`sf-truck-btn ${selected.status === s.value ? 'active' : ''}`} onClick={() => updateStatus(selected.id, s.value)} data-testid={`set-status-${s.value}`}>
                    {s.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginTop: '1rem' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--sf-gray)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Interne Notizen</label>
              <textarea
                value={notes}
                onChange={e => setNotes(e.target.value)}
                style={{ width: '100%', minHeight: '80px', marginTop: '0.5rem', background: 'var(--sf-bg)', border: '1px solid var(--sf-border)', borderRadius: '6px', padding: '0.75rem', color: 'var(--sf-white)', fontSize: '0.85rem', fontFamily: 'Outfit, sans-serif' }}
                placeholder="Interne Notizen..."
                data-testid="internal-notes"
              />
              <button className="sf-btn-primary sf-btn-sm" style={{ marginTop: '0.5rem' }} onClick={() => updateStatus(selected.id, selected.status)} data-testid="save-notes-btn">
                Notizen speichern
              </button>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
