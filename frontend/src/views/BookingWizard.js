"use client";
import { useState, useEffect, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Calendar } from '@/components/ui/calendar';
import { format, addDays } from 'date-fns';
import { de, fr, it } from 'date-fns/locale';
import {
  Truck, UtensilsCrossed, ShoppingBag, MapPin, CalendarDays,
  User, CheckCircle2, ArrowRight, ArrowLeft, Loader2, Users,
  Clock, Info
} from 'lucide-react';

const STEPS = ['truck', 'catering', 'location', 'calendar', 'customer', 'summary'];
const STEP_LABELS = {
  truck: 'Truck wählen',
  catering: 'Catering',
  location: 'Standort',
  calendar: 'Datum & Zeit',
  customer: 'Kundendaten',
  summary: 'Zusammenfassung'
};
const STEP_ICONS = {
  truck: Truck, catering: UtensilsCrossed, location: MapPin,
  calendar: CalendarDays, customer: User, summary: CheckCircle2
};

export default function BookingWizard() {
  const { lang, t } = useLanguage();
  const { user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedTruck = searchParams.get('truck') || '';

  const [step, setStep] = useState(0);
  const [trucks, setTrucks] = useState([]);
  const [menuCategories, setMenuCategories] = useState([]);
  const [calendarBlocks, setCalendarBlocks] = useState([]);
  const [deliveryCost, setDeliveryCost] = useState(null);
  const [deliveryLoading, setDeliveryLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const [booking, setBooking] = useState({
    truck_slug: preselectedTruck || '',
    catering_type: '', // 'eigenes' or 'unser'
    menu_category: '',
    guest_count: '',
    street: '',
    plz: '',
    city: '',
    date_from: null,
    date_to: null,
    time_from: '',
    time_to: '',
    // Customer data (pre-filled if logged in)
    first_name: '', last_name: '', email: '', mobile: '', company: '',
    remarks: '',
    privacy_accepted: false
  });

  // Load trucks and menu categories
  useEffect(() => {
    api.get('/trucks').then(r => setTrucks(r.data)).catch(() => {});
    api.get('/menu-categories').then(r => setMenuCategories(r.data)).catch(() => {});
  }, []);

  // Pre-fill customer data from auth
  useEffect(() => {
    if (user) {
      api.get('/customer/profile').then(r => {
        const p = r.data;
        setBooking(b => ({
          ...b,
          first_name: p.first_name || '', last_name: p.last_name || '',
          email: p.email || '', mobile: p.mobile || p.phone || '',
          company: p.company || ''
        }));
      }).catch(() => {});
    }
  }, [user]);

  // Load availability when truck is selected
  useEffect(() => {
    if (!booking.truck_slug) return;
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    // Load current and next 2 months
    const promises = [0, 1, 2].map(offset => {
      const m = ((month - 1 + offset) % 12) + 1;
      const y = year + Math.floor((month - 1 + offset) / 12);
      return api.get(`/truck-availability/${booking.truck_slug}?year=${y}&month=${m}`);
    });
    Promise.all(promises).then(results => {
      setCalendarBlocks(results.flatMap(r => r.data));
    }).catch(() => {});
  }, [booking.truck_slug]);

  // Calculate delivery cost when PLZ changes
  useEffect(() => {
    if (!booking.plz || booking.plz.length < 4) { setDeliveryCost(null); return; }
    const timeout = setTimeout(async () => {
      setDeliveryLoading(true);
      try {
        const r = await api.post('/calculate-delivery', { plz: booking.plz });
        setDeliveryCost(r.data);
      } catch { setDeliveryCost(null); }
      setDeliveryLoading(false);
    }, 600);
    return () => clearTimeout(timeout);
  }, [booking.plz]);

  const up = (k, v) => setBooking(b => ({ ...b, [k]: v }));
  const selectedTruck = trucks.find(t => t.slug === booking.truck_slug);

  const blockedDates = useMemo(() =>
    calendarBlocks
      .filter(b => b.status === 'blocked' || b.status === 'confirmed')
      .map(b => { const p = b.date.split('-'); return new Date(+p[0], +p[1]-1, +p[2]); }),
    [calendarBlocks]
  );

  const canProceed = () => {
    switch (STEPS[step]) {
      case 'truck': return !!booking.truck_slug;
      case 'catering': return !!booking.catering_type && (booking.catering_type === 'eigenes' || (booking.menu_category && booking.guest_count));
      case 'location': return !!(booking.street && booking.plz && booking.city);
      case 'calendar': return !!(booking.date_from && booking.time_from && booking.time_to);
      case 'customer': return !!(booking.first_name && booking.last_name && booking.email && booking.mobile && booking.privacy_accepted);
      case 'summary': return true;
      default: return false;
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const payload = {
        ...booking,
        date_from: booking.date_from ? format(booking.date_from, 'yyyy-MM-dd') : '',
        date_to: booking.date_to ? format(booking.date_to, 'yyyy-MM-dd') : '',
        guest_count: parseInt(booking.guest_count) || 0,
        delivery_km: deliveryCost?.km || 0,
        delivery_cost: deliveryCost?.cost || 0,
        lang
      };
      await api.post('/inquiries', {
        first_name: payload.first_name,
        last_name: payload.last_name,
        company: payload.company,
        email: payload.email,
        phone: payload.mobile,
        event_date: payload.date_from,
        event_time: `${payload.time_from} – ${payload.time_to}`,
        location: `${payload.street}, ${payload.plz} ${payload.city}`,
        guest_count: payload.guest_count,
        event_type: payload.catering_type === 'unser' ? 'Catering-Buchung' : 'Truck-Miete',
        selected_trucks: [selectedTruck?.name_de || booking.truck_slug],
        extras: [],
        budget: '',
        remarks: `Catering: ${payload.catering_type === 'unser' ? 'Unser Catering' : 'Eigenes Catering'}${payload.menu_category ? ` | Menü: ${payload.menu_category}` : ''}${payload.date_to ? ` | Bis: ${payload.date_to}` : ''} | Lieferung: ${payload.delivery_km}km (CHF ${payload.delivery_cost})${payload.remarks ? ` | Bemerkung: ${payload.remarks}` : ''}`,
        is_organizer: false,
        privacy_accepted: true,
        lang: payload.lang
      });
      toast.success('Buchungsanfrage erfolgreich gesendet!');
      setSubmitted(true);
    } catch (err) {
      toast.error('Fehler beim Senden. Bitte versuchen Sie es erneut.');
    }
    setSubmitting(false);
  };

  if (submitted) {
    return (
      <div className="sf-booking-success" data-testid="booking-success">
        <div className="sf-booking-success-card">
          <CheckCircle2 size={48} color="var(--sf-gold)" />
          <h2 className="sf-section-title" style={{ fontSize: '1.8rem', marginTop: '1rem' }}>Anfrage gesendet!</h2>
          <p style={{ color: 'var(--sf-gray)', maxWidth: 400, textAlign: 'center', lineHeight: 1.6 }}>
            Vielen Dank! Wir haben Ihre Buchungsanfrage erhalten und melden uns innerhalb von 24 Stunden bei Ihnen.
            Sie erhalten eine Bestaetigungs-E-Mail an <strong>{booking.email}</strong>.
          </p>
          <button className="sf-btn-primary" onClick={() => router.push('/')} style={{ marginTop: '1.5rem' }}>
            Zurueck zur Startseite
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="sf-booking-wizard" data-testid="booking-wizard">
      {/* Step Header */}
      <div className="sf-booking-header">
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(1.6rem, 3vw, 2.2rem)', marginBottom: '0.5rem' }}>
          Truck buchen
        </h1>
        <div className="sf-booking-steps" data-testid="booking-steps">
          {STEPS.map((s, i) => {
            const Icon = STEP_ICONS[s];
            return (
              <div key={s} className={`sf-booking-step-dot ${i === step ? 'active' : ''} ${i < step ? 'done' : ''}`}>
                <Icon size={14} />
                <span className="sf-booking-step-label">{STEP_LABELS[s]}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Step Content */}
      <div className="sf-booking-content">

        {/* STEP 1: Select Truck */}
        {STEPS[step] === 'truck' && (
          <div className="sf-booking-step-content" data-testid="step-truck">
            <h2 className="sf-booking-step-title">Welchen Truck moechten Sie?</h2>
            <div className="sf-booking-truck-grid">
              {trucks.map(truck => (
                <button
                  key={truck.slug}
                  type="button"
                  className={`sf-booking-truck-card ${booking.truck_slug === truck.slug ? 'selected' : ''}`}
                  onClick={() => up('truck_slug', truck.slug)}
                  data-testid={`truck-select-${truck.slug}`}
                >
                  {truck.images && truck.images[0] && (
                    <img src={truck.images[0]} alt={truck.name_de} className="sf-booking-truck-img" />
                  )}
                  <div className="sf-booking-truck-info">
                    <span className="sf-booking-truck-name">{truck.name_de}</span>
                    <span className="sf-booking-truck-tagline">{truck.tagline_de}</span>
                  </div>
                  {booking.truck_slug === truck.slug && (
                    <div className="sf-booking-truck-check"><CheckCircle2 size={20} /></div>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* STEP 2: Catering Type */}
        {STEPS[step] === 'catering' && (
          <div className="sf-booking-step-content" data-testid="step-catering">
            <h2 className="sf-booking-step-title">Catering-Option</h2>
            <div className="sf-booking-catering-options">
              <button
                type="button"
                className={`sf-booking-option-card ${booking.catering_type === 'eigenes' ? 'selected' : ''}`}
                onClick={() => up('catering_type', 'eigenes')}
                data-testid="catering-eigenes"
              >
                <ShoppingBag size={32} />
                <h3>Eigenes Catering</h3>
                <p>Sie organisieren das Essen selbst. Wir bringen nur den Truck an Ihren Standort.</p>
              </button>
              <button
                type="button"
                className={`sf-booking-option-card ${booking.catering_type === 'unser' ? 'selected' : ''}`}
                onClick={() => up('catering_type', 'unser')}
                data-testid="catering-unser"
              >
                <UtensilsCrossed size={32} />
                <h3>Unser Catering</h3>
                <p>Wir uebernehmen alles — Truck, Essen und Service fuer Ihre Gaeste.</p>
              </button>
            </div>

            {booking.catering_type === 'unser' && (
              <div className="sf-booking-catering-details" data-testid="catering-details">
                <div className="sf-booking-field">
                  <label>Menü-Kategorie *</label>
                  <select
                    value={booking.menu_category}
                    onChange={e => up('menu_category', e.target.value)}
                    data-testid="select-menu-category"
                  >
                    <option value="">Bitte wählen...</option>
                    {menuCategories.map(cat => (
                      <option key={cat.id} value={cat.name_de}>{cat.name_de}</option>
                    ))}
                  </select>
                </div>
                <div className="sf-booking-field">
                  <label><Users size={14} /> Anzahl Gäste *</label>
                  <input
                    type="number" min="1"
                    value={booking.guest_count}
                    onChange={e => up('guest_count', e.target.value)}
                    placeholder="z.B. 80"
                    data-testid="input-guest-count"
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 3: Location */}
        {STEPS[step] === 'location' && (
          <div className="sf-booking-step-content" data-testid="step-location">
            <h2 className="sf-booking-step-title">Wohin sollen wir liefern?</h2>
            <div className="sf-booking-location-form">
              <div className="sf-booking-field">
                <label>Strasse *</label>
                <input value={booking.street} onChange={e => up('street', e.target.value)} placeholder="Bahnhofstrasse 75" data-testid="input-street" />
              </div>
              <div className="sf-booking-row">
                <div className="sf-booking-field" style={{ flex: '0 0 120px' }}>
                  <label>PLZ *</label>
                  <input value={booking.plz} onChange={e => up('plz', e.target.value)} placeholder="8000" data-testid="input-plz" />
                </div>
                <div className="sf-booking-field" style={{ flex: 1 }}>
                  <label>Ort *</label>
                  <input value={booking.city} onChange={e => up('city', e.target.value)} placeholder="Zürich" data-testid="input-city" />
                </div>
              </div>

              {/* Delivery cost display */}
              {deliveryLoading && (
                <div className="sf-booking-delivery-info">
                  <Loader2 size={16} className="spin" /> Lieferkosten werden berechnet...
                </div>
              )}
              {deliveryCost && !deliveryCost.error && !deliveryLoading && (
                <div className="sf-booking-delivery-result" data-testid="delivery-cost">
                  <MapPin size={16} />
                  <span>Entfernung: <strong>{deliveryCost.km} km</strong></span>
                  <span className="sf-booking-delivery-price">
                    Lieferkosten: <strong>CHF {deliveryCost.cost.toFixed(2)}</strong>
                  </span>
                  <span className="sf-booking-delivery-note">
                    (CHF {deliveryCost.price_per_km}/km)
                  </span>
                </div>
              )}
              {deliveryCost && deliveryCost.error && !deliveryLoading && (
                <div className="sf-booking-delivery-error">
                  <Info size={14} /> {deliveryCost.error}
                </div>
              )}
            </div>
          </div>
        )}

        {/* STEP 4: Calendar & Time */}
        {STEPS[step] === 'calendar' && (
          <div className="sf-booking-step-content" data-testid="step-calendar">
            <h2 className="sf-booking-step-title">Wann brauchen Sie den Truck?</h2>
            <div className="sf-booking-calendar-layout">
              <div className="sf-booking-calendar-wrapper">
                <Calendar
                  mode="range"
                  selected={{ from: booking.date_from, to: booking.date_to }}
                  onSelect={(range) => {
                    up('date_from', range?.from || null);
                    up('date_to', range?.to || null);
                  }}
                  locale={lang === 'de' ? de : lang === 'fr' ? fr : lang === 'it' ? it : undefined}
                  modifiers={{ booked: blockedDates }}
                  modifiersStyles={{ booked: { backgroundColor: 'rgba(239,68,68,0.2)', color: '#f87171', borderRadius: '4px', textDecoration: 'line-through' } }}
                  disabled={[{ before: new Date() }, ...blockedDates.map(d => d)]}
                  numberOfMonths={2}
                  data-testid="booking-calendar"
                />
                <div className="sf-booking-legend">
                  <span><span className="sf-avail-dot available" /> Verfuegbar</span>
                  <span><span className="sf-avail-dot booked" /> Besetzt</span>
                </div>
              </div>
              <div className="sf-booking-time-fields">
                <div className="sf-booking-field">
                  <label><Clock size={14} /> Von (Uhrzeit) *</label>
                  <input type="time" value={booking.time_from} onChange={e => up('time_from', e.target.value)} data-testid="input-time-from" />
                </div>
                <div className="sf-booking-field">
                  <label><Clock size={14} /> Bis (Uhrzeit) *</label>
                  <input type="time" value={booking.time_to} onChange={e => up('time_to', e.target.value)} data-testid="input-time-to" />
                </div>
                {booking.date_from && (
                  <div className="sf-booking-date-summary">
                    <strong>{format(booking.date_from, 'dd.MM.yyyy')}</strong>
                    {booking.date_to && <span> – {format(booking.date_to, 'dd.MM.yyyy')}</span>}
                    {booking.time_from && booking.time_to && (
                      <div style={{ marginTop: '0.3rem', fontSize: '0.85rem', color: 'var(--sf-gray)' }}>
                        {booking.time_from} – {booking.time_to}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* STEP 5: Customer Data */}
        {STEPS[step] === 'customer' && (
          <div className="sf-booking-step-content" data-testid="step-customer">
            <h2 className="sf-booking-step-title">Ihre Kontaktdaten</h2>
            {user && <p style={{ color: 'var(--sf-gold)', fontSize: '0.85rem', marginBottom: '1rem' }}>Daten aus Ihrem Profil vorausgefuellt.</p>}
            <div className="sf-booking-customer-form">
              <div className="sf-booking-row">
                <div className="sf-booking-field"><label>Vorname *</label><input value={booking.first_name} onChange={e => up('first_name', e.target.value)} data-testid="cust-first-name" /></div>
                <div className="sf-booking-field"><label>Name *</label><input value={booking.last_name} onChange={e => up('last_name', e.target.value)} data-testid="cust-last-name" /></div>
              </div>
              <div className="sf-booking-row">
                <div className="sf-booking-field"><label>E-Mail *</label><input type="email" value={booking.email} onChange={e => up('email', e.target.value)} data-testid="cust-email" /></div>
                <div className="sf-booking-field"><label>Mobile *</label><input type="tel" value={booking.mobile} onChange={e => up('mobile', e.target.value)} placeholder="+41 79..." data-testid="cust-mobile" /></div>
              </div>
              <div className="sf-booking-field"><label>Firma (optional)</label><input value={booking.company} onChange={e => up('company', e.target.value)} data-testid="cust-company" /></div>
              <div className="sf-booking-field"><label>Bemerkungen</label><textarea value={booking.remarks} onChange={e => up('remarks', e.target.value)} placeholder="Weitere Wuensche oder Infos..." data-testid="cust-remarks" /></div>
              <label className="sf-booking-checkbox">
                <input type="checkbox" checked={booking.privacy_accepted} onChange={e => up('privacy_accepted', e.target.checked)} data-testid="cust-privacy" />
                Ich akzeptiere die Datenschutzbestimmungen *
              </label>
            </div>
          </div>
        )}

        {/* STEP 6: Summary */}
        {STEPS[step] === 'summary' && (
          <div className="sf-booking-step-content" data-testid="step-summary">
            <h2 className="sf-booking-step-title">Zusammenfassung</h2>
            <div className="sf-booking-summary">
              <div className="sf-booking-summary-row">
                <span className="sf-booking-summary-label">Truck:</span>
                <span>{selectedTruck?.name_de || booking.truck_slug}</span>
              </div>
              <div className="sf-booking-summary-row">
                <span className="sf-booking-summary-label">Catering:</span>
                <span>{booking.catering_type === 'unser' ? `Unser Catering (${booking.menu_category})` : 'Eigenes Catering'}</span>
              </div>
              {booking.catering_type === 'unser' && (
                <div className="sf-booking-summary-row">
                  <span className="sf-booking-summary-label">Gäste:</span>
                  <span>{booking.guest_count}</span>
                </div>
              )}
              <div className="sf-booking-summary-row">
                <span className="sf-booking-summary-label">Standort:</span>
                <span>{booking.street}, {booking.plz} {booking.city}</span>
              </div>
              {deliveryCost && !deliveryCost.error && (
                <div className="sf-booking-summary-row">
                  <span className="sf-booking-summary-label">Lieferkosten:</span>
                  <span>{deliveryCost.km} km — CHF {deliveryCost.cost.toFixed(2)}</span>
                </div>
              )}
              <div className="sf-booking-summary-row">
                <span className="sf-booking-summary-label">Datum:</span>
                <span>
                  {booking.date_from ? format(booking.date_from, 'dd.MM.yyyy') : ''}
                  {booking.date_to ? ` – ${format(booking.date_to, 'dd.MM.yyyy')}` : ''}
                </span>
              </div>
              <div className="sf-booking-summary-row">
                <span className="sf-booking-summary-label">Uhrzeit:</span>
                <span>{booking.time_from} – {booking.time_to}</span>
              </div>
              <div className="sf-booking-summary-row">
                <span className="sf-booking-summary-label">Kontakt:</span>
                <span>{booking.first_name} {booking.last_name} ({booking.email})</span>
              </div>
              {booking.remarks && (
                <div className="sf-booking-summary-row">
                  <span className="sf-booking-summary-label">Bemerkungen:</span>
                  <span>{booking.remarks}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="sf-booking-nav">
        {step > 0 && (
          <button type="button" className="sf-btn-outline" onClick={() => setStep(s => s - 1)} data-testid="booking-back-btn">
            <ArrowLeft size={16} /> Zurueck
          </button>
        )}
        <div style={{ flex: 1 }} />
        {step < STEPS.length - 1 ? (
          <button
            type="button" className="sf-btn-primary"
            disabled={!canProceed()}
            onClick={() => setStep(s => s + 1)}
            data-testid="booking-next-btn"
          >
            Weiter <ArrowRight size={16} />
          </button>
        ) : (
          <button
            type="button" className="sf-btn-primary"
            disabled={submitting}
            onClick={handleSubmit}
            data-testid="booking-submit-btn"
          >
            {submitting ? <><Loader2 size={16} className="spin" /> Senden...</> : <>Buchung absenden <ArrowRight size={16} /></>}
          </button>
        )}
      </div>
    </div>
  );
}
