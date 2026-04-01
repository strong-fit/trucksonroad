import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { LogIn } from 'lucide-react';

export default function CustomerLogin() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await login(email, password);
      if (data.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/konto');
      }
    } catch (err) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Anmeldung fehlgeschlagen');
    }
    setLoading(false);
  };

  return (
    <div className="sf-auth-page" data-testid="customer-login-page">
      <div className="sf-auth-card">
        <div className="sf-auth-header">
          <span className="sf-auth-logo">
            <span className="t">TRUCK</span><span className="on">ON</span><span className="r">ROAD</span>
          </span>
          <div className="sf-auth-subtitle">Kundenportal</div>
        </div>
        <form onSubmit={handleSubmit} className="sf-auth-form">
          <div className="sf-auth-field">
            <label>E-Mail</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="max@firma.ch" data-testid="customer-email-input" />
          </div>
          <div className="sf-auth-field">
            <label>Passwort</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="Passwort" data-testid="customer-password-input" />
          </div>
          <button type="submit" className="sf-auth-btn" disabled={loading} data-testid="customer-login-btn">
            <LogIn size={16} /> {loading ? 'Anmelden...' : 'Anmelden'}
          </button>
        </form>
        <div className="sf-auth-footer">
          Noch kein Konto? <Link to="/konto/registrieren" data-testid="register-link">Jetzt registrieren</Link>
        </div>
      </div>
    </div>
  );
}
