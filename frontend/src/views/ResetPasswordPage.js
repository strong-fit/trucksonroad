"use client";
import { useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import { toast } from 'sonner';
import api from '@/lib/api';
import { Lock, CheckCircle2 } from 'lucide-react';

export default function ResetPasswordPage({ variant = 'customer' }) {
  const { t } = useLanguage();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const loginPath = variant === 'admin' ? '/admin/login' : '/konto/login';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm) { toast.error(t('reset_mismatch')); return; }
    if (password.length < 6) { toast.error(t('change_wrong_old')); return; }
    setLoading(true);
    try {
      await api.post('/auth/reset-password', { token, password });
      setSuccess(true);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('reset_invalid'));
    }
    setLoading(false);
  };

  if (!token) {
    return (
      <div className={variant === 'admin' ? 'adm-login' : 'sf-auth-page'} data-testid="reset-password-page">
        <div className={variant === 'admin' ? 'adm-login-card' : 'sf-auth-card'}>
          <p style={{ textAlign: 'center', color: variant === 'admin' ? '#ef4444' : '#ef4444', padding: '2rem' }}>{t('reset_invalid')}</p>
          <div style={{ textAlign: 'center' }}>
            <Link href={loginPath} style={{ color: 'var(--sf-gold)' }}>{t('forgot_back')}</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={variant === 'admin' ? 'adm-login' : 'sf-auth-page'} data-testid="reset-password-page">
      <div className={variant === 'admin' ? 'adm-login-card' : 'sf-auth-card'}>
        <div className={variant === 'admin' ? 'adm-login-logo' : 'sf-auth-header'}>
          <span className={variant === 'admin' ? '' : 'sf-auth-logo'}>
            <span className="t">TRUCKS</span><span className="on">ON</span><span className="r">ROAD</span>
          </span>
        </div>
        {success ? (
          <div style={{ padding: '1.5rem 0', textAlign: 'center' }}>
            <CheckCircle2 size={40} style={{ color: '#22c55e', margin: '0 auto 1rem' }} />
            <h3 style={{ margin: '0 0 0.75rem', color: variant === 'admin' ? '#1a1a18' : 'var(--sf-cream)' }}>{t('reset_title')}</h3>
            <p style={{ color: variant === 'admin' ? '#6b6b64' : 'var(--sf-gray)', fontSize: '0.9rem', lineHeight: 1.6 }}>{t('reset_success')}</p>
            <Link href={loginPath} className={variant === 'admin' ? 'adm-login-btn' : 'sf-auth-btn'} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', marginTop: '1.5rem', textDecoration: 'none', justifyContent: 'center' }} data-testid="go-login-btn">
              {t('auth_login')}
            </Link>
          </div>
        ) : (
          <>
            <h3 style={{ textAlign: 'center', margin: '1rem 0 1.5rem', color: variant === 'admin' ? '#1a1a18' : 'var(--sf-cream)' }}>{t('reset_title')}</h3>
            <form onSubmit={handleSubmit} className={variant === 'admin' ? 'adm-login-form' : 'sf-auth-form'}>
              <div className={variant === 'admin' ? 'adm-login-group' : 'sf-auth-field'}>
                <label>{t('reset_new_password')}</label>
                <input type="password" required minLength={6} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••" data-testid="reset-password-input" />
              </div>
              <div className={variant === 'admin' ? 'adm-login-group' : 'sf-auth-field'}>
                <label>{t('reset_confirm')}</label>
                <input type="password" required minLength={6} value={confirm} onChange={e => setConfirm(e.target.value)} placeholder="••••••" data-testid="reset-confirm-input" />
              </div>
              <button type="submit" className={variant === 'admin' ? 'adm-login-btn' : 'sf-auth-btn'} disabled={loading} data-testid="reset-submit-btn">
                <Lock size={16} /> {loading ? '...' : t('reset_submit')}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
