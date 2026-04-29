"use client";
import { useState, useEffect } from 'react';
import { AdminLayout } from '@/views/admin/AdminDashboard';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Plus, Edit3, Trash2, GripVertical, Save } from 'lucide-react';

export default function AdminMenuCategories() {
  const [categories, setCategories] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name_de: '', name_en: '', name_fr: '', name_it: '', truck_slug: '', order: 0 });
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = () => {
    api.get('/admin/menu-categories').then(r => setCategories(r.data)).catch(() => {});
    api.get('/trucks').then(r => setTrucks(r.data)).catch(() => {});
  };
  useEffect(load, []);

  const save = async () => {
    if (!form.name_de) { toast.error('Name (DE) ist Pflicht'); return; }
    setLoading(true);
    try {
      if (editing) {
        await api.put(`/admin/menu-categories/${editing}`, form);
        toast.success('Kategorie aktualisiert');
      } else {
        await api.post('/admin/menu-categories', { ...form, order: categories.length + 1 });
        toast.success('Kategorie erstellt');
      }
      setForm({ name_de: '', name_en: '', name_fr: '', name_it: '', truck_slug: '', order: 0 });
      setEditing(null);
      load();
    } catch { toast.error('Fehler beim Speichern'); }
    setLoading(false);
  };

  const remove = async (id) => {
    if (!confirm('Kategorie wirklich löschen?')) return;
    try {
      await api.delete(`/admin/menu-categories/${id}`);
      toast.success('Gelöscht');
      load();
    } catch { toast.error('Fehler'); }
  };

  const edit = (cat) => {
    setEditing(cat.id);
    setForm({ name_de: cat.name_de, name_en: cat.name_en || '', name_fr: cat.name_fr || '', name_it: cat.name_it || '', truck_slug: cat.truck_slug || '', order: cat.order || 0 });
  };

  return (
    <AdminLayout title="Menü-Kategorien">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* Form */}
        <div className="adm-detail" data-testid="menu-cat-form">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title">{editing ? 'Kategorie bearbeiten' : 'Neue Kategorie'}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div><div className="adm-form-label">Name (DE) *</div><input className="adm-input" value={form.name_de} onChange={e => setForm(f => ({ ...f, name_de: e.target.value }))} placeholder="z.B. Burger-Menü" data-testid="cat-name-de" /></div>
            <div><div className="adm-form-label">Name (EN)</div><input className="adm-input" value={form.name_en} onChange={e => setForm(f => ({ ...f, name_en: e.target.value }))} data-testid="cat-name-en" /></div>
            <div><div className="adm-form-label">Name (FR)</div><input className="adm-input" value={form.name_fr} onChange={e => setForm(f => ({ ...f, name_fr: e.target.value }))} data-testid="cat-name-fr" /></div>
            <div><div className="adm-form-label">Name (IT)</div><input className="adm-input" value={form.name_it} onChange={e => setForm(f => ({ ...f, name_it: e.target.value }))} data-testid="cat-name-it" /></div>
            <div>
              <div className="adm-form-label">Zugehöriger Truck (optional)</div>
              <select className="adm-input" value={form.truck_slug} onChange={e => setForm(f => ({ ...f, truck_slug: e.target.value }))} data-testid="cat-truck">
                <option value="">Alle Trucks</option>
                {trucks.map(t => <option key={t.slug} value={t.slug}>{t.name_de}</option>)}
              </select>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
              <button className="adm-btn adm-btn-primary" onClick={save} disabled={loading} data-testid="cat-save-btn">
                <Save size={14} /> {editing ? 'Aktualisieren' : 'Erstellen'}
              </button>
              {editing && (
                <button className="adm-btn adm-btn-secondary" onClick={() => { setEditing(null); setForm({ name_de: '', name_en: '', name_fr: '', name_it: '', truck_slug: '', order: 0 }); }}>
                  Abbrechen
                </button>
              )}
            </div>
          </div>
        </div>

        {/* List */}
        <div className="adm-detail" data-testid="menu-cat-list">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title">Kategorien ({categories.length})</span>
          </div>
          {categories.length === 0 ? (
            <p style={{ color: 'var(--adm-muted)', fontSize: '0.85rem' }}>Noch keine Kategorien erstellt.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {categories.map(cat => (
                <div key={cat.id} style={{
                  display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.6rem 0.8rem',
                  background: editing === cat.id ? 'rgba(77,182,172,0.08)' : 'var(--adm-card)',
                  border: `1px solid ${editing === cat.id ? 'var(--adm-primary)' : 'var(--adm-border)'}`,
                  borderRadius: '6px'
                }} data-testid={`cat-item-${cat.id}`}>
                  <GripVertical size={14} style={{ opacity: 0.3 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{cat.name_de}</div>
                    {cat.truck_slug && <div style={{ fontSize: '0.75rem', color: 'var(--adm-muted)' }}>Truck: {cat.truck_slug}</div>}
                  </div>
                  <button className="adm-btn adm-btn-sm" style={{ padding: '0.3rem' }} onClick={() => edit(cat)} data-testid={`cat-edit-${cat.id}`}>
                    <Edit3 size={14} />
                  </button>
                  <button className="adm-btn adm-btn-sm" style={{ padding: '0.3rem', color: '#ef4444' }} onClick={() => remove(cat.id)} data-testid={`cat-del-${cat.id}`}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
}
