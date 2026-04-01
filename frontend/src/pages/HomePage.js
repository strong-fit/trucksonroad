import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { ArrowRight, Instagram, Star, Quote } from 'lucide-react';

const HERO_IMG_MAIN = "https://images.unsplash.com/photo-1565123409695-7b5ef63a2efb?w=900&q=80";
const HERO_IMG_ACCENT = "https://images.unsplash.com/photo-1509315811345-672d83ef2fbc?w=600&q=80";
const EVENT_IMG = "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=700&q=80";
const ACCENT_IMG = "https://images.unsplash.com/photo-1565123409695-7b5ef63a2efb?w=400&q=80";

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

const tickerItems = ["Burger Truck", "Bowl Truck", "Empanadas Truck", "Pocket Bowl Truck", "Retro Trailer", "Festivals", "Firmenanlässe", "Privatevents"];

export default function HomePage() {
  const { lang, t } = useLanguage();
  const [trucks, setTrucks] = useState([]);
  const [faqs, setFaqs] = useState([]);
  const [openFaq, setOpenFaq] = useState(null);
  const [instaData, setInstaData] = useState({ username: '', images: [] });
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    api.get('/trucks').then(r => setTrucks(r.data)).catch(() => {});
    api.get('/faqs').then(r => setFaqs(r.data)).catch(() => {});
    api.get('/instagram-gallery').then(r => setInstaData(r.data)).catch(() => {});
    api.get('/reviews').then(r => setReviews(r.data)).catch(() => {});
  }, []);

  const whomItems = [t('whom_1'), t('whom_2'), t('whom_3'), t('whom_4'), t('whom_5')];
  const whyItems = [
    { title: t('why_1_title'), text: t('why_1_text') },
    { title: t('why_2_title'), text: t('why_2_text') },
    { title: t('why_3_title'), text: t('why_3_text') },
    { title: t('why_4_title'), text: t('why_4_text') },
  ];

  return (
    <div data-testid="home-page">
      {/* HERO */}
      <section className="sf-hero" data-testid="hero-section">
        <div className="sf-hero-bg" />
        <div className="sf-hero-grid" />
        <div className="sf-hero-trucks">
          <img src={HERO_IMG_MAIN} alt="Foodtruck" className="sf-hero-truck-main" />
          <img src={HERO_IMG_ACCENT} alt="Foodtruck" className="sf-hero-truck-accent" />
        </div>
        <div className="sf-hero-content">
          <FadeUp delay={0.1}>
            <div className="sf-hero-eyebrow">{t('hero_eyebrow')}</div>
          </FadeUp>
          <FadeUp delay={0.2}>
            <h1 className="sf-hero-title">
              <span className="italic">{t('hero_title_1')}</span>{' '}
              {t('hero_title_2')}<span className="gold">{t('hero_title_3')}</span>
              <br />{t('hero_title_4')}<br />{t('hero_title_5')}
            </h1>
          </FadeUp>
          <FadeUp delay={0.3}>
            <p className="sf-hero-subtitle">{t('hero_subtitle')}</p>
          </FadeUp>
          <FadeUp delay={0.4}>
            <div className="sf-hero-actions">
              <Link to="/anfrage" className="sf-btn-primary" data-testid="hero-inquiry-btn">{t('hero_btn_inquiry')}</Link>
              <a href="#trucks" className="sf-btn-outline" data-testid="hero-trucks-btn">{t('hero_btn_trucks')}</a>
            </div>
          </FadeUp>
        </div>
        <div className="sf-hero-stats">
          <div className="sf-stat"><div className="sf-stat-num">{t('hero_stat_1_num')}</div><div className="sf-stat-label">{t('hero_stat_1_label')}</div></div>
          <div className="sf-stat"><div className="sf-stat-num">{t('hero_stat_2_num')}</div><div className="sf-stat-label">{t('hero_stat_2_label')}</div></div>
          <div className="sf-stat"><div className="sf-stat-num">{t('hero_stat_3_num')}</div><div className="sf-stat-label">{t('hero_stat_3_label')}</div></div>
        </div>
      </section>

      {/* TICKER */}
      <div className="sf-ticker" data-testid="ticker">
        <div className="sf-ticker-inner">
          {[...tickerItems, ...tickerItems].map((item, i) => (
            <span key={i} className="sf-ticker-item">{item}</span>
          ))}
        </div>
      </div>

      {/* TRUCKS */}
      <section className="sf-trucks-wrap" id="trucks" data-testid="trucks-section">
        <div className="sf-trucks-header">
          <div>
            <div className="sf-section-tag">{t('trucks_tag')}</div>
            <h2 className="sf-section-title">{t('trucks_title_1')}<br />{t('trucks_title_2')}</h2>
          </div>
          <p style={{ maxWidth: 300, color: 'var(--sf-gray)', fontSize: '0.9rem', lineHeight: 1.7 }}>
            {t('trucks_desc')}
          </p>
        </div>
        <div className="sf-trucks-grid">
          {trucks.map((truck) => (
            <Link
              key={truck.slug}
              to={`/trucks/${truck.slug}`}
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
          ))}
        </div>
      </section>

      {/* FOR WHOM */}
      <section className="sf-section" data-testid="whom-section">
        <div className="sf-whom">
          <div>
            <div className="sf-section-tag">{t('whom_tag')}</div>
            <h2 className="sf-section-title">{t('whom_title_1')}<br />{t('whom_title_2')}<br />{t('whom_title_3')}</h2>
            <ul className="sf-whom-list">
              {whomItems.map((item, i) => (
                <FadeUp key={i} delay={i * 0.1}>
                  <li className="sf-whom-item">
                    <span className="sf-whom-num">{String(i + 1).padStart(2, '0')}</span>
                    <span className="sf-whom-name">{item}</span>
                    <span className="sf-whom-arrow"><ArrowRight size={18} /></span>
                  </li>
                </FadeUp>
              ))}
            </ul>
          </div>
          <div className="sf-whom-visual">
            <img src={EVENT_IMG} alt="Event" className="sf-whom-img-main" />
            <img src={ACCENT_IMG} alt="Truck" className="sf-whom-img-accent" />
            <div className="sf-whom-badge">{t('whom_badge')}</div>
          </div>
        </div>
      </section>

      {/* WHY US */}
      <section className="sf-why-section" data-testid="why-section">
        <div className="sf-section-tag">{t('why_tag')}</div>
        <h2 className="sf-section-title">{t('why_title_1')}<br />{t('why_title_2')}</h2>
        <div className="sf-why-grid">
          {whyItems.map((item, i) => (
            <FadeUp key={i} delay={i * 0.1}>
              <div>
                <div className="sf-why-num">{String(i + 1).padStart(2, '0')}</div>
                <div className="sf-why-title">{item.title}</div>
                <p className="sf-why-text">{item.text}</p>
              </div>
            </FadeUp>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="sf-cta" data-testid="cta-section">
        <div className="sf-cta-eyebrow">{t('cta_eyebrow')}</div>
        <h2 className="sf-cta-title">
          {t('cta_title_1')} <em>{t('cta_title_em')}</em><br />{t('cta_title_2')}
        </h2>
        <p className="sf-cta-sub">{t('cta_sub')}</p>
        <div className="sf-cta-actions">
          <Link to="/anfrage" className="sf-btn-primary" data-testid="cta-inquiry-btn">{t('cta_btn')}</Link>
          <Link to="/faq" className="sf-btn-outline">{t('cta_btn_faq')}</Link>
        </div>
      </section>

      {/* TESTIMONIALS / BEWERTUNGEN */}
      {reviews.length > 0 && (
        <section className="sf-section" data-testid="reviews-section">
          <div className="sf-section-inner">
            <FadeUp>
              <div className="sf-section-tag">{lang === 'de' ? 'Kundenstimmen' : 'Testimonials'}</div>
              <h2 className="sf-section-title" style={{ marginBottom: '0.5rem' }}>
                {lang === 'de' ? 'Was unsere Kunden sagen' : 'What our clients say'}
              </h2>
              {(() => {
                const avg = (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1);
                return (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '2.5rem', color: 'var(--sf-gray)' }}>
                    <div style={{ display: 'flex', gap: '2px' }}>
                      {[1,2,3,4,5].map(s => (
                        <Star key={s} size={18} style={{ fill: s <= Math.round(parseFloat(avg)) ? '#e8b931' : 'transparent', color: s <= Math.round(parseFloat(avg)) ? '#e8b931' : '#555' }} />
                      ))}
                    </div>
                    <span style={{ fontSize: '0.9rem' }}>{avg} / 5 ({reviews.length} {lang === 'de' ? 'Bewertungen' : 'Reviews'})</span>
                  </div>
                );
              })()}
            </FadeUp>
            <div className="sf-reviews-grid" data-testid="reviews-grid">
              {reviews.slice(0, 6).map((r, i) => (
                <FadeUp key={r.id} delay={i * 0.1}>
                  <div className="sf-review-card" data-testid={`review-card-${r.id}`}>
                    <Quote size={24} className="sf-review-quote" />
                    <p className="sf-review-text">{r.text}</p>
                    <div className="sf-review-footer">
                      <div>
                        <div className="sf-review-author">{r.author}</div>
                        {r.event_type && <div className="sf-review-event">{r.event_type}</div>}
                      </div>
                      <div style={{ display: 'flex', gap: '2px' }}>
                        {[1,2,3,4,5].map(s => (
                          <Star key={s} size={13} style={{ fill: s <= r.rating ? '#e8b931' : 'transparent', color: s <= r.rating ? '#e8b931' : '#555' }} />
                        ))}
                      </div>
                    </div>
                  </div>
                </FadeUp>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* --- INSTAGRAM --- */}
      {instaData.images.length > 0 && (
        <section className="sf-section" data-testid="instagram-section">
          <div className="sf-section-inner">
            <div className="sf-tag">{lang === 'de' ? 'Folge uns' : 'Follow us'}</div>
            <h2 className="sf-section-title">
              <Instagram size={28} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '0.5rem', color: 'var(--sf-gold)' }} />
              {instaData.username ? `@${instaData.username}` : 'Instagram'}
            </h2>
            <div className="sf-insta-grid" data-testid="instagram-grid">
              {instaData.images.map((img, i) => (
                <a key={i} href={instaData.username ? `https://instagram.com/${instaData.username}` : '#'} target="_blank" rel="noopener noreferrer" className="sf-insta-item">
                  <img src={img} alt={`Instagram ${i + 1}`} loading="lazy" />
                </a>
              ))}
            </div>
            {instaData.username && (
              <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
                <a href={`https://instagram.com/${instaData.username}`} target="_blank" rel="noopener noreferrer" className="sf-btn-outline" style={{ textDecoration: 'none' }}>
                  <Instagram size={16} style={{ marginRight: '0.4rem' }} /> {lang === 'de' ? 'Auf Instagram folgen' : 'Follow on Instagram'}
                </a>
              </div>
            )}
          </div>
        </section>
      )}

      {/* FAQ PREVIEW */}
      <section className="sf-section" data-testid="faq-preview">
        <div className="sf-section-tag">{t('faq_tag')}</div>
        <h2 className="sf-section-title">{t('faq_title')}</h2>
        <div className="sf-faq-grid">
          {faqs.slice(0, 6).map((faq) => (
            <div key={faq.id} className="sf-faq-item" data-testid={`faq-item-${faq.id}`}>
              <div className="sf-faq-q" onClick={() => setOpenFaq(openFaq === faq.id ? null : faq.id)}>
                {faq[`question_${lang}`]}
                <span className={`sf-faq-icon ${openFaq === faq.id ? 'open' : ''}`}>+</span>
              </div>
              {openFaq === faq.id && (
                <div className="sf-faq-a">{faq[`answer_${lang}`]}</div>
              )}
            </div>
          ))}
        </div>
        {faqs.length > 6 && (
          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <Link to="/faq" className="sf-btn-outline">{t('faq_all')}</Link>
          </div>
        )}
      </section>
    </div>
  );
}
