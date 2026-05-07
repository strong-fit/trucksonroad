"use client";
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AdminLayout } from '@/views/admin/AdminDashboard';
import api from '@/lib/api';
import { toast } from 'sonner';
import {
  ArrowLeft, Save, Plus, Trash2, ArrowUp, ArrowDown,
  History, RotateCcw, Eye, X, FileText, ShieldCheck, Building2, GitCommit,
} from 'lucide-react';

const DOC_TITLES = {
  agb: 'AGB',
  datenschutz: 'Datenschutzerklärung',
  impressum: 'Impressum',
};
const DOC_ICONS = { agb: FileText, datenschutz: ShieldCheck, impressum: Building2 };

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('de-CH', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export default function AdminLegalEditor({ docType }) {
  const router = useRouter();
  const Icon = DOC_ICONS[docType] || FileText;
  const [doc, setDoc] = useState(null);
  const [form, setForm] = useState({ title: '', subtitle: '', sections: [] });
  const [changeNotes, setChangeNotes] = useState('');
  const [versions, setVersions] = useState([]);
  const [saving, setSaving] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [diffVersion, setDiffVersion] = useState(null);

  const loadAll = async () => {
    try {
      const [d, v] = await Promise.all([
        api.get(`/admin/legal/${docType}`),
        api.get(`/admin/legal/${docType}/versions`),
      ]);
      setDoc(d.data);
      setForm({
        title: d.data.title || '',
        subtitle: d.data.subtitle || '',
        sections: d.data.sections || [],
      });
      setVersions(v.data || []);
    } catch {
      toast.error('Konnte Dokument nicht laden');
    }
  };

  useEffect(() => { loadAll(); }, [docType]);

  const updateSection = (idx, field, value) => {
    const next = [...form.sections];
    next[idx] = { ...next[idx], [field]: value };
    setForm({ ...form, sections: next });
  };

  const addSection = () => {
    setForm({
      ...form,
      sections: [...form.sections, { heading: 'Neuer Abschnitt', content: '' }],
    });
  };

  const removeSection = (idx) => {
    if (!confirm('Diesen Abschnitt wirklich entfernen?')) return;
    setForm({ ...form, sections: form.sections.filter((_, i) => i !== idx) });
  };

  const moveSection = (idx, dir) => {
    const next = [...form.sections];
    const j = idx + dir;
    if (j < 0 || j >= next.length) return;
    [next[idx], next[j]] = [next[j], next[idx]];
    setForm({ ...form, sections: next });
  };

  const save = async () => {
    if (!form.title.trim()) { toast.error('Titel darf nicht leer sein'); return; }
    if (!form.sections.length) { toast.error('Mindestens ein Abschnitt erforderlich'); return; }
    setSaving(true);
    try {
      const r = await api.put(`/admin/legal/${docType}`, {
        title: form.title.trim(),
        subtitle: form.subtitle.trim(),
        sections: form.sections,
        change_notes: changeNotes.trim(),
      });
      toast.success(`Gespeichert als Version ${r.data.version}`);
      setChangeNotes('');
      await loadAll();
    } catch (e) {
      toast.error('Speichern fehlgeschlagen');
    }
    setSaving(false);
  };

  const restoreVersion = async (versionId, versionNum) => {
    if (!confirm(`Wirklich auf Version ${versionNum} zurücksetzen? Es wird automatisch eine neue Version erstellt, die Audit-Historie bleibt erhalten.`)) return;
    try {
      const r = await api.post(`/admin/legal/${docType}/restore/${versionId}`);
      toast.success(`Auf Version ${versionNum} zurückgesetzt — neue aktuelle Version: ${r.data.version}`);
      setShowHistory(false);
      await loadAll();
    } catch {
      toast.error('Wiederherstellung fehlgeschlagen');
    }
  };

  const showDiff = async (versionId) => {
    try {
      const r = await api.get(`/admin/legal/${docType}/versions/${versionId}`);
      setDiffVersion(r.data);
    } catch {
      toast.error('Konnte Version nicht laden');
    }
  };

  if (!doc) {
    return (
      <AdminLayout title="Lädt…">
        <div className="adm-card">Dokument wird geladen…</div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title={DOC_TITLES[docType] || 'Dokument'}>
      <div className="adm-legal-editor" data-testid="admin-legal-editor">
        {/* Top bar */}
        <div className="adm-legal-toolbar">
          <Link href="/admin/legal" className="adm-btn adm-btn-ghost" data-testid="admin-legal-back">
            <ArrowLeft size={14} /> Zurück
          </Link>
          <div className="adm-legal-toolbar-info">
            <Icon size={18} style={{ color: '#4db6ac' }} />
            <strong>{DOC_TITLES[docType]}</strong>
            <span className="adm-legal-version-badge" data-testid="admin-legal-current-version">v{doc.version}</span>
            <span className="adm-legal-meta-text">
              · zuletzt bearbeitet {formatDate(doc.updated_at)} von {doc.updated_by_name || doc.updated_by_email || 'System'}
            </span>
          </div>
          <div className="adm-legal-toolbar-actions">
            <a href={`/${docType}`} target="_blank" rel="noopener noreferrer" className="adm-btn adm-btn-ghost" data-testid="admin-legal-preview">
              <Eye size={14} /> Vorschau
            </a>
            <button onClick={() => setShowHistory(true)} className="adm-btn adm-btn-secondary" data-testid="admin-legal-history-btn">
              <History size={14} /> Historie ({versions.length})
            </button>
          </div>
        </div>

        {/* Form */}
        <div className="adm-card" data-testid="admin-legal-form">
          <label className="adm-label">Titel *</label>
          <input
            className="adm-input"
            value={form.title}
            onChange={e => setForm({ ...form, title: e.target.value })}
            data-testid="admin-legal-title"
          />

          <label className="adm-label" style={{ marginTop: '1rem' }}>Untertitel / Stand</label>
          <input
            className="adm-input"
            value={form.subtitle}
            onChange={e => setForm({ ...form, subtitle: e.target.value })}
            placeholder="z.B. Stand: Februar 2026 · …"
            data-testid="admin-legal-subtitle"
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2rem', marginBottom: '1rem' }}>
            <h3 className="adm-card-title" style={{ margin: 0 }}>Abschnitte ({form.sections.length})</h3>
            <button onClick={addSection} className="adm-btn adm-btn-secondary" data-testid="admin-legal-add-section">
              <Plus size={14} /> Abschnitt hinzufügen
            </button>
          </div>

          <div className="adm-legal-sections">
            {form.sections.map((s, idx) => (
              <div key={idx} className="adm-legal-section-card" data-testid={`admin-legal-section-${idx}`}>
                <div className="adm-legal-section-header">
                  <span className="adm-legal-section-num">#{idx + 1}</span>
                  <input
                    className="adm-input adm-legal-section-heading"
                    value={s.heading}
                    onChange={e => updateSection(idx, 'heading', e.target.value)}
                    placeholder="Überschrift (z.B. § 1 Geltungsbereich)"
                    data-testid={`admin-legal-section-heading-${idx}`}
                  />
                  <div className="adm-legal-section-actions">
                    <button onClick={() => moveSection(idx, -1)} disabled={idx === 0} className="adm-btn-icon" title="Nach oben">
                      <ArrowUp size={14} />
                    </button>
                    <button onClick={() => moveSection(idx, 1)} disabled={idx === form.sections.length - 1} className="adm-btn-icon" title="Nach unten">
                      <ArrowDown size={14} />
                    </button>
                    <button onClick={() => removeSection(idx)} className="adm-btn-icon adm-btn-danger" title="Entfernen" data-testid={`admin-legal-section-remove-${idx}`}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
                <textarea
                  className="adm-input adm-legal-section-content"
                  rows={Math.min(20, Math.max(4, s.content.split('\n').length + 1))}
                  value={s.content}
                  onChange={e => updateSection(idx, 'content', e.target.value)}
                  placeholder={'Inhalt …\n\nFormat-Hilfe:\n- Aufzählung mit "- " am Zeilenanfang\n- **fett** mit Doppelsternen\n- [Link-Text](https://…) für Links\n- Leerzeile = neuer Absatz'}
                  data-testid={`admin-legal-section-content-${idx}`}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Save bar */}
        <div className="adm-card adm-legal-save-card" data-testid="admin-legal-save-card">
          <label className="adm-label">Änderungsnotiz (optional, fürs Audit-Log)</label>
          <input
            className="adm-input"
            value={changeNotes}
            onChange={e => setChangeNotes(e.target.value)}
            placeholder="z.B. Anzahlung von 30% auf 25% reduziert"
            data-testid="admin-legal-change-notes"
          />
          <button
            onClick={save}
            disabled={saving}
            className="adm-btn adm-btn-primary"
            style={{ marginTop: '1rem' }}
            data-testid="admin-legal-save-btn"
          >
            <Save size={14} /> {saving ? 'Speichert…' : `Als Version ${doc.version + 1} speichern`}
          </button>
        </div>
      </div>

      {/* History drawer */}
      {showHistory && (
        <div className="adm-modal-overlay" onClick={() => setShowHistory(false)} data-testid="admin-legal-history-modal">
          <div className="adm-modal adm-modal-wide" onClick={e => e.stopPropagation()}>
            <div className="adm-modal-header">
              <h2><History size={18} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} /> Versionsverlauf — {DOC_TITLES[docType]}</h2>
              <button onClick={() => setShowHistory(false)} className="adm-btn-icon" data-testid="admin-legal-history-close">
                <X size={18} />
              </button>
            </div>
            <div className="adm-modal-body">
              <p style={{ color: 'var(--adm-text-muted, #94a3b8)', fontSize: '0.88rem', marginBottom: '1rem' }}>
                Lückenlose Audit-Historie. Jede Speicherung ist signiert mit Admin, Timestamp und Diff zur Vorversion.
                Klicken Sie auf eine Version, um sie wiederherzustellen oder den Diff einzusehen.
              </p>
              <div className="adm-legal-timeline">
                {versions.map(v => (
                  <div key={v.id} className={`adm-legal-version-row ${v.version === doc.version ? 'is-current' : ''}`} data-testid={`admin-legal-version-${v.version}`}>
                    <div className="adm-legal-version-marker">
                      <GitCommit size={14} />
                    </div>
                    <div className="adm-legal-version-body">
                      <div className="adm-legal-version-headline">
                        <strong>v{v.version}</strong>
                        {v.version === doc.version && <span className="adm-legal-version-current-pill">aktuell</span>}
                        {v.restored_from_version && (
                          <span className="adm-legal-version-restore-pill">
                            wiederhergestellt aus v{v.restored_from_version}
                          </span>
                        )}
                        <span className="adm-legal-version-diff">
                          <span style={{ color: '#4ade80' }}>+{v.diff_added || 0}</span>{' '}
                          <span style={{ color: '#f87171' }}>−{v.diff_removed || 0}</span>
                        </span>
                      </div>
                      <div className="adm-legal-version-meta">
                        {formatDate(v.created_at)} · {v.admin_name || v.admin_email}
                      </div>
                      {v.change_notes && (
                        <div className="adm-legal-version-notes">{v.change_notes}</div>
                      )}
                    </div>
                    <div className="adm-legal-version-actions">
                      <button onClick={() => showDiff(v.id)} className="adm-btn adm-btn-ghost adm-btn-sm" data-testid={`admin-legal-version-diff-${v.version}`}>
                        Diff
                      </button>
                      {v.version !== doc.version && (
                        <button onClick={() => restoreVersion(v.id, v.version)} className="adm-btn adm-btn-secondary adm-btn-sm" data-testid={`admin-legal-version-restore-${v.version}`}>
                          <RotateCcw size={12} /> Wiederherstellen
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Diff modal */}
      {diffVersion && (
        <div className="adm-modal-overlay" onClick={() => setDiffVersion(null)} data-testid="admin-legal-diff-modal">
          <div className="adm-modal adm-modal-wide" onClick={e => e.stopPropagation()}>
            <div className="adm-modal-header">
              <h2>Diff — v{diffVersion.version}</h2>
              <button onClick={() => setDiffVersion(null)} className="adm-btn-icon">
                <X size={18} />
              </button>
            </div>
            <div className="adm-modal-body">
              <div className="adm-legal-version-meta" style={{ marginBottom: '1rem' }}>
                {formatDate(diffVersion.created_at)} · {diffVersion.admin_name || diffVersion.admin_email}
                {diffVersion.change_notes && <> · <em>{diffVersion.change_notes}</em></>}
              </div>
              <pre className="adm-legal-diff-pre" data-testid="admin-legal-diff-pre">
                {diffVersion.diff_text || '(Kein Diff verfügbar — initiale Version)'}
              </pre>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}
