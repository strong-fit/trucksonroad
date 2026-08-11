"use client";
import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import PoweredByInvictaX from '@/components/PoweredByInvictaX';
import { toast } from 'sonner';
import { Mail, ArrowRight, KeyRound, UserCheck, Loader2, ArrowLeft } from 'lucide-react';

const STEPS = { EMAIL: 'email', CODE: 'code', PROFILE: 'profile' };

export default function CustomerLogin() {
  const { checkAuth } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();
  const [step, setStep] = useState(STEPS.EMAIL);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [profile, setProfile] = useState({
    first_name: '', last_name: '', street: '', plz: '', city: '', mobile: '', company: ''
  });
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const codeRefs = useRef([]);

  useEffect(() => {
    if (countdown <= 0) return;
    const timer = setTimeout(() => setCountdown(c => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown]);

  const sendCode = async (e) => {
    if (e) e.preventDefault();
    if (!email.includes('@')) { toast.error('Bitte gültige E-Mail eingeben'); return; }
    setLoading(true);
    try {
      await api.post('/auth/send-code', { email, lang: 'de' });
      toast.success('Bestätigungscode gesendet!');
      setStep(STEPS.CODE);
      setCountdown(60);
      setCode(['', '', '', '', '', '']);
      setTimeout(() => codeRefs.current[0]?.focus(), 100);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Fehler beim Senden');
    }
    setLoading(false);
  };

  const handleCodeInput = (idx, value) => {
    if (value.length > 1) {
      // Handle paste
      const digits = value.replace(/\D/g, '').slice(0, 6).split('');
      const newCode = [...code];
      digits.forEach((d, i) => { if (idx + i < 6) newCode[idx + i] = d; });
      setCode(newCode);
      const nextIdx = Math.min(idx + digits.length, 5);
      codeRefs.current[nextIdx]?.focus();
      if (newCode.every(c => c !== '')) verifyCode(newCode.join(''));
      return;
    }
    const newCode = [...code];
    newCode[idx] = value.replace(/\D/g, '');
    setCode(newCode);
    if (value && idx < 5) codeRefs.current[idx + 1]?.focus();
    if (newCode.every(c => c !== '')) verifyCode(newCode.join(''));
  };

  const handleCodeKeyDown = (idx, e) => {
    if (e.key === 'Backspace' && !code[idx] && idx > 0) {
      codeRefs.current[idx - 1]?.focus();
    }
  };

  const verifyCode = async (fullCode) => {
    setLoading(true);
    try {
      const r = await api.post('/auth/verify-code', { email, code: fullCode });
      if (r.data.is_new || !r.data.profile_complete) {
        toast.success('E-Mail bestätigt! Bitte Profil vervollständigen.');
        setStep(STEPS.PROFILE);
      } else {
        await checkAuth();
        toast.success('Erfolgreich angemeldet!');
        router.push('/konto');
      }
    } catch (err) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Code ungültig');
      setCode(['', '', '', '', '', '']);
      codeRefs.current[0]?.focus();
    }
    setLoading(false);
  };

  const completeProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/auth/complete-profile', profile);
      await checkAuth();
      toast.success('Profil gespeichert! Willkommen bei TrucksOnRoad.');
      router.push('/konto');
    } catch (err) {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Fehler beim Speichern');
    }
    setLoading(false);
  };

  const up = (k, v) => setProfile(p => ({ ...p, [k]: v }));

  return (
    <div className="sf-auth-page" data-testid="customer-login-page">
      <div className="sf-auth-card" style={{ maxWidth: step === STEPS.PROFILE ? '520px' : '440px' }}>
        <div className="sf-auth-header">
          <span className="sf-auth-logo">
            <span className="t">TRUCKS</span><span className="on">ON</span><span className="r">ROAD</span>
          </span>
          <div className="sf-auth-subtitle">
            {step === STEPS.EMAIL && 'Kundenportal'}
            {step === STEPS.CODE && 'Bestätigungscode'}
            {step === STEPS.PROFILE && 'Profil vervollständigen'}
          </div>
        </div>

        {/* Step indicator */}
        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', marginBottom: '1.5rem' }}>
          {[STEPS.EMAIL, STEPS.CODE, STEPS.PROFILE].map((s, i) => (
            <div key={s} style={{
              width: step === s ? '2rem' : '0.5rem', height: '0.3rem', borderRadius: '2px',
              background: [STEPS.EMAIL, STEPS.CODE, STEPS.PROFILE].indexOf(step) >= i ? 'var(--sf-gold, #4db6ac)' : 'rgba(0,0,0,0.1)',
              transition: 'all 0.3s'
            }} />
          ))}
        </div>

        {/* STEP 1: Email */}
        {step === STEPS.EMAIL && (
          <form onSubmit={sendCode} className="sf-auth-form" data-testid="step-email">
            <p style={{ fontSize: '0.88rem', color: '#6b6b64', textAlign: 'center', lineHeight: 1.6, marginBottom: '1rem' }}>
              Geben Sie Ihre E-Mail-Adresse ein. Sie erhalten einen Bestätigungscode per E-Mail.
            </p>
            <div className="sf-auth-field">
              <label>E-Mail-Adresse</label>
              <input
                type="email" required value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="max@firma.ch" autoFocus
                data-testid="login-email-input"
              />
            </div>
            <button type="submit" className="sf-auth-btn" disabled={loading} data-testid="send-code-btn">
              {loading ? <Loader2 size={16} className="spin" /> : <Mail size={16} />}
              {loading ? 'Sende...' : 'Code senden'}
            </button>
          </form>
        )}

        {/* STEP 2: Verification Code */}
        {step === STEPS.CODE && (
          <div className="sf-auth-form" data-testid="step-code">
            <p style={{ fontSize: '0.88rem', color: '#6b6b64', textAlign: 'center', lineHeight: 1.6, marginBottom: '0.5rem' }}>
              Wir haben einen 6-stelligen Code an
            </p>
            <p style={{ fontSize: '0.92rem', color: '#1a1a18', textAlign: 'center', fontWeight: 600, marginBottom: '1.5rem' }}>
              {email}
            </p>
            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', marginBottom: '1.5rem' }}>
              {code.map((digit, idx) => (
                <input
                  key={idx}
                  ref={el => codeRefs.current[idx] = el}
                  type="text" inputMode="numeric" maxLength={6}
                  value={digit}
                  onChange={e => handleCodeInput(idx, e.target.value)}
                  onKeyDown={e => handleCodeKeyDown(idx, e)}
                  onFocus={e => e.target.select()}
                  data-testid={`code-input-${idx}`}
                  style={{
                    width: '3rem', height: '3.5rem', textAlign: 'center',
                    fontSize: '1.5rem', fontFamily: "'Bebas Neue', monospace",
                    border: '2px solid ' + (digit ? 'var(--sf-gold, #4db6ac)' : '#e0e0e0'),
                    borderRadius: '8px', outline: 'none', background: '#fff',
                    transition: 'border-color 0.2s'
                  }}
                />
              ))}
            </div>
            {loading && (
              <div style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--sf-gold, #4db6ac)' }}>
                <Loader2 size={20} className="spin" style={{ display: 'inline-block' }} /> Wird geprüft...
              </div>
            )}
            <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
              <button
                onClick={sendCode} disabled={countdown > 0 || loading}
                style={{
                  background: 'none', border: 'none', cursor: countdown > 0 ? 'default' : 'pointer',
                  color: countdown > 0 ? '#9c9c94' : 'var(--sf-gold, #4db6ac)',
                  fontSize: '0.85rem', textDecoration: countdown > 0 ? 'none' : 'underline'
                }}
                data-testid="resend-code-btn"
              >
                {countdown > 0 ? `Neuen Code senden (${countdown}s)` : 'Neuen Code senden'}
              </button>
            </div>
            <button
              onClick={() => { setStep(STEPS.EMAIL); setCode(['', '', '', '', '', '']); }}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                color: '#6b6b64', fontSize: '0.85rem', display: 'flex',
                alignItems: 'center', gap: '0.3rem', margin: '1rem auto 0'
              }}
              data-testid="back-to-email-btn"
            >
              <ArrowLeft size={14} /> Andere E-Mail verwenden
            </button>
          </div>
        )}

        {/* STEP 3: Complete Profile */}
        {step === STEPS.PROFILE && (
          <form onSubmit={completeProfile} className="sf-auth-form" data-testid="step-profile">
            <p style={{ fontSize: '0.88rem', color: '#6b6b64', textAlign: 'center', lineHeight: 1.6, marginBottom: '1rem' }}>
              Fast geschafft! Bitte vervollständigen Sie Ihr Profil.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="sf-auth-field">
                <label>Vorname *</label>
                <input required value={profile.first_name} onChange={e => up('first_name', e.target.value)} placeholder="Max" data-testid="profile-first-name" />
              </div>
              <div className="sf-auth-field">
                <label>Name *</label>
                <input required value={profile.last_name} onChange={e => up('last_name', e.target.value)} placeholder="Muster" data-testid="profile-last-name" />
              </div>
            </div>
            <div className="sf-auth-field">
              <label>Strasse *</label>
              <input required value={profile.street} onChange={e => up('street', e.target.value)} placeholder="Bahnhofstrasse 75" data-testid="profile-street" />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '0.75rem' }}>
              <div className="sf-auth-field">
                <label>PLZ *</label>
                <input required value={profile.plz} onChange={e => up('plz', e.target.value)} placeholder="8620" data-testid="profile-plz" />
              </div>
              <div className="sf-auth-field">
                <label>Ort *</label>
                <input required value={profile.city} onChange={e => up('city', e.target.value)} placeholder="Wetzikon" data-testid="profile-city" />
              </div>
            </div>
            <div className="sf-auth-field">
              <label>Mobile *</label>
              <input required type="tel" value={profile.mobile} onChange={e => up('mobile', e.target.value)} placeholder="+41 79 123 45 67" data-testid="profile-mobile" />
            </div>
            <div className="sf-auth-field">
              <label>Firma (optional)</label>
              <input value={profile.company} onChange={e => up('company', e.target.value)} placeholder="Firma AG" data-testid="profile-company" />
            </div>
            <button type="submit" className="sf-auth-btn" disabled={loading} data-testid="complete-profile-btn">
              {loading ? <Loader2 size={16} className="spin" /> : <UserCheck size={16} />}
              {loading ? 'Speichern...' : 'Profil speichern & weiter'}
            </button>
          </form>
        )}

        {step === STEPS.EMAIL && (
          <div className="sf-auth-footer" style={{ marginTop: '1rem' }}>
            <span style={{ fontSize: '0.82rem', color: '#9c9c94' }}>Kein Passwort nötig – sicher per E-Mail-Code</span>
          </div>
        )}
        <PoweredByInvictaX variant="light" />
      </div>
    </div>
  );
}
