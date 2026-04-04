"use client";
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { ArrowRight, Instagram, Star, Quote, ChevronRight, Calendar, Tag, Send, FileText, PartyPopper, Building2, Heart, Music, Cake, Users, Sparkles, Award } from 'lucide-react';

const HERO_IMG_MAIN = "https://images.unsplash.com/photo-1565123409695-7b5ef63a2efb?w=900&q=80";
const HERO_IMG_ACCENT = "https://images.unsplash.com/photo-1509315811345-672d83ef2fbc?w=600&q=80";

const UC_IMAGES = {
  corporate: "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&q=80",
  wedding: "https://images.unsplash.com/photo-1519225421980-715cb0215aed?w=600&q=80",
  festival: "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=600&q=80",
  birthday: "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=600&q=80",
};

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

const tickerItems = ["Burger Truck", "Bowl Truck", "Empanadas Truck", "Pocket Bowl Truck", "Retro Trailer", "Festivals", "Hochzeiten", "Firmenanlässe", "Privatevents"];

export default function HomePage() {
  const { lang, t } = useLanguage();
  const [trucks, setTrucks] = useState([]);
  const [faqs, setFaqs] = useState([]);
  const [openFaq, setOpenFaq] = useState(null);
  const [instaData, setInstaData] = useState({ username: '', images: [] });
  const [reviews, setReviews] = useState([]);
  const [blogPosts, setBlogPosts] = useState([]);

  useEffect(() => {
    api.get('/trucks').then(r => setTrucks(r.data)).catch(() => {});
    api.get('/faqs').then(r => setFaqs(r.data)).catch(() => {});
    api.get('/instagram-gallery').then(r => setInstaData(r.data)).catch(() => {});
    api.get('/reviews').then(r => setReviews(r.data)).catch(() => {});
    api.get('/blog?limit=3').then(r => setBlogPosts(r.data.posts || [])).catch(() => {});
  }, []);

  const useCases = [
    { key: 'corporate', icon: Building2, img: UC_IMAGES.corporate, typeIndex: 1 },
    { key: 'wedding', icon: Heart, img: UC_IMAGES.wedding, typeIndex: 3 },
    { key: 'festival', icon: Music, img: UC_IMAGES.festival, typeIndex: 0 },
    { key: 'birthday', icon: Cake, img: UC_IMAGES.birthday, typeIndex: 2 },
  ];

  const howSteps = [
    { num: '01', icon: Send, key: '1' },
    { num: '02', icon: FileText, key: '2' },
    { num: '03', icon: PartyPopper, key: '3' },
  ];

  return (
    <div data-testid="home-page">
      {/* ===== HERO – Emotional, experience-focused ===== */}
      <section className="sf-hero" data-testid="hero-section">
        <div className="sf-hero-bg" />
        <div className="sf-hero-grid" />
        <div className="sf-hero-trucks">
          <img src={HERO_IMG_MAIN} alt="Foodtruck Event" className="sf-hero-truck-main" />
          <img src={HERO_IMG_ACCENT} alt="Foodtruck" className="sf-hero-truck-accent" />
        </div>
        <div className="sf-hero-content">
          <FadeUp delay={0.1}>
            <div className="sf-hero-eyebrow">{t('hero_eyebrow')}</div>
          </FadeUp>
          <FadeUp delay={0.2}>
            <h1 className="sf-hero-title">
              {t('hero_title_1')}<br />
              <span className="gold">{t('hero_title_2')}</span><br />
              {t('hero_title_4')}{t('hero_title_5')}
            </h1>
          </FadeUp>
          <FadeUp delay={0.3}>
            <p className="sf-hero-subtitle">{t('hero_subtitle')}</p>
          </FadeUp>
          <FadeUp delay={0.4}>
            <div className="sf-hero-actions">
              <Link href="/anfrage" className="sf-btn-primary" data-testid="hero-inquiry-btn">{t('hero_btn_inquiry')}</Link>
              <a href="#how-it-works" className="sf-btn-outline" data-testid="hero-how-btn">{t('hero_btn_trucks')}</a>
            </div>
          </FadeUp>
        </div>
        <div className="sf-hero-stats">
          <div className="sf-stat"><div className="sf-stat-num">{t('hero_stat_1_num')}</div><div className="sf-stat-label">{t('hero_stat_1_label')}</div></div>
          <div className="sf-stat"><div className="sf-stat-num">{t('hero_stat_2_num')}</div><div className="sf-stat-label">{t('hero_stat_2_label')}</div></div>
          <div className="sf-stat"><div className="sf-stat-num">{t('hero_stat_3_num')}</div><div className="sf-stat-label">{t('hero_stat_3_label')}</div></div>
        </div>
      </section>

      {/* ===== TICKER ===== */}
      <div className="sf-ticker" data-testid="ticker">
        <div className="sf-ticker-inner">
          {[...tickerItems, ...tickerItems].map((item, i) => (
            <span key={i} className="sf-ticker-item">{item}</span>
          ))}
        </div>
      </div>

      {/* ===== USE CASES – "Für jeden Anlass" ===== */}
      <section className="sf-section" data-testid="use-cases-section">
        <FadeUp>
          <div className="sf-section-tag">{t('uc_tag')}</div>
          <h2 className="sf-section-title" style={{ maxWidth: 700 }}>{t('uc_title')}</h2>
        </FadeUp>
        <div className="sf-uc-grid" data-testid="use-cases-grid">
          {useCases.map((uc, i) => {
            const Icon = uc.icon;
            return (
              <FadeUp key={uc.key} delay={i * 0.1}>
                <Link href={`/anfrage?type=${uc.typeIndex}`} className="sf-uc-card" data-testid={`uc-card-${uc.key}`}>
                  <img src={uc.img} alt={t(`uc_${uc.key}_title`)} className="sf-uc-card-img" />
                  <div className="sf-uc-card-overlay" />
                  <div className="sf-uc-card-content">
                    <div className="sf-uc-card-icon"><Icon size={22} /></div>
                    <h3 className="sf-uc-card-title">{t(`uc_${uc.key}_title`)}</h3>
                    <p className="sf-uc-card-desc">{t(`uc_${uc.key}_desc`)}</p>
                    <span className="sf-uc-card-cta">{t('uc_cta')} <ArrowRight size={14} /></span>
                  </div>
                </Link>
              </FadeUp>
            );
          })}
        </div>
      </section>

      {/* ===== HOW IT WORKS – "So funktioniert's" ===== */}
      <section className="sf-how-section" id="how-it-works" data-testid="how-it-works-section">
        <FadeUp>
          <div className="sf-section-tag">{t('how_tag')}</div>
          <h2 className="sf-section-title">{t('how_title')}</h2>
        </FadeUp>
        <div className="sf-how-grid">
          {howSteps.map((step, i) => {
            const Icon = step.icon;
            return (
              <FadeUp key={step.key} delay={i * 0.15}>
                <div className="sf-how-step" data-testid={`how-step-${step.key}`}>
                  <div className="sf-how-num-wrap">
                    <span className="sf-how-num">{step.num}</span>
                    <Icon size={24} className="sf-how-icon" />
                  </div>
                  <h3 className="sf-how-step-title">{t(`how_step${step.key}_title`)}</h3>
                  <p className="sf-how-step-desc">{t(`how_step${step.key}_desc`)}</p>
                  {i < howSteps.length - 1 && <div className="sf-how-connector" />}
                </div>
              </FadeUp>
            );
          })}
        </div>
        <FadeUp delay={0.5}>
          <div style={{ textAlign: 'center', marginTop: '3rem' }}>
            <Link href="/anfrage" className="sf-btn-primary" data-testid="how-cta-btn">{t('hero_btn_inquiry')}</Link>
          </div>
        </FadeUp>
      </section>

      {/* ===== PRICING – "Preis auf Anfrage" ===== */}
      <section className="sf-section" data-testid="pricing-section">
        <FadeUp>
          <div className="sf-section-tag">{t('pricing_tag')}</div>
          <h2 className="sf-section-title">{t('pricing_title')}</h2>
          <p style={{ color: 'var(--sf-gray)', fontSize: '0.92rem', maxWidth: 550, margin: '0 auto 2.5rem', textAlign: 'center', lineHeight: 1.7 }}>
            {t('pricing_subtitle')}
          </p>
        </FadeUp>
        <div className="sf-pricing-grid" data-testid="pricing-grid">
          {[
            { size: 'small', icon: Users },
            { size: 'medium', icon: Sparkles },
            { size: 'large', icon: Award },
          ].map((pkg, i) => {
            const Icon = pkg.icon;
            return (
              <FadeUp key={pkg.size} delay={i * 0.12}>
                <div className={`sf-pricing-card ${pkg.size === 'medium' ? 'sf-pricing-featured' : ''}`} data-testid={`pricing-card-${pkg.size}`}>
                  <div className="sf-pricing-card-icon"><Icon size={22} /></div>
                  <h3 className="sf-pricing-card-title">{t(`pricing_${pkg.size}_title`)}</h3>
                  <div className="sf-pricing-card-guests">{t(`pricing_${pkg.size}_guests`)}</div>
                  <p className="sf-pricing-card-desc">{t(`pricing_${pkg.size}_desc`)}</p>
                  <div className="sf-pricing-card-price">{t('pricing_price')}</div>
                  <div className="sf-pricing-card-includes">{t('pricing_includes')}</div>
                  <Link href="/anfrage" className="sf-btn-primary sf-pricing-card-btn">{t('hero_btn_inquiry')}</Link>
                </div>
              </FadeUp>
            );
          })}
        </div>
        <FadeUp delay={0.4}>
          <div className="sf-pricing-bottom" data-testid="pricing-cta">
            <div className="sf-pricing-cta-text">{t('pricing_cta')}</div>
            <div className="sf-pricing-note">{t('pricing_note')}</div>
          </div>
        </FadeUp>
      </section>

      {/* ===== TRUST NUMBERS ===== */}
      <section className="sf-trust-bar" data-testid="trust-numbers-section">
        <div className="sf-trust-inner">
          <FadeUp><div className="sf-trust-item"><span className="sf-trust-num">{t('trust_events_num')}</span><span className="sf-trust-label">{t('trust_events_label')}</span></div></FadeUp>
          <FadeUp delay={0.1}><div className="sf-trust-item"><span className="sf-trust-num">{t('trust_satisfaction_num')}</span><span className="sf-trust-label">{t('trust_satisfaction_label')}</span></div></FadeUp>
          <FadeUp delay={0.2}><div className="sf-trust-item"><span className="sf-trust-num">{t('trust_response_num')}</span><span className="sf-trust-label">{t('trust_response_label')}</span></div></FadeUp>
          <FadeUp delay={0.3}><div className="sf-trust-item"><span className="sf-trust-num">{t('trust_concepts_num')}</span><span className="sf-trust-label">{t('trust_concepts_label')}</span></div></FadeUp>
        </div>
      </section>

      {/* ===== REVIEWS / TESTIMONIALS (moved up for trust) ===== */}
      {reviews.length > 0 && (
        <section className="sf-section" data-testid="reviews-section">
          <div className="sf-section-inner">
            <FadeUp>
              <div className="sf-section-tag">{t('reviews_tag')}</div>
              <h2 className="sf-section-title" style={{ marginBottom: '0.5rem' }}>
                {t('reviews_title')}
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
                    <span style={{ fontSize: '0.9rem' }}>{avg} / 5 ({reviews.length} {t('reviews_count')})</span>
                  </div>
                );
              })()}
            </FadeUp>
            <div className="sf-reviews-grid" data-testid="reviews-grid">
              {reviews.slice(0, 6).map((r, i) => (
                <FadeUp key={r.id} delay={i * 0.1}>
                  <div className="sf-review-card" data-testid={`review-card-${r.id}`}>
                    <Quote size={24} className="sf-review-quote" />
                    {r.source === 'google' && (
                      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(46,125,50,0.12)', color: '#2e7d32', fontSize: '0.68rem', fontWeight: 600, padding: '2px 8px', borderRadius: '10px', marginBottom: '0.5rem' }} data-testid="review-google-badge">
                        Google Review
                      </div>
                    )}
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

      {/* ===== CUSTOMER LOGOS ===== */}
      <section className="sf-logos-section" data-testid="logos-section">
        <FadeUp>
          <div className="sf-section-tag" style={{ textAlign: 'center' }}>{t('logos_tag')}</div>
          <div className="sf-logos-grid">
            {['Google', 'UBS', 'SBB', 'Migros', 'Swiss', 'Zurich'].map((name, i) => (
              <div key={name} className="sf-logo-item" data-testid={`logo-${name.toLowerCase()}`}>
                <span className="sf-logo-text">{name}</span>
              </div>
            ))}
          </div>
        </FadeUp>
      </section>

      {/* ===== TRUCKS ===== */}
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
          ))}
        </div>
      </section>

      {/* ===== CTA ===== */}
      <section className="sf-cta" data-testid="cta-section">
        <div className="sf-cta-eyebrow">{t('cta_eyebrow')}</div>
        <h2 className="sf-cta-title">
          {t('cta_title_1')} <em>{t('cta_title_em')}</em><br />{t('cta_title_2')}
        </h2>
        <p className="sf-cta-sub">{t('cta_sub')}</p>
        <div className="sf-cta-actions">
          <Link href="/anfrage" className="sf-btn-primary" data-testid="cta-inquiry-btn">{t('cta_btn')}</Link>
          <Link href="/faq" className="sf-btn-outline">{t('cta_btn_faq')}</Link>
        </div>
      </section>

      {/* ===== FAQ PREVIEW ===== */}
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
            <Link href="/faq" className="sf-btn-outline">{t('faq_all')}</Link>
          </div>
        )}
      </section>

      {/* ===== BLOG PREVIEW ===== */}
      {blogPosts.length > 0 && (
        <section className="sf-section" data-testid="blog-preview-section">
          <div className="sf-section-tag">{t('blog_tag')}</div>
          <h2 className="sf-section-title">{t('blog_title')}</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem', maxWidth: '1100px', margin: '0 auto' }}>
            {blogPosts.slice(0, 3).map((post, i) => (
              <FadeUp key={post.id} delay={i * 0.1}>
                <Link href={`/blog/${post.slug}`} style={{ textDecoration: 'none', color: 'inherit' }} data-testid={`blog-preview-${post.slug}`}>
                  <div className="sf-blog-card" style={{
                    borderRadius: '12px', overflow: 'hidden',
                    border: '1px solid rgba(255,255,255,0.08)',
                    background: 'rgba(255,255,255,0.03)'
                  }}>
                    {post.image && (
                      <div style={{ height: '180px', overflow: 'hidden' }}>
                        <img src={post.image} alt={post[`title_${lang}`] || post.title_de} style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.4s' }} loading="lazy" />
                      </div>
                    )}
                    <div style={{ padding: '1.1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--sf-gold)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                          <Tag size={10} style={{ marginRight: '3px', display: 'inline' }} />{post.category}
                        </span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--sf-gray)' }}>
                          <Calendar size={10} style={{ marginRight: '3px', display: 'inline' }} />
                          {new Date(post.created_at).toLocaleDateString('de-CH')}
                        </span>
                      </div>
                      <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--sf-text)', lineHeight: 1.3, marginBottom: '0.4rem' }}>
                        {post[`title_${lang}`] || post.title_de}
                      </h3>
                      <p style={{ fontSize: '0.82rem', color: 'var(--sf-gray)', lineHeight: 1.6 }}>
                        {(post[`excerpt_${lang}`] || post.excerpt_de || '').slice(0, 120)}...
                      </p>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--sf-gold)', fontSize: '0.82rem', fontWeight: 600, marginTop: '0.6rem' }}>
                        {t('blog_read_more')} <ChevronRight size={14} />
                      </div>
                    </div>
                  </div>
                </Link>
              </FadeUp>
            ))}
          </div>
          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <Link href="/blog" className="sf-btn-outline" data-testid="blog-view-all">{t('blog_all')}</Link>
          </div>
        </section>
      )}

      {/* ===== INSTAGRAM ===== */}
      {instaData.images.length > 0 && (
        <section className="sf-section" data-testid="instagram-section">
          <div className="sf-section-inner">
            <div className="sf-tag">{t('instagram_tag')}</div>
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
                  <Instagram size={16} style={{ marginRight: '0.4rem' }} /> {t('instagram_follow')}
                </a>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
