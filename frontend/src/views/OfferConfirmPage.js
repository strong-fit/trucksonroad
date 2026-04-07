"use client";
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle2, FileText, MapPin, Calendar, Users, CreditCard, Banknote, Loader2 } from 'lucide-react';

export default function OfferConfirmPage() {
  const searchParams = useSearchParams();
  const [phase, setPhase] = useState('loading');
  const [offer, setOffer] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('invoice');
  const [confirming, setConfirming] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const inquiryId = searchParams.get('id');
  const token = searchParams.get('token');

  useEffect(() => {
    if (!inquiryId || !token) {
      setPhase('error');
      setErrorMsg('Ungültiger Link');
      return;
    }
    fetch(`/api/confirm-offer/${inquiryId}/${token}`)
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(data => {
        setOffer(data);
        if (data.already_confirmed) {
          setPhase('already');
        } else {
          setPhase('review');
        }
      })
      .catch(() => { setPhase('error'); setErrorMsg('Ungültiger oder abgelaufener Link.'); });
  }, [inquiryId, token]);

  const handleConfirm = async () => {
    setConfirming(true);
    try {
      const res = await fetch(`/api/confirm-offer/${inquiryId}/${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_method: paymentMethod }),
      });
      const data = await res.json();
      if (data.already_confirmed) {
        setPhase('already');
      } else {
        setPhase('confirmed');
      }
    } catch {
      setErrorMsg('Verbindungsfehler. Bitte versuchen Sie es erneut.');
      setPhase('error');
    } finally {
      setConfirming(false);
    }
  };

  const accentColor = '#4db6ac';

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a08', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }} data-testid="offer-confirm-page">
      <div style={{ maxWidth: 520, width: '100%' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <span style={{ fontFamily: "'Bebas Neue',sans-serif", fontSize: '2rem', letterSpacing: '0.1em' }}>
            <span style={{ color: '#f5f0e8' }}>TRUCKS</span><span style={{ color: accentColor }}>on</span><span style={{ color: '#f5f0e8' }}>ROAD</span>
          </span>
        </div>

        {/* Loading */}
        {phase === 'loading' && (
          <div style={{ background: '#1a1a18', borderRadius: 12, padding: '3rem', textAlign: 'center' }}>
            <Loader2 size={32} color={accentColor} style={{ animation: 'spin 1s linear infinite' }} />
            <p style={{ color: '#9c9c94', marginTop: '1rem' }}>Offerte wird geladen...</p>
            <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
          </div>
        )}

        {/* Review Phase - Show offer details + payment selection */}
        {phase === 'review' && offer && (
          <div style={{ background: '#1a1a18', borderRadius: 12, overflow: 'hidden' }} data-testid="offer-review-section">
            <div style={{ background: 'linear-gradient(135deg, #1a1a18 0%, #252520 100%)', padding: '1.5rem 2rem', borderBottom: '1px solid #333' }}>
              <h2 style={{ color: '#f5f0e8', margin: 0, fontSize: '1.3rem' }}>Ihre Offerte</h2>
              <p style={{ color: '#9c9c94', margin: '0.3rem 0 0', fontSize: '0.85rem' }}>
                Bitte prüfen Sie die Details und bestätigen Sie.
              </p>
            </div>

            <div style={{ padding: '1.5rem 2rem' }}>
              {/* Event Details */}
              <div style={{ display: 'grid', gap: '0.8rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.7rem' }}>
                  <Calendar size={16} color={accentColor} />
                  <div>
                    <div style={{ color: '#9c9c94', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Datum</div>
                    <div style={{ color: '#f5f0e8', fontSize: '0.92rem' }}>{offer.event_date || '–'} {offer.event_time && `· ${offer.event_time}`}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.7rem' }}>
                  <MapPin size={16} color={accentColor} />
                  <div>
                    <div style={{ color: '#9c9c94', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Ort</div>
                    <div style={{ color: '#f5f0e8', fontSize: '0.92rem' }}>{offer.location || '–'}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.7rem' }}>
                  <Users size={16} color={accentColor} />
                  <div>
                    <div style={{ color: '#9c9c94', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Gäste · Eventtyp</div>
                    <div style={{ color: '#f5f0e8', fontSize: '0.92rem' }}>{offer.guest_count || '–'} Gäste · {offer.event_type || '–'}</div>
                  </div>
                </div>
                {offer.selected_trucks?.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.7rem' }}>
                    <FileText size={16} color={accentColor} />
                    <div>
                      <div style={{ color: '#9c9c94', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Trucks</div>
                      <div style={{ color: '#f5f0e8', fontSize: '0.92rem' }}>{offer.selected_trucks.join(', ')}</div>
                    </div>
                  </div>
                )}
              </div>

              {/* Amount */}
              {offer.invoice_amount > 0 && (
                <div style={{ background: '#252520', borderRadius: 8, padding: '1rem 1.25rem', marginBottom: '1.5rem', border: `1px solid ${accentColor}33` }}>
                  <div style={{ color: '#9c9c94', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem' }}>Offerte-Betrag</div>
                  <div style={{ color: accentColor, fontSize: '1.5rem', fontWeight: 700, fontFamily: "'Bebas Neue',sans-serif", letterSpacing: '0.04em' }}>
                    CHF {offer.invoice_amount.toLocaleString('de-CH', { minimumFractionDigits: 2 })}
                  </div>
                </div>
              )}

              {/* Payment Method Selection */}
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ color: '#f5f0e8', fontSize: '0.88rem', fontWeight: 600, marginBottom: '0.75rem' }}>Zahlungsart wählen</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <button
                    onClick={() => setPaymentMethod('invoice')}
                    data-testid="payment-invoice"
                    style={{
                      background: paymentMethod === 'invoice' ? `${accentColor}15` : '#252520',
                      border: `2px solid ${paymentMethod === 'invoice' ? accentColor : '#333'}`,
                      borderRadius: 10, padding: '1rem', cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem',
                    }}
                  >
                    <CreditCard size={22} color={paymentMethod === 'invoice' ? accentColor : '#9c9c94'} />
                    <span style={{ color: paymentMethod === 'invoice' ? '#f5f0e8' : '#9c9c94', fontSize: '0.85rem', fontWeight: 600 }}>Rechnung</span>
                    <span style={{ color: '#6b6b64', fontSize: '0.72rem' }}>Zahlung innert 30 Tagen</span>
                  </button>
                  <button
                    onClick={() => setPaymentMethod('cash')}
                    data-testid="payment-cash"
                    style={{
                      background: paymentMethod === 'cash' ? `${accentColor}15` : '#252520',
                      border: `2px solid ${paymentMethod === 'cash' ? accentColor : '#333'}`,
                      borderRadius: 10, padding: '1rem', cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem',
                    }}
                  >
                    <Banknote size={22} color={paymentMethod === 'cash' ? accentColor : '#9c9c94'} />
                    <span style={{ color: paymentMethod === 'cash' ? '#f5f0e8' : '#9c9c94', fontSize: '0.85rem', fontWeight: 600 }}>Barzahlung</span>
                    <span style={{ color: '#6b6b64', fontSize: '0.72rem' }}>Zahlung vor Ort</span>
                  </button>
                </div>
              </div>

              {/* Confirm Button */}
              <button
                onClick={handleConfirm}
                disabled={confirming}
                data-testid="confirm-offer-btn"
                style={{
                  width: '100%', padding: '0.9rem', background: accentColor, color: '#fff',
                  border: 'none', borderRadius: 8, fontSize: '1rem', fontWeight: 700,
                  cursor: confirming ? 'wait' : 'pointer', opacity: confirming ? 0.7 : 1,
                  transition: 'opacity 0.2s', letterSpacing: '0.02em',
                }}
              >
                {confirming ? 'Wird bestätigt...' : 'Offerte verbindlich bestätigen'}
              </button>
              <p style={{ color: '#6b6b64', fontSize: '0.72rem', textAlign: 'center', marginTop: '0.75rem', lineHeight: 1.5 }}>
                Mit der Bestätigung akzeptieren Sie unser Angebot. Wir melden uns umgehend bei Ihnen.
              </p>
            </div>
          </div>
        )}

        {/* Confirmed */}
        {phase === 'confirmed' && (
          <div style={{ background: '#1a1a18', borderRadius: 12, padding: '2.5rem', textAlign: 'center' }} data-testid="offer-confirmed-section">
            <div style={{ width: 64, height: 64, borderRadius: '50%', background: accentColor, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.25rem' }}>
              <CheckCircle2 size={32} color="#fff" />
            </div>
            <h2 style={{ color: '#f5f0e8', margin: '0 0 0.5rem', fontSize: '1.4rem' }}>Offerte bestätigt!</h2>
            <p style={{ color: '#9c9c94', lineHeight: 1.7, fontSize: '0.9rem', maxWidth: 380, margin: '0 auto' }}>
              Vielen Dank! Wir haben Ihre Bestätigung erhalten und melden uns in Kürze bei Ihnen mit allen weiteren Details.
            </p>
            <div style={{ background: '#252520', borderRadius: 8, padding: '0.8rem 1.2rem', display: 'inline-block', marginTop: '1.25rem', fontSize: '0.82rem', color: '#9c9c94' }}>
              Zahlungsart: <strong style={{ color: '#f5f0e8' }}>{paymentMethod === 'cash' ? 'Barzahlung' : 'Rechnung'}</strong>
            </div>
          </div>
        )}

        {/* Already Confirmed */}
        {phase === 'already' && (
          <div style={{ background: '#1a1a18', borderRadius: 12, padding: '2.5rem', textAlign: 'center' }} data-testid="offer-already-section">
            <CheckCircle2 size={40} color={accentColor} style={{ margin: '0 auto 1rem', display: 'block' }} />
            <h2 style={{ color: '#f5f0e8', margin: '0 0 0.5rem' }}>Bereits bestätigt</h2>
            <p style={{ color: '#9c9c94', fontSize: '0.88rem' }}>
              Diese Offerte wurde bereits bestätigt{offer?.confirmed_at ? ` am ${new Date(offer.confirmed_at).toLocaleDateString('de-CH')}` : ''}.
            </p>
            {offer?.payment_method && (
              <div style={{ background: '#252520', borderRadius: 8, padding: '0.6rem 1rem', display: 'inline-block', marginTop: '1rem', fontSize: '0.82rem', color: '#9c9c94' }}>
                Zahlungsart: <strong style={{ color: '#f5f0e8' }}>{offer.payment_method === 'cash' ? 'Barzahlung' : 'Rechnung'}</strong>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {phase === 'error' && (
          <div style={{ background: '#1a1a18', borderRadius: 12, padding: '2.5rem', textAlign: 'center' }} data-testid="offer-error-section">
            <h2 style={{ color: '#ef4444', margin: '0 0 0.5rem' }}>Fehler</h2>
            <p style={{ color: '#9c9c94' }}>{errorMsg}</p>
          </div>
        )}

        {/* Back link */}
        <div style={{ textAlign: 'center', marginTop: '1.25rem' }}>
          <Link href="/" style={{ color: accentColor, textDecoration: 'none', fontSize: '0.85rem' }} data-testid="back-to-home">
            Zurück zur Startseite
          </Link>
        </div>
      </div>
    </div>
  );
}
