import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { toast } from 'sonner';

export default function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { t } = useLanguage();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      window.location.href = '/admin';
    } catch (err) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(e => e.msg || '').join(' ') : t('login_failed');
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
            <label>{t('auth_email')}</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@truckonroad.ch" data-testid="admin-email-input" />
          </div>
          <div className="adm-login-group">
            <label>{t('auth_password')}</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} placeholder={t('auth_password')} data-testid="admin-password-input" />
          </div>
          <button type="submit" className="adm-login-btn" disabled={loading} data-testid="admin-login-btn">
            {loading ? t('auth_logging_in') : t('auth_login')}
          </button>
        </form>
      </div>
    </div>
  );
}
