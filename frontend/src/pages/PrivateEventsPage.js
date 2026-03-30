import { Link } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { Gift, Building2, Heart, PartyPopper, Trophy, CalendarDays } from 'lucide-react';

const BOWL_IMG = "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/9fk5box5_Bildschirmfoto%202026-03-25%20um%2023.23.44.png";

export default function PrivateEventsPage() {
  const { lang, t } = useLanguage();
  const isDE = lang === 'de';

  const eventTypes = [
    { icon: <Gift size={20} />, name: isDE ? 'Geburtstag' : 'Birthday' },
    { icon: <Heart size={20} />, name: isDE ? 'Hochzeit' : 'Wedding' },
    { icon: <Building2 size={20} />, name: isDE ? 'Firmenfeier' : 'Corporate Party' },
    { icon: <PartyPopper size={20} />, name: isDE ? 'Er\u00f6ffnung' : 'Opening' },
    { icon: <Trophy size={20} />, name: isDE ? 'Vereinsanlass' : 'Club Event' },
    { icon: <CalendarDays size={20} />, name: isDE ? 'Kundenevent' : 'Client Event' },
  ];

  const steps = [
    { num: '1', title: isDE ? 'Anfrage' : 'Inquiry', text: isDE ? 'F\u00fcllt unser Formular aus mit euren W\u00fcnschen und Details.' : 'Fill out our form with your wishes and details.' },
    { num: '2', title: isDE ? 'Angebot' : 'Offer', text: isDE ? 'Wir pr\u00fcfen und senden euch eine massgeschneiderte Offerte.' : 'We review and send you a tailored offer.' },
    { num: '3', title: isDE ? 'Best\u00e4tigung' : 'Confirmation', text: isDE ? 'Nach Best\u00e4tigung planen wir alles f\u00fcr euren Anlass.' : 'After confirmation, we plan everything for your event.' },
  ];

  return (
    <div data-testid="private-events-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag">{t('priv_tag')}</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>{t('priv_title')}</h1>
        <p className="sf-page-hero-desc">{t('priv_desc')}</p>
        <Link to="/anfrage" className="sf-btn-primary" data-testid="priv-inquiry-btn">{t('nav_cta')}</Link>
      </div>

      <section className="sf-section">
        <div className="sf-section-tag">{isDE ? 'Anl\u00e4sse' : 'Event Types'}</div>
        <h2 className="sf-section-title">{isDE ? 'F\u00fcr diese Anl\u00e4sse\nsind wir bereit.' : 'We\'re ready for\nthese occasions.'}</h2>
        <div className="sf-info-grid">
          {eventTypes.map((ev, i) => (
            <div key={i} className="sf-info-card" data-testid={`event-type-${i}`} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.5rem' }}>
              <span style={{ color: 'var(--sf-gold)' }}>{ev.icon}</span>
              <span style={{ fontWeight: 600 }}>{ev.name}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="sf-section" style={{ paddingTop: 0 }}>
        <div className="sf-section-tag">{isDE ? 'So funktioniert es' : 'How it works'}</div>
        <h2 className="sf-section-title">{isDE ? 'In 3 Schritten\nzu eurem Event.' : 'Your event\nin 3 steps.'}</h2>
        <div className="sf-process">
          {steps.map((step, i) => (
            <div key={i} className="sf-process-step" data-testid={`process-step-${i}`}>
              <div className="sf-process-num">{step.num}</div>
              <div className="sf-process-title">{step.title}</div>
              <div className="sf-process-text">{step.text}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="sf-section" style={{ paddingTop: 0 }}>
        <div className="sf-whom">
          <div>
            <div className="sf-section-tag">{isDE ? 'Gut zu wissen' : 'Good to know'}</div>
            <h2 className="sf-section-title" style={{ fontSize: '1.8rem' }}>{isDE ? 'Was ihr wissen\nm\u00fcsst' : 'What you need\nto know'}</h2>
            <ul className="sf-truck-list" style={{ marginTop: '1.5rem' }}>
              <li>{isDE ? 'Buchung ab ca. 50 G\u00e4sten' : 'Booking from approx. 50 guests'}</li>
              <li>{isDE ? 'Individuell kalkuliert nach Konzept und Ort' : 'Individually calculated by concept and location'}</li>
              <li>{isDE ? 'Mindestens 4\u20138 Wochen im Voraus buchen' : 'Book at least 4-8 weeks in advance'}</li>
              <li>{isDE ? 'Men\u00fc individuell anpassbar' : 'Menu individually customizable'}</li>
              <li>{isDE ? 'Einsatzgebiet: Ganze Schweiz' : 'Service area: All of Switzerland'}</li>
              <li>{isDE ? 'Vegetarische und vegane Optionen verf\u00fcgbar' : 'Vegetarian and vegan options available'}</li>
            </ul>
          </div>
          <div className="sf-whom-visual">
            <img src={BOWL_IMG} alt="Bowl Truck" className="sf-whom-img-main" />
          </div>
        </div>
      </section>

      <section className="sf-cta">
        <div className="sf-cta-eyebrow">{isDE ? 'Bereit f\u00fcr euren Anlass?' : 'Ready for your event?'}</div>
        <h2 className="sf-cta-title">
          {isDE ? 'Jetzt unverbindlich anfragen.' : 'Inquire without obligation.'}
        </h2>
        <div className="sf-cta-actions">
          <Link to="/anfrage" className="sf-btn-primary">{t('nav_cta')}</Link>
          <Link to="/faq" className="sf-btn-outline">{t('cta_btn_faq')}</Link>
        </div>
      </section>
    </div>
  );
}
