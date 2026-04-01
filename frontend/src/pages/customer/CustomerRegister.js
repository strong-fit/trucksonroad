import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { UserPlus } from 'lucide-react';

export default function CustomerRegister() {
  const { checkAuth } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', password: '', password2: '', company: '', phone: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.password2) { toast.error('Passwörter stimmen nicht überein'); return; }
    if (form.password.length < 6) { toast.error('Passwort muss mindestens 6 Zeichen haben'); return; }
    setLoading(true);
    try {
      await api.post('/auth/register', {
        email: form.email, password: form.password,
        first_name: form.first_name, last_name: form.last_name,
        company: form.company, phone: form.phone
      });
      await checkAuth();
      toast.success('Konto erstellt!');
      navigate('/konto');
    } catch (err) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Registrierung fehlgeschlagen');
    }
    setLoading(false);
  };

  const u = (k, v) => setForm(f => ({ ...f, [k]: v }));

  return (
    <div className="sf-auth-page" data-testid="customer-register-page">
      <div className="sf-auth-card" style={{ maxWidth: '480px' }}>
        <div className="sf-auth-header">
          <span className="sf-auth-logo">
            <span className="t">TRUCK</span><span className="on">ON</span><span className="r">ROAD</span>
          </span>
          <div className="sf-auth-subtitle">Konto erstellen</div>
        </div>
        <form onSubmit={handleSubmit} className="sf-auth-form">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div className="sf-auth-field">
              <label>Vorname *</label>
              <input required value={form.first_name} onChange={e => u('first_name', e.target.value)} placeholder="Max" data-testid="reg-first-name" />
            </div>
            <div className="sf-auth-field">
              <label>Nachname *</label>
              <input required value={form.last_name} onChange={e => u('last_name', e.target.value)} placeholder="Muster" data-testid="reg-last-name" />
            </div>
          </div>
          <div className="sf-auth-field">
            <label>E-Mail *</label>
            <input type="email" required value={form.email} onChange={e => u('email', e.target.value)} placeholder="max@firma.ch" data-testid="reg-email" />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div className="sf-auth-field">
              <label>Firma</label>
              <input value={form.company} onChange={e => u('company', e.target.value)} placeholder="optional" data-testid="reg-company" />
            </div>
            <div className="sf-auth-field">
              <label>Telefon</label>
              <input value={form.phone} onChange={e => u('phone', e.target.value)} placeholder="+41 79..." data-testid="reg-phone" />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div className="sf-auth-field">
              <label>Passwort *</label>
              <input type="password" required value={form.password} onChange={e => u('password', e.target.value)} placeholder="Min. 6 Zeichen" data-testid="reg-password" />
            </div>
            <div className="sf-auth-field">
              <label>Wiederholen *</label>
              <input type="password" required value={form.password2} onChange={e => u('password2', e.target.value)} placeholder="Passwort bestätigen" data-testid="reg-password2" />
            </div>
          </div>
          <button type="submit" className="sf-auth-btn" disabled={loading} data-testid="reg-submit-btn">
            <UserPlus size={16} /> {loading ? 'Erstellen...' : 'Konto erstellen'}
          </button>
        </form>
        <div className="sf-auth-footer">
          Bereits ein Konto? <Link to="/konto/login" data-testid="login-link">Anmelden</Link>
        </div>
      </div>
    </div>
  );
}
