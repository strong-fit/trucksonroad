import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Save, Plus, Trash2, GripVertical, HelpCircle } from 'lucide-react';

export default function AdminFAQs() {
  const { t } = useLanguage();
  const [faqs, setFaqs] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ question_de: '', answer_de: '', question_en: '', answer_en: '', order: 0 });

  const load = () => api.get('/admin/faqs').then(r => setFaqs(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const startEdit = (faq) => {
    setEditing(faq.id);
    setForm({ question_de: faq.question_de, answer_de: faq.answer_de, question_en: faq.question_en || '', answer_en: faq.answer_en || '', order: faq.order || 0 });
  };

  const startNew = () => {
    setEditing('new');
    setForm({ question_de: '', answer_de: '', question_en: '', answer_en: '', order: faqs.length });
  };

  const cancel = () => { setEditing(null); setForm({ question_de: '', answer_de: '', question_en: '', answer_en: '', order: 0 }); };

  const save = async () => {
    if (!form.question_de || !form.answer_de) { toast.error('Frage und Antwort (DE) sind Pflichtfelder'); return; }
    try {
      if (editing === 'new') {
        await api.post('/admin/faqs', form);
        toast.success('FAQ erstellt');
      } else {
        await api.put(`/admin/faqs/${editing}`, form);
        toast.success('FAQ aktualisiert');
      }
      cancel();
      load();
    } catch { toast.error('Fehler'); }
  };

  const remove = async (id) => {
    if (!window.confirm('FAQ wirklich loeschen?')) return;
    try {
      await api.delete(`/admin/faqs/${id}`);
      toast.success('FAQ geloescht');
      load();
    } catch { toast.error('Fehler'); }
  };

  return (
    <AdminLayout title={t('admin_faqs')}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
        <button className="adm-btn adm-btn-primary" onClick={startNew} data-testid="add-faq-btn">
          <Plus size={15} /> Neue FAQ
        </button>
      </div>

      {editing && (
        <div className="adm-detail" style={{ marginBottom: '1.25rem' }} data-testid="faq-edit-form">
          <div className="adm-detail-header">
            <span className="adm-detail-title">{editing === 'new' ? 'Neue FAQ' : 'FAQ bearbeiten'}</span>
            <button className="adm-detail-close" onClick={cancel}>&times;</button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <div className="adm-form-label">Frage (DE) *</div>
              <input className="adm-input" value={form.question_de} onChange={e => setForm({...form, question_de: e.target.value})} data-testid="faq-question-de" />
              <div className="adm-form-label" style={{ marginTop: '0.75rem' }}>Antwort (DE) *</div>
              <textarea className="adm-textarea" value={form.answer_de} onChange={e => setForm({...form, answer_de: e.target.value})} data-testid="faq-answer-de" />
            </div>
            <div>
              <div className="adm-form-label">Frage (EN)</div>
              <input className="adm-input" value={form.question_en} onChange={e => setForm({...form, question_en: e.target.value})} data-testid="faq-question-en" />
              <div className="adm-form-label" style={{ marginTop: '0.75rem' }}>Antwort (EN)</div>
              <textarea className="adm-textarea" value={form.answer_en} onChange={e => setForm({...form, answer_en: e.target.value})} data-testid="faq-answer-en" />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '1rem' }}>
            <div>
              <div className="adm-form-label">Reihenfolge</div>
              <input className="adm-input" type="number" value={form.order} onChange={e => setForm({...form, order: parseInt(e.target.value) || 0})} style={{ width: '80px' }} data-testid="faq-order" />
            </div>
            <div style={{ flex: 1 }} />
            <button className="adm-btn adm-btn-secondary" onClick={cancel}>Abbrechen</button>
            <button className="adm-btn adm-btn-primary" onClick={save} data-testid="faq-save-btn">
              <Save size={14} /> Speichern
            </button>
          </div>
        </div>
      )}

      <div className="adm-table-wrap" data-testid="faq-table-wrap">
        {faqs.length === 0 ? (
          <div className="adm-empty">
            <div className="adm-empty-icon"><HelpCircle size={22} /></div>
            Noch keine FAQs vorhanden.
          </div>
        ) : (
          <table className="adm-table" data-testid="faq-table">
            <thead>
              <tr>
                <th style={{ width: '50px' }}>#</th>
                <th>Frage (DE)</th>
                <th>Antwort (DE)</th>
                <th style={{ width: '120px' }}></th>
              </tr>
            </thead>
            <tbody>
              {faqs.map(faq => (
                <tr key={faq.id} data-testid={`faq-row-${faq.id}`}>
                  <td style={{ color: 'var(--adm-text-muted)' }}>{faq.order}</td>
                  <td style={{ fontWeight: 500 }}>{faq.question_de}</td>
                  <td style={{ color: 'var(--adm-text-secondary)', fontSize: '0.78rem', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{faq.answer_de}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.3rem' }}>
                      <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => startEdit(faq)} data-testid={`faq-edit-${faq.id}`}>Bearbeiten</button>
                      <button className="adm-btn adm-btn-danger adm-btn-sm" onClick={() => remove(faq.id)} data-testid={`faq-delete-${faq.id}`} style={{ padding: '0.25rem 0.4rem' }}>
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </AdminLayout>
  );
}
