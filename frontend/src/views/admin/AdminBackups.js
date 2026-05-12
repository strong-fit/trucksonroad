"use client";
import { useState, useEffect, useCallback } from 'react';
import { AdminLayout } from '@/views/admin/AdminDashboard';
import api from '@/lib/api';
import { toast } from 'sonner';
import {
  Database, Cloud, RefreshCw, Play, Trash2, Download,
  CheckCircle2, AlertCircle, Settings as SettingsIcon, HardDrive, Eye, EyeOff,
} from 'lucide-react';

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('de-CH', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export default function AdminBackups() {
  const [localBackups, setLocalBackups] = useState([]);
  const [cloudBackups, setCloudBackups] = useState([]);
  const [cloudCount, setCloudCount] = useState(0);
  const [cfg, setCfg] = useState(null);
  const [cfgDraft, setCfgDraft] = useState({});
  const [showSecret, setShowSecret] = useState(false);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [retentionLocal, setRetentionLocal] = useState(14);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [a, b, c] = await Promise.all([
        api.get('/admin/backups'),
        api.get('/admin/backups/cloud/config'),
        api.get('/admin/backups/cloud/list').catch(() => ({ data: { backups: [], count: 0 } })),
      ]);
      setLocalBackups(a.data.backups || []);
      setRetentionLocal(a.data.retention_local || 14);
      setCfg(a.data && b.data ? b.data : null);
      setCfgDraft({
        enabled: b.data.enabled,
        endpoint: b.data.endpoint,
        access_key: b.data.access_key,
        secret_key: '',
        bucket: b.data.bucket,
        prefix: b.data.prefix,
        region: b.data.region,
        retention_days: b.data.retention_days,
      });
      setCloudBackups(c.data.backups || []);
      setCloudCount(c.data.count || 0);
    } catch {
      toast.error('Daten konnten nicht geladen werden');
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const runBackup = async () => {
    setRunning(true);
    try {
      const r = await api.post('/admin/backups');
      const local = r.data.local;
      const cloud = r.data.cloud;
      if (cloud && cloud.ok) {
        toast.success(`Backup OK · ${local.filename} (${local.size_mb} MB) → Cloud`);
      } else if (cloud && !cloud.ok) {
        toast.warning(`Lokal OK · Cloud-Upload fehlgeschlagen: ${cloud.error || 'unbekannt'}`);
      } else {
        toast.success(`Lokal-Backup OK · ${local.filename}`);
      }
      await loadAll();
    } catch (e) {
      toast.error('Backup fehlgeschlagen: ' + (e.response?.data?.detail || e.message));
    }
    setRunning(false);
  };

  const testConnection = async () => {
    setTesting(true);
    try {
      const r = await api.post('/admin/backups/cloud/test');
      if (r.data.ok) toast.success(r.data.message);
      else toast.error(r.data.message);
    } catch (e) {
      toast.error('Test fehlgeschlagen: ' + e.message);
    }
    setTesting(false);
  };

  const saveCfg = async () => {
    setSaving(true);
    try {
      await api.put('/admin/backups/cloud/config', cfgDraft);
      toast.success('Cloud-Konfiguration gespeichert');
      setCfgDraft({ ...cfgDraft, secret_key: '' });
      await loadAll();
    } catch (e) {
      toast.error('Speichern fehlgeschlagen');
    }
    setSaving(false);
  };

  const deleteLocal = async (filename) => {
    if (!confirm(`Lokales Backup ${filename} wirklich löschen?`)) return;
    try {
      await api.delete(`/admin/backups/${encodeURIComponent(filename)}`);
      toast.success('Gelöscht');
      await loadAll();
    } catch { toast.error('Löschen fehlgeschlagen'); }
  };

  const deleteCloud = async (key) => {
    if (!confirm(`Cloud-Backup ${key} wirklich löschen?`)) return;
    try {
      await api.delete(`/admin/backups/cloud/${encodeURIComponent(key)}`);
      toast.success('Aus Cloud gelöscht');
      await loadAll();
    } catch { toast.error('Löschen fehlgeschlagen'); }
  };

  const downloadLocal = (filename) => {
    const url = `${api.defaults.baseURL}/admin/backups/download/${encodeURIComponent(filename)}`;
    window.open(url, '_blank');
  };

  return (
    <AdminLayout title="Backups & Cloud">
      <div className="adm-card" data-testid="admin-backups-intro">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 className="adm-card-title">DB-Backup-System</h2>
            <p style={{ color: 'var(--adm-text-muted,#94a3b8)', marginTop: '0.4rem', fontSize: '0.88rem', lineHeight: 1.55 }}>
              Tägliche automatische Sicherung um <strong>03:00 Europe/Zurich</strong> · {retentionLocal} Tage lokal · 30 Tage Cloud (Infomaniak Swiss Backup S3).
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button onClick={loadAll} className="adm-btn adm-btn-ghost" data-testid="admin-backups-refresh">
              <RefreshCw size={14} /> Aktualisieren
            </button>
            <button onClick={runBackup} disabled={running} className="adm-btn adm-btn-primary" data-testid="admin-backups-run-now">
              <Play size={14} /> {running ? 'Backup läuft...' : 'Backup jetzt starten'}
            </button>
          </div>
        </div>
      </div>

      {/* Cloud config */}
      <div className="adm-card" style={{ marginTop: '1.5rem' }} data-testid="admin-backups-cloud-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
          <Cloud size={18} style={{ color: '#4db6ac' }} />
          <h3 className="adm-card-title" style={{ margin: 0 }}>Infomaniak Swiss Backup (S3)</h3>
          {cfg && cfg.enabled ? (
            <span className="adm-legal-version-badge" style={{ background: 'rgba(74,222,128,0.15)', color: '#4ade80' }}>aktiv</span>
          ) : (
            <span className="adm-legal-version-badge" style={{ background: 'rgba(248,113,113,0.12)', color: '#f87171' }}>deaktiviert</span>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div>
            <label className="adm-label">Endpoint</label>
            <input
              className="adm-input"
              value={cfgDraft.endpoint || ''}
              onChange={e => setCfgDraft({ ...cfgDraft, endpoint: e.target.value })}
              placeholder="https://s3.swiss-backup04.infomaniak.com"
              data-testid="admin-backups-endpoint"
            />
          </div>
          <div>
            <label className="adm-label">Bucket</label>
            <input
              className="adm-input"
              value={cfgDraft.bucket || ''}
              onChange={e => setCfgDraft({ ...cfgDraft, bucket: e.target.value })}
              placeholder="emergent-apps-backup"
              data-testid="admin-backups-bucket"
            />
          </div>
          <div>
            <label className="adm-label">Prefix (App-Trennung)</label>
            <input
              className="adm-input"
              value={cfgDraft.prefix || ''}
              onChange={e => setCfgDraft({ ...cfgDraft, prefix: e.target.value })}
              placeholder="truck"
              data-testid="admin-backups-prefix"
            />
          </div>
          <div>
            <label className="adm-label">Region</label>
            <input
              className="adm-input"
              value={cfgDraft.region || ''}
              onChange={e => setCfgDraft({ ...cfgDraft, region: e.target.value })}
              placeholder="us-east-1"
            />
          </div>
          <div>
            <label className="adm-label">Access Key</label>
            <input
              className="adm-input"
              value={cfgDraft.access_key || ''}
              onChange={e => setCfgDraft({ ...cfgDraft, access_key: e.target.value })}
              data-testid="admin-backups-access-key"
            />
          </div>
          <div>
            <label className="adm-label">
              Secret Key
              {cfg && cfg.secret_key_set && (
                <span style={{ marginLeft: '0.5rem', fontSize: '0.7rem', color: 'var(--adm-text-muted,#94a3b8)', textTransform: 'none' }}>
                  (gesetzt: {cfg.secret_key_masked} – leer lassen zum Beibehalten)
                </span>
              )}
            </label>
            <div style={{ position: 'relative' }}>
              <input
                className="adm-input"
                type={showSecret ? 'text' : 'password'}
                value={cfgDraft.secret_key || ''}
                onChange={e => setCfgDraft({ ...cfgDraft, secret_key: e.target.value })}
                placeholder={cfg?.secret_key_set ? '(unverändert)' : 'Secret Key eingeben'}
                data-testid="admin-backups-secret-key"
              />
              <button
                type="button"
                onClick={() => setShowSecret(v => !v)}
                style={{ position: 'absolute', right: '0.5rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--adm-text-muted,#94a3b8)' }}
              >
                {showSecret ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
          </div>
          <div>
            <label className="adm-label">Cloud-Retention (Tage)</label>
            <input
              type="number"
              min="1"
              max="365"
              className="adm-input"
              value={cfgDraft.retention_days || 30}
              onChange={e => setCfgDraft({ ...cfgDraft, retention_days: parseInt(e.target.value) || 30 })}
              data-testid="admin-backups-retention"
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer', padding: '0.5rem 0' }}>
              <input
                type="checkbox"
                checked={!!cfgDraft.enabled}
                onChange={e => setCfgDraft({ ...cfgDraft, enabled: e.target.checked })}
                data-testid="admin-backups-enabled-toggle"
              />
              <span style={{ fontSize: '0.92rem' }}>Cloud-Upload aktivieren</span>
            </label>
          </div>
        </div>

        <div style={{ marginTop: '1.2rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button onClick={testConnection} disabled={testing} className="adm-btn adm-btn-secondary" data-testid="admin-backups-test-conn">
            <CheckCircle2 size={14} /> {testing ? 'Teste...' : 'Verbindung testen'}
          </button>
          <button onClick={saveCfg} disabled={saving} className="adm-btn adm-btn-primary" data-testid="admin-backups-save-cfg">
            <SettingsIcon size={14} /> {saving ? 'Speichert...' : 'Konfiguration speichern'}
          </button>
        </div>
      </div>

      {/* Local backups */}
      <div className="adm-card" style={{ marginTop: '1.5rem' }} data-testid="admin-backups-local">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
          <HardDrive size={18} style={{ color: '#d4af37' }} />
          <h3 className="adm-card-title" style={{ margin: 0 }}>Lokale Backups</h3>
          <span style={{ color: 'var(--adm-text-muted,#94a3b8)', fontSize: '0.82rem' }}>
            {localBackups.length} Archiv(e) · Rotation alle {retentionLocal} Tage
          </span>
        </div>
        {localBackups.length === 0 ? (
          <p style={{ color: 'var(--adm-text-muted,#94a3b8)', fontSize: '0.9rem', textAlign: 'center', padding: '1.5rem 0' }}>
            Noch keine lokalen Backups. Starten Sie das erste manuell über „Backup jetzt starten".
          </p>
        ) : (
          <div className="adm-legal-timeline">
            {localBackups.map(b => (
              <div key={b.filename} className="adm-legal-version-row" data-testid={`admin-backup-local-${b.filename}`}>
                <div className="adm-legal-version-marker"><Database size={14} /></div>
                <div className="adm-legal-version-body">
                  <div className="adm-legal-version-headline">
                    <strong style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.86rem' }}>{b.filename}</strong>
                    <span className="adm-legal-version-diff">{b.size_mb} MB</span>
                  </div>
                  <div className="adm-legal-version-meta">{formatDate(b.created_at)}</div>
                </div>
                <div className="adm-legal-version-actions">
                  <button onClick={() => downloadLocal(b.filename)} className="adm-btn adm-btn-ghost adm-btn-sm" title="Download">
                    <Download size={12} />
                  </button>
                  <button onClick={() => deleteLocal(b.filename)} className="adm-btn-icon adm-btn-danger" title="Löschen">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Cloud backups */}
      <div className="adm-card" style={{ marginTop: '1.5rem' }} data-testid="admin-backups-cloud-list">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
          <Cloud size={18} style={{ color: '#4db6ac' }} />
          <h3 className="adm-card-title" style={{ margin: 0 }}>Cloud-Backups</h3>
          <span style={{ color: 'var(--adm-text-muted,#94a3b8)', fontSize: '0.82rem' }}>
            {cloudCount} Archiv(e) bei Infomaniak Swiss Backup
          </span>
        </div>
        {!cfg?.enabled ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--adm-text-muted,#94a3b8)', fontSize: '0.88rem', padding: '1rem 0' }}>
            <AlertCircle size={16} /> Cloud-Upload ist deaktiviert. Aktivieren Sie es oben.
          </div>
        ) : cloudBackups.length === 0 ? (
          <p style={{ color: 'var(--adm-text-muted,#94a3b8)', fontSize: '0.9rem', textAlign: 'center', padding: '1.5rem 0' }}>
            Noch keine Cloud-Backups vorhanden.
          </p>
        ) : (
          <div className="adm-legal-timeline">
            {cloudBackups.map(b => (
              <div key={b.key} className="adm-legal-version-row" data-testid={`admin-backup-cloud-${b.filename}`}>
                <div className="adm-legal-version-marker" style={{ background: 'rgba(77,182,172,0.15)' }}>
                  <Cloud size={14} />
                </div>
                <div className="adm-legal-version-body">
                  <div className="adm-legal-version-headline">
                    <strong style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.86rem' }}>{b.filename}</strong>
                    <span className="adm-legal-version-diff">{b.size_mb} MB</span>
                  </div>
                  <div className="adm-legal-version-meta" style={{ fontSize: '0.74rem' }}>
                    {b.key} · {formatDate(b.last_modified)}
                  </div>
                </div>
                <div className="adm-legal-version-actions">
                  <button onClick={() => deleteCloud(b.key)} className="adm-btn-icon adm-btn-danger" title="Aus Cloud löschen">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
