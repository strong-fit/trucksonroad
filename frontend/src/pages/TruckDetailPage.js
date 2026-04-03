import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { ArrowLeft, ArrowRight, Users, Clock, Zap, Quote, ChevronDown, ChevronUp, Utensils, CheckCircle2 } from 'lucide-react';

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

export default function TruckDetailPage() {
  const { slug } = useParams();
  const { lang, t } = useLanguage();
  const [truck, setTruck] = useState(null);
  const [showSpecs, setShowSpecs] = useState(false);

  useEffect(() => {
    api.get(`/trucks/${slug}`).then(r => setTruck(r.data)).catch(() => {});
  }, [slug]);

  if (!truck) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="sf-spinner" />
    </div>
  );

  const name = truck[`name_${lang}`];
  const tagline = truck[`tagline_${lang}`];
  const desc = truck[`description_${lang}`];
  const menu = truck[`menu_${lang}`] || [];
  const suitable = truck[`suitable_for_${lang}`] || [];

  return (
    <div data-testid="truck-detail-page">
      {/* ===== IMMERSIVE HERO ===== */}
      <section className="td-hero" data-testid="truck-hero">
        <img src={truck.image} alt={name} className="td-hero-img" />
        <div className="td-hero-overlay" />
        <div className="td-hero-content">
          <Link to="/#trucks" className="td-back-link" data-testid="truck-back-link">
            <ArrowLeft size={16} /> {t('truck_back')}
          </Link>
          {truck.tag && <div className="td-tag-badge">{truck.tag}</div>}
          <h1 className="td-hero-name" data-testid="truck-name">{name}</h1>
          <p className="td-hero-tagline">{tagline}</p>
        </div>
      </section>

      {/* ===== QUICK STATS BAR ===== */}
      <div className="td-stats-bar" data-testid="truck-stats-bar">
        <div className="td-stat"><Users size={18} /><span>{truck.capacity}</span></div>
        <div className="td-stat"><Clock size={18} /><span>{truck.setup_time}</span></div>
        <div className="td-stat"><Zap size={18} /><span>{truck.power}</span></div>
        <div className="td-stat"><CheckCircle2 size={18} /><span>{suitable.length} {t('truck_suitable')}</span></div>
      </div>

      <div className="td-content">
        {/* ===== STORY / EXPERIENCE ===== */}
        <FadeUp>
          <section className="td-story" data-testid="truck-story">
            <div className="sf-section-tag">{t('truck_experience_tag')}</div>
            <p className="td-story-text">{desc}</p>
          </section>
        </FadeUp>

        {/* ===== PERFECT FOR YOUR EVENT ===== */}
        <FadeUp>
          <section className="td-perfect" data-testid="truck-perfect-for">
            <div className="sf-section-tag">{t('truck_perfect_tag')}</div>
            <p className="td-perfect-subtitle">{t('truck_perfect_desc')}</p>
            <div className="td-perfect-grid">
              {suitable.map((item, i) => (
                <FadeUp key={item} delay={i * 0.08}>
                  <Link to={`/anfrage?truck=${slug}`} className="td-perfect-card" data-testid={`suitable-${i}`}>
                    <span className="td-perfect-card-name">{item}</span>
                    <ArrowRight size={14} className="td-perfect-card-arrow" />
                  </Link>
                </FadeUp>
              ))}
            </div>
          </section>
        </FadeUp>

        {/* ===== MENU ===== */}
        {menu.length > 0 && (
          <FadeUp>
            <section className="td-menu" data-testid="truck-menu">
              <div className="sf-section-tag"><Utensils size={14} style={{ display: 'inline', marginRight: 6 }} />{t('truck_menu_tag')}</div>
              <div className="td-menu-grid">
                {menu.map((item, i) => (
                  <div key={i} className="td-menu-item" data-testid={`menu-item-${i}`}>
                    <div className="td-menu-dot" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </section>
          </FadeUp>
        )}

        {/* ===== CUSTOMER QUOTE ===== */}
        <FadeUp>
          <section className="td-quote" data-testid="truck-quote">
            <Quote size={32} className="td-quote-icon" />
            <blockquote className="td-quote-text">{t('truck_quote_text')}</blockquote>
            <div className="td-quote-author">
              <span className="td-quote-name">{t('truck_quote_author')}</span>
              <span className="td-quote-event">{t('truck_quote_event')}</span>
            </div>
          </section>
        </FadeUp>

        {/* ===== TECHNICAL SPECS (Collapsible) ===== */}
        <FadeUp>
          <section className="td-specs" data-testid="truck-specs">
            <button className="td-specs-toggle" onClick={() => setShowSpecs(!showSpecs)} data-testid="toggle-specs-btn">
              <span className="sf-section-tag" style={{ margin: 0 }}>{t('truck_specs_tag')}</span>
              {showSpecs ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
            {showSpecs && (
              <div className="td-specs-grid" data-testid="specs-grid">
                <div className="td-specs-item"><div className="td-specs-label">{t('truck_capacity')}</div><div className="td-specs-value">{truck.capacity}</div></div>
                <div className="td-specs-item"><div className="td-specs-label">{t('truck_space')}</div><div className="td-specs-value">{truck.space_required}</div></div>
                <div className="td-specs-item"><div className="td-specs-label">{t('truck_power')}</div><div className="td-specs-value">{truck.power}</div></div>
                <div className="td-specs-item"><div className="td-specs-label">{t('truck_water')}</div><div className="td-specs-value">{truck.water}</div></div>
                <div className="td-specs-item"><div className="td-specs-label">{t('truck_setup')}</div><div className="td-specs-value">{truck.setup_time}</div></div>
              </div>
            )}
          </section>
        </FadeUp>

        {/* ===== EMOTIONAL CTA ===== */}
        <FadeUp>
          <section className="td-cta" data-testid="truck-cta-section">
            <h2 className="td-cta-title">{t('truck_cta_emotional')}</h2>
            <p className="td-cta-sub">{t('truck_cta_sub')}</p>
            <Link to={`/anfrage?truck=${slug}`} className="sf-btn-primary td-cta-btn" data-testid="truck-inquiry-btn">
              {t('truck_cta')} <ArrowRight size={16} />
            </Link>
          </section>
        </FadeUp>
      </div>
    </div>
  );
}
