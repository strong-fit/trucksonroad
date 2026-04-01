import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Save, Truck, ChevronDown, ChevronUp } from 'lucide-react';

export default function AdminTrucks() {
  const [trucks, setTrucks] = useState([]);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    api.get('/admin/trucks').then(r => setTrucks(r.data)).catch(() => {});
  }, []);

  const toggle = (slug) => setExpanded(expanded === slug ? null : slug);

  const updateField = (slug, field, value) => {
    setTrucks(prev => prev.map(t => t.slug === slug ? { ...t, [field]: value } : t));
  };

  const updateMenuItem = (slug, idx, value) => {
    setTrucks(prev => prev.map(t => {
      if (t.slug !== slug) return t;
      const menu = [...(t.menu_de || [])];
      menu[idx] = value;
      return { ...t, menu_de: menu };
    }));
  };

  const addMenuItem = (slug) => {
    setTrucks(prev => prev.map(t => t.slug === slug ? { ...t, menu_de: [...(t.menu_de || []), ''] } : t));
  };

  const removeMenuItem = (slug, idx) => {
    setTrucks(prev => prev.map(t => {
      if (t.slug !== slug) return t;
      const menu = [...(t.menu_de || [])];
      menu.splice(idx, 1);
      return { ...t, menu_de: menu };
    }));
  };

  const save = async (truck) => {
    try {
      const { slug, ...data } = truck;
      await api.put(`/admin/trucks/${slug}`, data);
      toast.success(`${truck.name_de} gespeichert`);
    } catch { toast.error('Fehler beim Speichern'); }
  };

  return (
    <AdminLayout title="Trucks">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {trucks.map(truck => (
          <div key={truck.slug} className="adm-detail" data-testid={`truck-card-${truck.slug}`} style={{ padding: 0, overflow: 'hidden' }}>
            <div
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.5rem', cursor: 'pointer', background: expanded === truck.slug ? 'var(--adm-hover)' : 'transparent' }}
              onClick={() => toggle(truck.slug)}
              data-testid={`truck-toggle-${truck.slug}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Truck size={18} style={{ color: 'var(--adm-gold)' }} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{truck.name_de}</span>
                {truck.tag && <span className="adm-badge adm-badge-confirmed"><span className="adm-badge-dot" />{truck.tag}</span>}
              </div>
              {expanded === truck.slug ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </div>

            {expanded === truck.slug && (
              <div style={{ padding: '0 1.5rem 1.5rem', borderTop: '1px solid var(--adm-border)' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '1rem' }}>
                  <div>
                    <div className="adm-form-label">Name (DE)</div>
                    <input className="adm-input" value={truck.name_de || ''} onChange={e => updateField(truck.slug, 'name_de', e.target.value)} data-testid={`truck-name-de-${truck.slug}`} />
                  </div>
                  <div>
                    <div className="adm-form-label">Name (EN)</div>
                    <input className="adm-input" value={truck.name_en || ''} onChange={e => updateField(truck.slug, 'name_en', e.target.value)} data-testid={`truck-name-en-${truck.slug}`} />
                  </div>
                </div>
                <div style={{ marginTop: '0.75rem' }}>
                  <div className="adm-form-label">Beschreibung (DE)</div>
                  <textarea className="adm-textarea" value={truck.desc_de || ''} onChange={e => updateField(truck.slug, 'desc_de', e.target.value)} data-testid={`truck-desc-${truck.slug}`} />
                </div>
                <div style={{ marginTop: '0.75rem' }}>
                  <div className="adm-form-label">Bild-URL</div>
                  <input className="adm-input" value={truck.image || ''} onChange={e => updateField(truck.slug, 'image', e.target.value)} data-testid={`truck-image-${truck.slug}`} />
                  {truck.image && <img src={truck.image} alt="" style={{ marginTop: '0.5rem', maxHeight: '120px', borderRadius: '8px', border: '1px solid var(--adm-border)' }} />}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem', marginTop: '0.75rem' }}>
                  <div>
                    <div className="adm-form-label">Kapazitaet</div>
                    <input className="adm-input" value={truck.capacity || ''} onChange={e => updateField(truck.slug, 'capacity', e.target.value)} />
                  </div>
                  <div>
                    <div className="adm-form-label">Platzbedarf</div>
                    <input className="adm-input" value={truck.space_required || ''} onChange={e => updateField(truck.slug, 'space_required', e.target.value)} />
                  </div>
                  <div>
                    <div className="adm-form-label">Tag</div>
                    <input className="adm-input" value={truck.tag || ''} onChange={e => updateField(truck.slug, 'tag', e.target.value)} />
                  </div>
                </div>
                <div style={{ marginTop: '0.75rem' }}>
                  <div className="adm-form-label">Menu (DE)</div>
                  {(truck.menu_de || []).map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.3rem' }}>
                      <input className="adm-input" value={item} onChange={e => updateMenuItem(truck.slug, idx, e.target.value)} style={{ flex: 1 }} />
                      <button className="adm-btn adm-btn-danger adm-btn-sm" onClick={() => removeMenuItem(truck.slug, idx)}>-</button>
                    </div>
                  ))}
                  <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => addMenuItem(truck.slug)} style={{ marginTop: '0.3rem' }}>+ Menu-Item</button>
                </div>
                <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                  <button className="adm-btn adm-btn-primary" onClick={() => save(truck)} data-testid={`truck-save-${truck.slug}`}>
                    <Save size={14} /> Speichern
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </AdminLayout>
  );
}
