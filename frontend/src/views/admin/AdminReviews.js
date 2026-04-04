"use client";
import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Star, Plus, Trash2, Save, Eye, EyeOff, Globe, AlertCircle } from 'lucide-react';

function StarRating({ value, onChange, size = 18 }) {
  return (
    <div style={{ display: 'flex', gap: '2px' }}>
      {[1, 2, 3, 4, 5].map(s => (
        <Star
          key={s}
          size={size}
          onClick={() => onChange?.(s)}
          style={{
            cursor: onChange ? 'pointer' : 'default',
            fill: s <= value ? '#e8b931' : 'transparent',
            color: s <= value ? '#e8b931' : '#ccc',
            transition: 'all 0.15s'
          }}
        />
      ))}
    </div>
  );
}

function SourceBadge({ source }) {
  if (source === 'google') {
    return (
      <span style={{
        display: 'inline-flex', alignItems: 'center', gap: '4px',
        background: '#e8f5e9', color: '#2e7d32', fontSize: '0.7rem',
        fontWeight: 600, padding: '2px 8px', borderRadius: '10px'
      }} data-testid="badge-google">
        <Globe size={11} /> Google
      </span>
    );
  }
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '4px',
      background: '#fff3e0', color: '#e65100', fontSize: '0.7rem',
      fontWeight: 600, padding: '2px 8px', borderRadius: '10px'
    }} data-testid="badge-placeholder">
      Platzhalter
    </span>
  );
}

export default function AdminReviews() {
  const { t } = useLanguage();
  const [reviews, setReviews] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ author: '', rating: 5, text: '', date: '', event_type: '', source: 'google', is_active: true });
  const [saving, setSaving] = useState(false);

  const load = () => api.get('/admin/reviews').then(r => setReviews(r.data)).catch(() => {});

  useEffect(() => { load(); }, []);

  const googleReviews = reviews.filter(r => r.source === 'google' && r.is_active);
  const placeholderReviews = reviews.filter(r => r.source !== 'google');
  const activeReviews = reviews.filter(r => r.is_active);
  const avgRating = activeReviews.length > 0
    ? (activeReviews.reduce((s, r) => s + r.rating, 0) / activeReviews.length).toFixed(1)
    : '0.0';

  const resetForm = () => {
    setForm({ author: '', rating: 5, text: '', date: new Date().toISOString().slice(0, 10), event_type: '', source: 'google', is_active: true });
    setEditing(null);
  };

  const startEdit = (r) => {
    setForm({ author: r.author, rating: r.rating, text: r.text, date: r.date, event_type: r.event_type || '', source: r.source || 'placeholder', is_active: r.is_active });
    setEditing(r.id);
  };

  const handleSave = async () => {
    if (!form.author || !form.text) { toast.error('Name und Text sind Pflichtfelder'); return; }
    setSaving(true);
    try {
      if (editing) {
        await api.put(`/admin/reviews/${editing}`, form);
        toast.success('Bewertung aktualisiert');
      } else {
        await api.post('/admin/reviews', form);
        toast.success('Bewertung erstellt');
      }
      resetForm();
      load();
    } catch { toast.error('Fehler beim Speichern'); }
    setSaving(false);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bewertung wirklich loeschen?')) return;
    try {
      await api.delete(`/admin/reviews/${id}`);
      toast.success('Geloescht');
      load();
    } catch { toast.error('Fehler'); }
  };

  const toggleActive = async (r) => {
    try {
      await api.put(`/admin/reviews/${r.id}`, { is_active: !r.is_active });
      load();
    } catch { toast.error('Fehler'); }
  };

  return (
    <AdminLayout title={t('admin_reviews')}>
      {/* Info banner */}
      {googleReviews.length > 0 && placeholderReviews.length > 0 && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.75rem 1rem',
          background: '#e8f5e9', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.82rem', color: '#2e7d32'
        }} data-testid="google-active-banner">
          <Globe size={16} />
          <span><strong>Google-Bewertungen aktiv:</strong> {placeholderReviews.length} Platzhalter werden auf der Webseite automatisch ausgeblendet.</span>
        </div>
      )}

      {googleReviews.length === 0 && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.75rem 1rem',
          background: '#fff3e0', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.82rem', color: '#e65100'
        }} data-testid="placeholder-info-banner">
          <AlertCircle size={16} />
          <span>Aktuell werden <strong>Platzhalter-Bewertungen</strong> angezeigt. Sobald du eine Google-Bewertung hinzufuegst, verschwinden die Platzhalter automatisch von der Webseite.</span>
        </div>
      )}

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.25rem' }}>
        <div className="adm-detail" style={{ padding: '1rem', textAlign: 'center' }} data-testid="reviews-total">
          <div style={{ fontSize: '1.6rem', fontWeight: 700 }}>{reviews.length}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)' }}>Gesamt</div>
        </div>
        <div className="adm-detail" style={{ padding: '1rem', textAlign: 'center' }} data-testid="reviews-google">
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#2e7d32' }}>{googleReviews.length}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)' }}>Google</div>
        </div>
        <div className="adm-detail" style={{ padding: '1rem', textAlign: 'center' }} data-testid="reviews-placeholder">
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#e65100' }}>{placeholderReviews.length}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)' }}>Platzhalter</div>
        </div>
        <div className="adm-detail" style={{ padding: '1rem', textAlign: 'center' }} data-testid="reviews-avg">
          <div style={{ fontSize: '1.6rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.3rem' }}>
            <Star size={20} style={{ fill: '#e8b931', color: '#e8b931' }} /> {avgRating}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)' }}>Durchschnitt</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* Form */}
        <div className="adm-detail" data-testid="review-form">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title">{editing ? 'Bewertung bearbeiten' : 'Google-Bewertung importieren'}</span>
            {editing && (
              <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={resetForm}>Abbrechen</button>
            )}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div>
              <div className="adm-form-label">Quelle *</div>
              <select className="adm-input" value={form.source} onChange={e => setForm(f => ({ ...f, source: e.target.value }))} data-testid="review-source">
                <option value="google">Google Bewertung</option>
                <option value="placeholder">Platzhalter</option>
              </select>
            </div>
            <div>
              <div className="adm-form-label">Name / Firma *</div>
              <input className="adm-input" value={form.author} onChange={e => setForm(f => ({ ...f, author: e.target.value }))} placeholder="z.B. Max Muster" data-testid="review-author" />
            </div>
            <div>
              <div className="adm-form-label">Bewertung *</div>
              <StarRating value={form.rating} onChange={v => setForm(f => ({ ...f, rating: v }))} size={24} />
            </div>
            <div>
              <div className="adm-form-label">Text *</div>
              <textarea className="adm-input" rows={3} value={form.text} onChange={e => setForm(f => ({ ...f, text: e.target.value }))} placeholder="Bewertungstext von Google kopieren..." data-testid="review-text" />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div>
                <div className="adm-form-label">Datum</div>
                <input className="adm-input" type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} data-testid="review-date" />
              </div>
              <div>
                <div className="adm-form-label">Event-Typ</div>
                <select className="adm-input" value={form.event_type} onChange={e => setForm(f => ({ ...f, event_type: e.target.value }))} data-testid="review-event-type">
                  <option value="">-- Typ --</option>
                  <option value="Festival">Festival</option>
                  <option value="Firmenanlass">Firmenanlass</option>
                  <option value="Hochzeit">Hochzeit</option>
                  <option value="Privatanlass">Privatanlass</option>
                  <option value="Geburtstag">Geburtstag</option>
                  <option value="Sonstiges">Sonstiges</option>
                </select>
              </div>
            </div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem' }}>
              <input type="checkbox" checked={form.is_active} onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))} />
              Auf Webseite anzeigen
            </label>
            <button className="adm-btn adm-btn-primary" onClick={handleSave} disabled={saving} data-testid="review-save-btn">
              <Save size={15} /> {saving ? 'Speichern...' : editing ? 'Aktualisieren' : 'Bewertung erstellen'}
            </button>
          </div>
        </div>

        {/* List */}
        <div className="adm-detail" data-testid="reviews-list">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title">Alle Bewertungen ({reviews.length})</span>
          </div>
          {reviews.length === 0 ? (
            <div className="adm-empty">Noch keine Bewertungen vorhanden.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '500px', overflowY: 'auto' }}>
              {reviews.map(r => (
                <div key={r.id} style={{ padding: '0.75rem', border: '1px solid var(--adm-border)', borderRadius: '8px', opacity: r.is_active ? 1 : 0.5 }} data-testid={`review-item-${r.id}`}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{r.author}</span>
                      <SourceBadge source={r.source || 'placeholder'} />
                    </div>
                    <StarRating value={r.rating} size={14} />
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--adm-text-secondary)', marginBottom: '0.4rem', lineHeight: 1.5 }}>{r.text}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.72rem', color: 'var(--adm-text-secondary)' }}>
                      {r.date}{r.event_type ? ` | ${r.event_type}` : ''}
                    </span>
                    <div style={{ display: 'flex', gap: '0.3rem' }}>
                      <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => toggleActive(r)} title={r.is_active ? 'Ausblenden' : 'Einblenden'} style={{ padding: '0.2rem 0.4rem' }}>
                        {r.is_active ? <Eye size={13} /> : <EyeOff size={13} />}
                      </button>
                      <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => startEdit(r)} style={{ padding: '0.2rem 0.4rem', fontSize: '0.72rem' }}>
                        Bearbeiten
                      </button>
                      <button className="adm-btn adm-btn-danger adm-btn-sm" onClick={() => handleDelete(r.id)} style={{ padding: '0.2rem 0.4rem' }}>
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
}
