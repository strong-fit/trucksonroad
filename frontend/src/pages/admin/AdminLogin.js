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
      // Force full reload to ensure auth cookies are read properly
      window.location.href = '/admin';
    } catch (err) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(e => e.msg || '').join(' ') : 'Login fehlgeschlagen';
      toast.error(msg);
      setLoading(false);
    }
  };

  return (
    <div className="sf-login" data-testid="admin-login-page">
      <div className="sf-login-card">
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <span className="sf-logo-text" style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.3rem', fontWeight: 800 }}>STRONG</span>
          <span className="sf-logo-accent" style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.3rem', fontWeight: 800 }}>FOOD</span>
        </div>
        <h2 className="sf-login-title">Admin Login</h2>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="sf-form-group">
            <label>E-Mail</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@strongfood.ch" data-testid="admin-email-input" />
          </div>
          <div className="sf-form-group">
            <label>Passwort</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="Passwort" data-testid="admin-password-input" />
          </div>
          <button type="submit" className="sf-btn-primary" style={{ width: '100%' }} disabled={loading} data-testid="admin-login-btn">
            {loading ? 'Anmelden...' : 'Anmelden'}
          </button>
        </form>
      </div>
    </div>
  );
}
