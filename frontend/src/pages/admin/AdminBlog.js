import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Save, Trash2, Eye, EyeOff, Plus, FileText, Globe, ExternalLink } from 'lucide-react';

const CATEGORY_OPTIONS = [
  { value: 'guide', label: 'Ratgeber' },
  { value: 'locations', label: 'Standorte' },
  { value: 'tipps', label: 'Tipps' },
  { value: 'events', label: 'Events' },
  { value: 'regionen', label: 'Regionen' },
  { value: 'rezepte', label: 'Rezepte' },
  { value: 'news', label: 'News' },
];

export default function AdminBlog() {
  const { t } = useLanguage();
  const [posts, setPosts] = useState([]);
  const [editing, setEditing] = useState(null);
  const [activeLang, setActiveLang] = useState('de');
  const [form, setForm] = useState({
    slug: '', title_de: '', title_en: '', title_fr: '', title_it: '',
    excerpt_de: '', excerpt_en: '', excerpt_fr: '', excerpt_it: '',
    content_de: '', content_en: '', content_fr: '', content_it: '',
    category: 'news', image: '', tags: '', author: 'TrucksOnRoad Team', is_published: false
  });
  const [saving, setSaving] = useState(false);

  const load = () => api.get('/admin/blog').then(r => setPosts(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const publishedCount = posts.filter(p => p.is_published).length;

  const resetForm = () => {
    setForm({
      slug: '', title_de: '', title_en: '', title_fr: '', title_it: '',
      excerpt_de: '', excerpt_en: '', excerpt_fr: '', excerpt_it: '',
      content_de: '', content_en: '', content_fr: '', content_it: '',
      category: 'news', image: '', tags: '', author: 'TrucksOnRoad Team', is_published: false
    });
    setEditing(null);
    setActiveLang('de');
  };

  const startEdit = (p) => {
    setForm({
      slug: p.slug, title_de: p.title_de || '', title_en: p.title_en || '', title_fr: p.title_fr || '', title_it: p.title_it || '',
      excerpt_de: p.excerpt_de || '', excerpt_en: p.excerpt_en || '', excerpt_fr: p.excerpt_fr || '', excerpt_it: p.excerpt_it || '',
      content_de: p.content_de || '', content_en: p.content_en || '', content_fr: p.content_fr || '', content_it: p.content_it || '',
      category: p.category || 'news', image: p.image || '', tags: (p.tags || []).join(', '), author: p.author || 'TrucksOnRoad Team', is_published: p.is_published
    });
    setEditing(p.id);
    setActiveLang('de');
  };

  const handleSave = async () => {
    if (!form.slug || !form.title_de) { toast.error('Slug und deutscher Titel sind Pflichtfelder'); return; }
    setSaving(true);
    const payload = { ...form, tags: form.tags.split(',').map(t => t.trim()).filter(Boolean) };
    try {
      if (editing) {
        await api.put(`/admin/blog/${editing}`, payload);
        toast.success('Beitrag aktualisiert');
      } else {
        await api.post('/admin/blog', payload);
        toast.success('Beitrag erstellt');
      }
      resetForm();
      load();
    } catch { toast.error('Fehler beim Speichern'); }
    setSaving(false);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Beitrag wirklich loeschen?')) return;
    try {
      await api.delete(`/admin/blog/${id}`);
      toast.success('Geloescht');
      load();
    } catch { toast.error('Fehler'); }
  };

  const togglePublished = async (p) => {
    try {
      await api.put(`/admin/blog/${p.id}`, { is_published: !p.is_published });
      load();
    } catch { toast.error('Fehler'); }
  };

  const autoSlug = (title) => {
    return title.toLowerCase().replace(/[äÄ]/g, 'ae').replace(/[öÖ]/g, 'oe').replace(/[üÜ]/g, 'ue')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  };

  const LANGS = ['de', 'en', 'fr', 'it'];

  return (
    <AdminLayout title="Blog-Beitraege">
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.25rem' }}>
        <div className="adm-detail" style={{ padding: '1rem', textAlign: 'center' }} data-testid="blog-stats-total">
          <div style={{ fontSize: '1.6rem', fontWeight: 700 }}>{posts.length}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)' }}>Gesamt</div>
        </div>
        <div className="adm-detail" style={{ padding: '1rem', textAlign: 'center' }} data-testid="blog-stats-published">
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#2e7d32' }}>{publishedCount}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)' }}>Veroeffentlicht</div>
        </div>
        <div className="adm-detail" style={{ padding: '1rem', textAlign: 'center' }} data-testid="blog-stats-draft">
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#e65100' }}>{posts.length - publishedCount}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)' }}>Entwurf</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* Form */}
        <div className="adm-detail" data-testid="blog-form">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title">{editing ? 'Beitrag bearbeiten' : 'Neuer Beitrag'}</span>
            {editing && <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={resetForm}>Abbrechen</button>}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div>
                <div className="adm-form-label">Slug (URL) *</div>
                <input className="adm-input" value={form.slug} onChange={e => setForm(f => ({ ...f, slug: e.target.value }))} placeholder="z.B. foodtruck-mieten-schweiz" data-testid="blog-slug" />
              </div>
              <div>
                <div className="adm-form-label">Kategorie</div>
                <select className="adm-input" value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} data-testid="blog-category">
                  {CATEGORY_OPTIONS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
            </div>

            <div>
              <div className="adm-form-label">Bild-URL</div>
              <input className="adm-input" value={form.image} onChange={e => setForm(f => ({ ...f, image: e.target.value }))} placeholder="https://images.unsplash.com/..." data-testid="blog-image" />
            </div>

            {/* Language Tabs */}
            <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.5rem' }}>
              {LANGS.map(l => (
                <button key={l} onClick={() => setActiveLang(l)}
                  style={{
                    padding: '0.3rem 0.8rem', borderRadius: '6px 6px 0 0', border: 'none',
                    background: activeLang === l ? 'var(--adm-accent)' : 'transparent',
                    color: activeLang === l ? '#fff' : 'var(--adm-text-secondary)',
                    fontWeight: 600, fontSize: '0.78rem', cursor: 'pointer'
                  }}
                  data-testid={`blog-lang-tab-${l}`}
                >
                  {l.toUpperCase()}
                </button>
              ))}
            </div>

            <div>
              <div className="adm-form-label">Titel ({activeLang.toUpperCase()}) {activeLang === 'de' && '*'}</div>
              <input
                className="adm-input"
                value={form[`title_${activeLang}`]}
                onChange={e => {
                  const v = e.target.value;
                  setForm(f => ({ ...f, [`title_${activeLang}`]: v, ...(activeLang === 'de' && !editing ? { slug: autoSlug(v) } : {}) }));
                }}
                placeholder={`Titel auf ${activeLang.toUpperCase()}`}
                data-testid={`blog-title-${activeLang}`}
              />
            </div>

            <div>
              <div className="adm-form-label">Kurzbeschreibung ({activeLang.toUpperCase()})</div>
              <textarea className="adm-input" rows={2} value={form[`excerpt_${activeLang}`]}
                onChange={e => setForm(f => ({ ...f, [`excerpt_${activeLang}`]: e.target.value }))}
                placeholder={`Kurzbeschreibung auf ${activeLang.toUpperCase()}`}
                data-testid={`blog-excerpt-${activeLang}`}
              />
            </div>

            <div>
              <div className="adm-form-label">Inhalt ({activeLang.toUpperCase()}) – Markdown</div>
              <textarea className="adm-input" rows={10} value={form[`content_${activeLang}`]}
                onChange={e => setForm(f => ({ ...f, [`content_${activeLang}`]: e.target.value }))}
                placeholder={`## Titel\n\nText hier...\n\n### Untertitel\n\n- Punkt 1\n- Punkt 2`}
                style={{ fontFamily: 'monospace', fontSize: '0.82rem' }}
                data-testid={`blog-content-${activeLang}`}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div>
                <div className="adm-form-label">Tags (kommagetrennt)</div>
                <input className="adm-input" value={form.tags} onChange={e => setForm(f => ({ ...f, tags: e.target.value }))} placeholder="Foodtruck, Schweiz, Event" data-testid="blog-tags" />
              </div>
              <div>
                <div className="adm-form-label">Autor</div>
                <input className="adm-input" value={form.author} onChange={e => setForm(f => ({ ...f, author: e.target.value }))} data-testid="blog-author" />
              </div>
            </div>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem' }}>
              <input type="checkbox" checked={form.is_published} onChange={e => setForm(f => ({ ...f, is_published: e.target.checked }))} />
              Veroeffentlichen
            </label>

            <button className="adm-btn adm-btn-primary" onClick={handleSave} disabled={saving} data-testid="blog-save-btn">
              <Save size={15} /> {saving ? 'Speichern...' : editing ? 'Aktualisieren' : 'Beitrag erstellen'}
            </button>
          </div>
        </div>

        {/* List */}
        <div className="adm-detail" data-testid="blog-list">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title">Alle Beitraege ({posts.length})</span>
          </div>
          {posts.length === 0 ? (
            <div className="adm-empty">Noch keine Beitraege vorhanden.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '600px', overflowY: 'auto' }}>
              {posts.map(p => (
                <div key={p.id} style={{ padding: '0.7rem', border: '1px solid var(--adm-border)', borderRadius: '8px', opacity: p.is_published ? 1 : 0.5 }} data-testid={`blog-item-${p.id}`}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.3rem' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.85rem', lineHeight: 1.3 }}>{p.title_de}</div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--adm-text-secondary)', marginTop: '0.2rem' }}>
                        /{p.slug} &middot; {p.category}
                      </div>
                    </div>
                    <span style={{
                      fontSize: '0.68rem', fontWeight: 600, padding: '2px 8px', borderRadius: '10px',
                      background: p.is_published ? '#e8f5e9' : '#fff3e0',
                      color: p.is_published ? '#2e7d32' : '#e65100'
                    }}>
                      {p.is_published ? 'Live' : 'Entwurf'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.3rem', marginTop: '0.4rem' }}>
                    <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => togglePublished(p)} style={{ padding: '0.2rem 0.4rem' }}>
                      {p.is_published ? <EyeOff size={13} /> : <Eye size={13} />}
                    </button>
                    <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => startEdit(p)} style={{ padding: '0.2rem 0.4rem', fontSize: '0.72rem' }}>
                      Bearbeiten
                    </button>
                    <button className="adm-btn adm-btn-danger adm-btn-sm" onClick={() => handleDelete(p.id)} style={{ padding: '0.2rem 0.4rem' }}>
                      <Trash2 size={13} />
                    </button>
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
