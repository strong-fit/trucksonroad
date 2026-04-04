"use client";
import { useState, useEffect, useRef } from 'react';
import { AdminLayout } from '@/views/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Save, Truck, ChevronDown, ChevronUp, Upload, X, Image, Film, Loader2, Plus, GripVertical } from 'lucide-react';

export default function AdminTrucks() {
  const { t } = useLanguage();
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
    <AdminLayout title={t('admin_trucks')}>
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
                {(truck.gallery || []).length > 0 && (
                  <span style={{ fontSize: '0.7rem', color: 'var(--adm-muted)', display: 'flex', alignItems: 'center', gap: 3 }}>
                    <Image size={12} /> {truck.gallery.length}
                  </span>
                )}
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
                  <div className="adm-form-label">Hauptbild-URL</div>
                  <input className="adm-input" value={truck.image || ''} onChange={e => updateField(truck.slug, 'image', e.target.value)} data-testid={`truck-image-${truck.slug}`} />
                  {truck.image && <img src={truck.image} alt="" style={{ marginTop: '0.5rem', maxHeight: '120px', borderRadius: '8px', border: '1px solid var(--adm-border)' }} />}
                </div>

                {/* Gallery Section */}
                <GalleryManager truck={truck} onUpdate={(gallery) => updateField(truck.slug, 'gallery', gallery)} />

                {/* Video URL */}
                <div style={{ marginTop: '0.75rem' }}>
                  <div className="adm-form-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Film size={14} /> Video-URL (YouTube/Vimeo)
                  </div>
                  <input
                    className="adm-input"
                    value={truck.video_url || ''}
                    onChange={e => updateField(truck.slug, 'video_url', e.target.value)}
                    placeholder="https://www.youtube.com/embed/..."
                    data-testid={`truck-video-${truck.slug}`}
                  />
                  <div style={{ fontSize: '0.7rem', color: 'var(--adm-muted)', marginTop: 4 }}>
                    Verwende die Embed-URL, z.B. https://www.youtube.com/embed/VIDEO_ID
                  </div>
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

function GalleryManager({ truck, onUpdate }) {
  const [uploading, setUploading] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const inputRef = useRef(null);
  const gallery = truck.gallery || [];

  const handleUpload = async (fileList) => {
    if (!fileList?.length) return;
    setUploading(true);
    const newGallery = [...gallery];
    for (const file of Array.from(fileList)) {
      if (file.size > 10 * 1024 * 1024) { toast.error('Max. 10 MB pro Bild'); continue; }
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await api.post(`/admin/trucks/${truck.slug}/gallery`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        newGallery.push(res.data.url);
      } catch { toast.error('Upload fehlgeschlagen'); }
    }
    onUpdate(newGallery);
    setUploading(false);
  };

  const addUrl = () => {
    if (!urlInput.trim()) return;
    onUpdate([...gallery, urlInput.trim()]);
    setUrlInput('');
  };

  const removeImage = async (idx) => {
    const url = gallery[idx];
    try {
      await api.delete(`/admin/trucks/${truck.slug}/gallery`, { data: { url } });
    } catch {}
    const newGallery = gallery.filter((_, i) => i !== idx);
    onUpdate(newGallery);
  };

  return (
    <div style={{ marginTop: '0.75rem' }} data-testid={`gallery-section-${truck.slug}`}>
      <div className="adm-form-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <Image size={14} /> Bildergalerie ({gallery.length} Bilder)
      </div>

      {/* Gallery Grid */}
      {gallery.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '0.5rem', marginBottom: '0.75rem' }}>
          {gallery.map((url, idx) => (
            <div key={idx} style={{ position: 'relative', aspectRatio: '4/3', borderRadius: 8, overflow: 'hidden', border: '1px solid var(--adm-border)' }} data-testid={`gallery-img-${idx}`}>
              <img src={url} alt={`Gallery ${idx + 1}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              <button
                onClick={() => removeImage(idx)}
                style={{
                  position: 'absolute', top: 4, right: 4, width: 22, height: 22,
                  borderRadius: '50%', background: 'rgba(0,0,0,0.7)', border: 'none',
                  color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  padding: 0
                }}
                data-testid={`gallery-remove-${idx}`}
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload + URL Input */}
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <button
          className="adm-btn adm-btn-secondary adm-btn-sm"
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
          data-testid={`gallery-upload-btn-${truck.slug}`}
          style={{ display: 'flex', alignItems: 'center', gap: 4 }}
        >
          {uploading ? <Loader2 size={14} className="sf-spin" /> : <Upload size={14} />}
          {uploading ? 'Lädt...' : 'Bild hochladen'}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          style={{ display: 'none' }}
          onChange={e => handleUpload(e.target.files)}
        />
        <div style={{ flex: 1, display: 'flex', gap: '0.3rem' }}>
          <input
            className="adm-input"
            value={urlInput}
            onChange={e => setUrlInput(e.target.value)}
            placeholder="Oder Bild-URL einfügen..."
            style={{ flex: 1, fontSize: '0.8rem' }}
            onKeyDown={e => e.key === 'Enter' && addUrl()}
            data-testid={`gallery-url-input-${truck.slug}`}
          />
          <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={addUrl} data-testid={`gallery-url-add-${truck.slug}`}>
            <Plus size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
