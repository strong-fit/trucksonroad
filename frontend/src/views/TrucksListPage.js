"use client";
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { ArrowRight } from 'lucide-react';

function useInView() {
  const ref = useRef();
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold: 0.1 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return [ref, visible];
}

function FadeUp({ children, delay = 0, className = '' }) {
  const [ref, visible] = useInView();
  return (
    <div ref={ref} className={`sf-fade-up ${visible ? 'visible' : ''} ${className}`} style={{ transitionDelay: `${delay}s` }}>
      {children}
    </div>
  );
}

export default function TrucksListPage() {
  const [trucks, setTrucks] = useState([]);
  const { lang, t } = useLanguage();

  useEffect(() => {
    api.get('/trucks').then(r => setTrucks(r.data)).catch(() => {});
  }, []);

  return (
    <div data-testid="trucks-list-page">
      <section className="sf-page-hero" data-testid="trucks-list-hero">
        <div className="sf-page-hero-inner">
          <div className="sf-section-tag">{t('trucks_tag')}</div>
          <h1 className="sf-page-hero-title">
            {t('trucks_title_1')}<br />{t('trucks_title_2')}
          </h1>
          <p className="sf-page-hero-sub">
            {t('trucks_desc')}
          </p>
        </div>
      </section>

      <section className="sf-section" style={{ paddingTop: '3rem' }}>
        <div className="sf-trucks-grid" data-testid="trucks-list-grid">
          {trucks.map((truck, i) => (
            <FadeUp key={truck.slug} delay={i * 0.08}>
              <Link
                href={`/trucks/${truck.slug}`}
                className={`sf-truck-card ${truck.is_wide ? 'sf-truck-card-wide' : ''}`}
                data-testid={`truck-card-${truck.slug}`}
              >
                <img src={truck.image} alt={truck[`name_${lang}`]} />
                {truck.tag && <div className="sf-truck-card-tag">{truck.tag}</div>}
                <div className="sf-truck-card-info">
                  <div className="sf-truck-card-name">{truck[`name_${lang}`]}</div>
                  <div className="sf-truck-card-sub">{truck[`tagline_${lang}`]}</div>
                </div>
              </Link>
            </FadeUp>
          ))}
        </div>
      </section>

      <section className="sf-cta" data-testid="trucks-list-cta">
        <h2 className="sf-cta-title">
          {t('cta_title_1')} <em>{t('cta_title_em')}</em><br />{t('cta_title_2')}
        </h2>
        <p className="sf-cta-sub">{t('cta_sub')}</p>
        <div className="sf-cta-actions">
          <Link href="/anfrage" className="sf-btn-primary" data-testid="trucks-list-inquiry-btn">
            {t('cta_btn')} <ArrowRight size={16} style={{ marginLeft: 6 }} />
          </Link>
        </div>
      </section>
    </div>
  );
}
