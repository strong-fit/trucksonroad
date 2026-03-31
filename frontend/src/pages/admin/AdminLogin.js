import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export default function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      window.location.href = '/admin';
    } catch (err) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(e => e.msg || '').join(' ') : 'Login fehlgeschlagen';
      toast.error(msg);
      setLoading(false);
    }
  };

  return (
    <div className="adm-login" data-testid="admin-login-page">
      <div className="adm-login-card">
        <div className="adm-login-logo">
          <span className="t">TRUCK</span>
          <span className="on">ON</span>
          <span className="r">ROAD</span>
        </div>
        <div className="adm-login-subtitle">Administration</div>
        <form onSubmit={handleSubmit} className="adm-login-form">
          <div className="adm-login-group">
            <label>E-Mail</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@truckonroad.ch" data-testid="admin-email-input" />
          </div>
          <div className="adm-login-group">
            <label>Passwort</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="Passwort" data-testid="admin-password-input" />
          </div>
          <button type="submit" className="adm-login-btn" disabled={loading} data-testid="admin-login-btn">
            {loading ? 'Anmelden...' : 'Anmelden'}
          </button>
        </form>
      </div>
    </div>
  );
}
