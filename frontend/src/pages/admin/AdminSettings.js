import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Save, Send, Building2, Server, Eye, Download, Instagram, Plus, Trash2, Globe, Facebook, Linkedin, Zap } from 'lucide-react';

export default function AdminSettings() {
  const { t } = useLanguage();
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [testingSend, setTestingSend] = useState(false);
  const [preview, setPreview] = useState(null);
  const [previewType, setPreviewType] = useState('confirmation');

  useEffect(() => {
    api.get('/admin/settings').then(r => setSettings(r.data)).catch(() => {});
  }, []);

  const loadPreview = async () => {
    try {
      const r = await api.get('/admin/email-preview');
      setPreview(r.data);
    } catch { toast.error('Vorschau konnte nicht geladen werden'); }
  };

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

  if (!settings) return <AdminLayout title={t('admin_settings')}><div className="adm-empty">{t('loading')}</div></AdminLayout>;

  return (
    <AdminLayout title={t('admin_settings')}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
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

        <div className="adm-detail" data-testid="settings-email">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Server size={18} /> E-Mail (SMTP)</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem' }}>
              <input type="checkbox" checked={settings.email_notifications || false} onChange={e => update('email_notifications', e.target.checked)} data-testid="settings-email-enabled" />
              E-Mail-Benachrichtigungen aktiviert
            </label>
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

      <div style={{ marginTop: '1.25rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* Booking Auto-Confirmation */}
        <div className="adm-detail" data-testid="settings-booking">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Zap size={18} /> Buchungseinstellungen</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <label style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem' }}>
              <input type="checkbox" checked={settings.auto_confirmation || false} onChange={e => update('auto_confirmation', e.target.checked)} data-testid="settings-auto-confirmation" style={{ marginTop: '0.15rem' }} />
              <div>
                <div style={{ fontWeight: 600 }}>Automatische Bestätigung</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--adm-text-secondary)', marginTop: '0.2rem' }}>
                  Wenn aktiviert, werden neue Anfragen automatisch bestätigt. Wenn deaktiviert, müssen Anfragen manuell bestätigt werden.
                </div>
              </div>
            </label>
            <div style={{ padding: '0.6rem 0.8rem', borderRadius: '6px', fontSize: '0.78rem', background: settings.auto_confirmation ? '#dcfce7' : '#fef3c7', color: settings.auto_confirmation ? '#166534' : '#92400e' }}>
              {settings.auto_confirmation
                ? 'Modus: AUTOMATISCH – Anfragen werden sofort bestätigt.'
                : 'Modus: MANUELL – Anfragen müssen im Admin-Bereich geprüft und bestätigt werden.'}
            </div>
            <div style={{ marginTop: '0.5rem', borderTop: '1px solid var(--adm-border)', paddingTop: '0.75rem' }}>
              <div className="adm-form-label">Event-Erinnerung (Tage vorher)</div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <input className="adm-input" type="number" min="0" max="30" style={{ width: '80px' }} value={settings.event_reminder_days ?? 3} onChange={e => update('event_reminder_days', parseInt(e.target.value) || 0)} data-testid="settings-reminder-days" />
                <span style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)' }}>Tage vor dem Event wird eine Erinnerung an den Kunden gesendet. 0 = deaktiviert.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Social Media */}
        <div className="adm-detail" data-testid="settings-social">
          <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Globe size={18} /> Social Media & SEO</span>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--adm-text-secondary)', marginBottom: '0.75rem' }}>
            Diese Links werden automatisch in die strukturierten Daten (JSON-LD) eingebettet, damit Google und KI-Suchmaschinen euer Unternehmen besser finden.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div>
              <div className="adm-form-label">Google Business Profil</div>
              <input className="adm-input" value={settings.social_google_business || ''} onChange={e => update('social_google_business', e.target.value)} placeholder="https://g.page/truckonroad" data-testid="settings-google-business" />
            </div>
            <div>
              <div className="adm-form-label">Instagram</div>
              <input className="adm-input" value={settings.social_instagram || ''} onChange={e => update('social_instagram', e.target.value)} placeholder="https://instagram.com/truckonroad" data-testid="settings-social-instagram" />
            </div>
            <div>
              <div className="adm-form-label">Facebook</div>
              <input className="adm-input" value={settings.social_facebook || ''} onChange={e => update('social_facebook', e.target.value)} placeholder="https://facebook.com/truckonroad" data-testid="settings-social-facebook" />
            </div>
            <div>
              <div className="adm-form-label">TikTok</div>
              <input className="adm-input" value={settings.social_tiktok || ''} onChange={e => update('social_tiktok', e.target.value)} placeholder="https://tiktok.com/@truckonroad" data-testid="settings-social-tiktok" />
            </div>
            <div>
              <div className="adm-form-label">LinkedIn</div>
              <input className="adm-input" value={settings.social_linkedin || ''} onChange={e => update('social_linkedin', e.target.value)} placeholder="https://linkedin.com/company/truckonroad" data-testid="settings-social-linkedin" />
            </div>
            <div style={{ marginTop: '0.5rem', borderTop: '1px solid var(--adm-border)', paddingTop: '0.75rem' }}>
              <div className="adm-form-label">Google Search Console Verification</div>
              <input className="adm-input" value={settings.google_verification || ''} onChange={e => update('google_verification', e.target.value)} placeholder="z.B. abc123def456..." data-testid="settings-google-verification" />
              <div style={{ fontSize: '0.72rem', color: 'var(--adm-text-secondary)', marginTop: '0.2rem' }}>
                Kopiere den content-Wert vom Google HTML-Tag hierher (nur den Code, ohne Anführungszeichen).
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

      {/* Email Preview */}
      <div className="adm-detail" style={{ marginTop: '1.5rem' }} data-testid="email-preview-section">
        <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Eye size={18} /> E-Mail Vorschau</span>
          <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={loadPreview} data-testid="load-preview-btn">
            <Eye size={13} /> Vorschau laden
          </button>
        </div>

        {preview && (
          <>
            <div className="adm-filters" style={{ marginBottom: '1rem', flexWrap: 'wrap' }}>
              <button className={`adm-filter-btn ${previewType === 'confirmation' ? 'active' : ''}`} onClick={() => setPreviewType('confirmation')} data-testid="preview-confirmation-btn">
                Bestaetigungsmail
              </button>
              <button className={`adm-filter-btn ${previewType === 'notification' ? 'active' : ''}`} onClick={() => setPreviewType('notification')} data-testid="preview-notification-btn">
                Admin-Info
              </button>
              <button className={`adm-filter-btn ${previewType === 'status_confirmed' ? 'active' : ''}`} onClick={() => setPreviewType('status_confirmed')}>
                Buchung bestaetigt
              </button>
              <button className={`adm-filter-btn ${previewType === 'status_completed' ? 'active' : ''}`} onClick={() => setPreviewType('status_completed')}>
                Abgeschlossen
              </button>
              <button className={`adm-filter-btn ${previewType === 'invoice_sent' ? 'active' : ''}`} onClick={() => setPreviewType('invoice_sent')}>
                Rechnung
              </button>
              <button className={`adm-filter-btn ${previewType === 'invoice_paid' ? 'active' : ''}`} onClick={() => setPreviewType('invoice_paid')}>
                Zahlung OK
              </button>
              <button className={`adm-filter-btn ${previewType === 'file_upload' ? 'active' : ''}`} onClick={() => setPreviewType('file_upload')}>
                Datei-Upload
              </button>
              <button className={`adm-filter-btn ${previewType === 'event_reminder' ? 'active' : ''}`} onClick={() => setPreviewType('event_reminder')}>
                Erinnerung
              </button>
            </div>
            <div style={{ border: '1px solid var(--adm-border)', borderRadius: '8px', padding: '1rem', background: '#fff' }} data-testid="email-preview-content">
              <div dangerouslySetInnerHTML={{ __html: preview[previewType] || preview.confirmation }} />
            </div>
          </>
        )}

        {!preview && (
          <div className="adm-empty" style={{ padding: '1.5rem' }}>
            Klicken Sie auf "Vorschau laden", um die E-Mail-Templates zu sehen.
          </div>
        )}
      </div>

      {/* PDF Download */}
      <div className="adm-detail" style={{ marginTop: '1.25rem' }} data-testid="pdf-download-section">
        <div className="adm-detail-header" style={{ borderBottom: 'none', paddingBottom: 0, marginBottom: 0 }}>
          <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Download size={18} /> Veranstalter-PDF</span>
          <a href={`${process.env.REACT_APP_BACKEND_URL}/api/download/veranstalter-pdf`} target="_blank" rel="noopener noreferrer" className="adm-btn adm-btn-primary adm-btn-sm" data-testid="download-pdf-btn">
            <Download size={13} /> PDF herunterladen
          </a>
        </div>
      </div>

      {/* Instagram Gallery Settings */}
      <div className="adm-detail" style={{ marginTop: '1.25rem' }} data-testid="instagram-settings">
        <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Instagram size={18} /> Instagram Feed</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div>
            <div className="adm-form-label">Instagram Benutzername</div>
            <input className="adm-input" value={settings.instagram_username || ''} onChange={e => update('instagram_username', e.target.value)} placeholder="truckonroad" data-testid="settings-instagram-username" />
          </div>
          <div>
            <div className="adm-form-label">Bilder (URLs) - werden auf der Homepage als Galerie angezeigt</div>
            {(settings.instagram_images || []).map((img, idx) => (
              <div key={idx} style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.3rem' }}>
                <input className="adm-input" value={img} onChange={e => {
                  const imgs = [...(settings.instagram_images || [])];
                  imgs[idx] = e.target.value;
                  update('instagram_images', imgs);
                }} placeholder="https://..." />
                <button className="adm-btn adm-btn-danger adm-btn-sm" onClick={() => {
                  const imgs = [...(settings.instagram_images || [])];
                  imgs.splice(idx, 1);
                  update('instagram_images', imgs);
                }} style={{ padding: '0.25rem 0.4rem' }}><Trash2 size={13} /></button>
              </div>
            ))}
            <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => update('instagram_images', [...(settings.instagram_images || []), ''])} data-testid="add-insta-image-btn">
              <Plus size={13} /> Bild hinzufuegen
            </button>
          </div>
        </div>
      </div>

      {/* Perplexity API Key for Event Scout */}
      <div className="adm-detail" style={{ marginTop: '1.25rem' }} data-testid="perplexity-settings">
        <div className="adm-detail-header" style={{ borderBottom: '1px solid var(--adm-border)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          <span className="adm-detail-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Zap size={18} /> KI Event-Scout (Perplexity)</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div>
            <div className="adm-form-label">Perplexity API-Key</div>
            <input className="adm-input" type="password" value={settings.perplexity_api_key || ''} onChange={e => update('perplexity_api_key', e.target.value)} placeholder="pplx-..." data-testid="settings-perplexity-key" />
            <div style={{ fontSize: '0.72rem', color: 'var(--adm-text-muted)', marginTop: '0.3rem' }}>
              API-Key von <a href="https://www.perplexity.ai/settings/api" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--adm-accent)' }}>perplexity.ai/settings/api</a> – wird fuer den KI Event-Scout verwendet
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
