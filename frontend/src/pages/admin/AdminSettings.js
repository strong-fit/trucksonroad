import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Save, Send, Building2, Mail, Phone, MapPin, MessageSquare, Server } from 'lucide-react';

export default function AdminSettings() {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [testingSend, setTestingSend] = useState(false);

  useEffect(() => {
    api.get('/admin/settings').then(r => setSettings(r.data)).catch(() => {});
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await api.put('/admin/settings', settings);
      toast.success('Einstellungen gespeichert');
    } catch { toast.error('Fehler beim Speichern'); }
    setSaving(false);
  };

  const sendTest = async () => {
    if (!testEmail) return;
    setTestingSend(true);
    try {
      await api.post('/admin/settings/test-email', { to: testEmail });
      toast.success('Test-E-Mail wird gesendet');
    } catch { toast.error('Fehler beim Senden'); }
    setTestingSend(false);
  };

  const update = (key, value) => setSettings(prev => ({ ...prev, [key]: value }));

  if (!settings) return <AdminLayout title="Einstellungen"><div className="adm-empty">Laden...</div></AdminLayout>;

  return (
    <AdminLayout title="Einstellungen">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* Company Info */}
        <div className="adm-detail" data-testid="settings-company">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Building2 size={18} /> Firmendaten</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div>
              <div className="adm-form-label">Firmenname</div>
              <input className="adm-input" value={settings.company_name || ''} onChange={e => update('company_name', e.target.value)} data-testid="settings-company-name" />
            </div>
            <div>
              <div className="adm-form-label">Adresse</div>
              <input className="adm-input" value={settings.company_address || ''} onChange={e => update('company_address', e.target.value)} data-testid="settings-company-address" />
            </div>
            <div>
              <div className="adm-form-label">Telefon</div>
              <input className="adm-input" value={settings.company_phone || ''} onChange={e => update('company_phone', e.target.value)} data-testid="settings-company-phone" />
            </div>
            <div>
              <div className="adm-form-label">E-Mail</div>
              <input className="adm-input" value={settings.company_email || ''} onChange={e => update('company_email', e.target.value)} data-testid="settings-company-email" />
            </div>
            <div>
              <div className="adm-form-label">WhatsApp Nummer</div>
              <input className="adm-input" value={settings.whatsapp_number || ''} onChange={e => update('whatsapp_number', e.target.value)} placeholder="+41791234567" data-testid="settings-whatsapp" />
            </div>
          </div>
        </div>

        {/* SMTP Settings */}
        <div className="adm-detail" data-testid="settings-email">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Server size={18} /> E-Mail (SMTP)</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem' }}>
                <input type="checkbox" checked={settings.email_notifications || false} onChange={e => update('email_notifications', e.target.checked)} data-testid="settings-email-enabled" />
                E-Mail-Benachrichtigungen aktiviert
              </label>
            </div>
            <div>
              <div className="adm-form-label">Benachrichtigung an (Admin E-Mail)</div>
              <input className="adm-input" type="email" value={settings.notification_email || ''} onChange={e => update('notification_email', e.target.value)} placeholder="admin@truckonroad.ch" data-testid="settings-notification-email" />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px', gap: '0.5rem' }}>
              <div>
                <div className="adm-form-label">SMTP Host</div>
                <input className="adm-input" value={settings.smtp_host || ''} onChange={e => update('smtp_host', e.target.value)} data-testid="settings-smtp-host" />
              </div>
              <div>
                <div className="adm-form-label">Port</div>
                <input className="adm-input" type="number" value={settings.smtp_port || 587} onChange={e => update('smtp_port', parseInt(e.target.value))} data-testid="settings-smtp-port" />
              </div>
            </div>
            <div>
              <div className="adm-form-label">SMTP E-Mail (Absender)</div>
              <input className="adm-input" type="email" value={settings.smtp_email || ''} onChange={e => update('smtp_email', e.target.value)} placeholder="truckonroad@gmail.com" data-testid="settings-smtp-email" />
            </div>
            <div>
              <div className="adm-form-label">SMTP Passwort (App-Passwort)</div>
              <input className="adm-input" type="password" value={settings.smtp_password || ''} onChange={e => update('smtp_password', e.target.value)} placeholder="xxxx xxxx xxxx xxxx" data-testid="settings-smtp-password" />
            </div>
            <div style={{ borderTop: '1px solid var(--adm-border)', paddingTop: '0.75rem', marginTop: '0.25rem' }}>
              <div className="adm-form-label">Test-E-Mail senden</div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input className="adm-input" type="email" value={testEmail} onChange={e => setTestEmail(e.target.value)} placeholder="test@beispiel.ch" data-testid="settings-test-email-input" />
                <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={sendTest} disabled={testingSend} data-testid="settings-test-email-btn" style={{ whiteSpace: 'nowrap' }}>
                  <Send size={13} /> Test
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '1.25rem', display: 'flex', justifyContent: 'flex-end' }}>
        <button className="adm-btn adm-btn-primary" onClick={save} disabled={saving} data-testid="settings-save-btn">
          <Save size={15} /> {saving ? 'Speichern...' : 'Einstellungen speichern'}
        </button>
      </div>
    </AdminLayout>
  );
}
