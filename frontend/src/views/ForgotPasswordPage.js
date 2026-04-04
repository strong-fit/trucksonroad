"use client";
import { useState } from 'react';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { toast } from 'sonner';
import api from '@/lib/api';
import { Mail, ArrowLeft } from 'lucide-react';

export default function ForgotPasswordPage({ variant = 'customer' }) {
  const { t } = useLanguage();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const loginPath = variant === 'admin' ? '/admin/login' : '/konto/login';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/auth/forgot-password', { email });
      setSent(true);
    } catch {
      toast.error(t('form_send_error'));
    }
    setLoading(false);
  };

  return (
    <div className={variant === 'admin' ? 'adm-login' : 'sf-auth-page'} data-testid="forgot-password-page">
      <div className={variant === 'admin' ? 'adm-login-card' : 'sf-auth-card'}>
        <div className={variant === 'admin' ? 'adm-login-logo' : 'sf-auth-header'}>
          <span className={variant === 'admin' ? '' : 'sf-auth-logo'}>
            <span className="t">TRUCKS</span><span className="on">ON</span><span className="r">ROAD</span>
          </span>
        </div>
        {sent ? (
          <div style={{ padding: '1.5rem 0', textAlign: 'center' }}>
            <Mail size={40} style={{ color: 'var(--sf-gold)', margin: '0 auto 1rem' }} />
            <h3 style={{ margin: '0 0 0.75rem', color: variant === 'admin' ? '#1a1a18' : 'var(--sf-cream)' }}>{t('forgot_title')}</h3>
            <p style={{ color: variant === 'admin' ? '#6b6b64' : 'var(--sf-gray)', fontSize: '0.9rem', lineHeight: 1.6 }}>{t('forgot_sent')}</p>
            <Link href={loginPath} className={variant === 'admin' ? 'adm-login-btn' : 'sf-auth-btn'} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', marginTop: '1.5rem', textDecoration: 'none' }} data-testid="back-to-login-btn">
              <ArrowLeft size={16} /> {t('forgot_back')}
            </Link>
          </div>
        ) : (
          <>
            <h3 style={{ textAlign: 'center', margin: '1rem 0 0.5rem', color: variant === 'admin' ? '#1a1a18' : 'var(--sf-cream)' }}>{t('forgot_title')}</h3>
            <p style={{ textAlign: 'center', color: variant === 'admin' ? '#6b6b64' : 'var(--sf-gray)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>{t('forgot_desc')}</p>
            <form onSubmit={handleSubmit} className={variant === 'admin' ? 'adm-login-form' : 'sf-auth-form'}>
              <div className={variant === 'admin' ? 'adm-login-group' : 'sf-auth-field'}>
                <label>{t('auth_email')}</label>
                <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="max@firma.ch" data-testid="forgot-email-input" />
              </div>
              <button type="submit" className={variant === 'admin' ? 'adm-login-btn' : 'sf-auth-btn'} disabled={loading} data-testid="forgot-submit-btn">
                <Mail size={16} /> {loading ? '...' : t('forgot_send')}
              </button>
            </form>
            <div className={variant === 'admin' ? '' : 'sf-auth-footer'} style={{ textAlign: 'center', marginTop: '1rem' }}>
              <Link href={loginPath} style={{ color: 'var(--sf-gold)', fontSize: '0.85rem' }} data-testid="back-to-login-link">{t('forgot_back')}</Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
