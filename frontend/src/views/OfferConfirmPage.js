"use client";
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

export default function OfferConfirmPage() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('invoice');

  const inquiryId = searchParams.get('id');
  const token = searchParams.get('token');

  useEffect(() => {
    if (!inquiryId || !token) {
      setStatus('error');
      setMessage('Ungültiger Link');
      return;
    }
    fetch(`/api/confirm-offer/${inquiryId}/${token}`)
      .then(r => r.json())
      .then(data => {
        if (data.message?.includes('bereits')) {
          setStatus('already');
          setMessage(data.message);
        } else if (data.message) {
          setStatus('confirmed');
          setMessage(data.message);
        } else {
          setStatus('error');
          setMessage('Fehler bei der Bestätigung');
        }
      })
      .catch(() => { setStatus('error'); setMessage('Verbindungsfehler'); });
  }, [inquiryId, token]);

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a08', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
      <div style={{ maxWidth: 500, width: '100%', background: '#1a1a18', borderRadius: 12, padding: '2.5rem', textAlign: 'center' }}>
        <div style={{ fontFamily: "'Bebas Neue',sans-serif", fontSize: '1.8rem', letterSpacing: '0.1em', marginBottom: '1.5rem' }}>
          <span style={{ color: '#f5f0e8' }}>TRUCKS</span><span style={{ color: '#4db6ac' }}>on</span><span style={{ color: '#f5f0e8' }}>ROAD</span>
        </div>

        {status === 'loading' && (
          <p style={{ color: '#f5f0e8' }}>Offerte wird bestätigt...</p>
        )}

        {status === 'confirmed' && (
          <>
            <div style={{ width: 60, height: 60, borderRadius: '50%', background: '#4db6ac', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
              <svg width="28" height="28" fill="none" stroke="#fff" strokeWidth="3" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7"/></svg>
            </div>
            <h2 style={{ color: '#f5f0e8', margin: '0 0 0.5rem' }}>Offerte bestätigt!</h2>
            <p style={{ color: '#9c9c94', lineHeight: 1.6 }}>{message}</p>
          </>
        )}

        {status === 'already' && (
          <>
            <h2 style={{ color: '#f5f0e8', margin: '0 0 0.5rem' }}>Bereits bestätigt</h2>
            <p style={{ color: '#9c9c94' }}>{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <h2 style={{ color: '#ef4444', margin: '0 0 0.5rem' }}>Fehler</h2>
            <p style={{ color: '#9c9c94' }}>{message}</p>
          </>
        )}

        <Link href="/" style={{ display: 'inline-block', marginTop: '1.5rem', color: '#4db6ac', textDecoration: 'none', fontSize: '0.9rem' }}>
          Zurück zur Startseite
        </Link>
      </div>
    </div>
  );
}
