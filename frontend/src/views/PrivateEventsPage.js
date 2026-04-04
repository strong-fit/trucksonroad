"use client";
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { Gift, Building2, Heart, PartyPopper, Trophy, CalendarDays } from 'lucide-react';

const BOWL_IMG = "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/9fk5box5_Bildschirmfoto%202026-03-25%20um%2023.23.44.png";

export default function PrivateEventsPage() {
  const { t } = useLanguage();

  const eventTypes = [
    { icon: <Gift size={20} />, name: t('priv_type_1') },
    { icon: <Heart size={20} />, name: t('priv_type_2') },
    { icon: <Building2 size={20} />, name: t('priv_type_3') },
    { icon: <PartyPopper size={20} />, name: t('priv_type_4') },
    { icon: <Trophy size={20} />, name: t('priv_type_5') },
    { icon: <CalendarDays size={20} />, name: t('priv_type_6') },
  ];

  const steps = [
    { num: '1', title: t('priv_step_1_title'), text: t('priv_step_1_text') },
    { num: '2', title: t('priv_step_2_title'), text: t('priv_step_2_text') },
    { num: '3', title: t('priv_step_3_title'), text: t('priv_step_3_text') },
  ];

  return (
    <div data-testid="private-events-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag">{t('priv_tag')}</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>{t('priv_title')}</h1>
        <p className="sf-page-hero-desc">{t('priv_desc')}</p>
        <Link href="/anfrage" className="sf-btn-primary" data-testid="priv-inquiry-btn">{t('nav_cta')}</Link>
      </div>

      <section className="sf-section">
        <div className="sf-section-tag">{t('priv_events_tag')}</div>
        <h2 className="sf-section-title">{t('priv_events_title')}</h2>
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
        <div className="sf-section-tag">{t('priv_steps_tag')}</div>
        <h2 className="sf-section-title">{t('priv_steps_title')}</h2>
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
            <div className="sf-section-tag">{t('priv_know_tag')}</div>
            <h2 className="sf-section-title" style={{ fontSize: '1.8rem' }}>{t('priv_know_title')}</h2>
            <ul className="sf-truck-list" style={{ marginTop: '1.5rem' }}>
              <li>{t('priv_know_1')}</li>
              <li>{t('priv_know_2')}</li>
              <li>{t('priv_know_3')}</li>
              <li>{t('priv_know_4')}</li>
              <li>{t('priv_know_5')}</li>
              <li>{t('priv_know_6')}</li>
            </ul>
          </div>
          <div className="sf-whom-visual">
            <img src={BOWL_IMG} alt="Bowl Truck" className="sf-whom-img-main" />
          </div>
        </div>
      </section>

      <section className="sf-cta">
        <div className="sf-cta-eyebrow">{t('priv_cta_eyebrow')}</div>
        <h2 className="sf-cta-title">{t('priv_cta_title')}</h2>
        <div className="sf-cta-actions">
          <Link href="/anfrage" className="sf-btn-primary">{t('nav_cta')}</Link>
          <Link href="/faq" className="sf-btn-outline">{t('cta_btn_faq')}</Link>
        </div>
      </section>
    </div>
  );
}
