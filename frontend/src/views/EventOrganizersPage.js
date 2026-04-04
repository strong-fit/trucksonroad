"use client";
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { Zap, Users, Shield, Eye, Clock, Truck } from 'lucide-react';

const TRUCK_IMG = "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/apahq84l_Bildschirmfoto%202026-03-23%20um%2017.15.39.png";

export default function EventOrganizersPage() {
  const { t } = useLanguage();

  const features = [
    { icon: <Zap size={20} />, title: t('org_feat_1_title'), text: t('org_feat_1_text') },
    { icon: <Users size={20} />, title: t('org_feat_2_title'), text: t('org_feat_2_text') },
    { icon: <Shield size={20} />, title: t('org_feat_3_title'), text: t('org_feat_3_text') },
    { icon: <Eye size={20} />, title: t('org_feat_4_title'), text: t('org_feat_4_text') },
    { icon: <Truck size={20} />, title: t('org_feat_5_title'), text: t('org_feat_5_text') },
    { icon: <Clock size={20} />, title: t('org_feat_6_title'), text: t('org_feat_6_text') },
  ];

  return (
    <div data-testid="organizers-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag">{t('org_tag')}</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>{t('org_title')}</h1>
        <p className="sf-page-hero-desc">{t('org_desc')}</p>
        <Link href="/anfrage" className="sf-btn-primary" data-testid="org-inquiry-btn">{t('nav_cta')}</Link>
      </div>

      <section className="sf-section">
        <div className="sf-section-tag">{t('org_why_tag')}</div>
        <h2 className="sf-section-title">{t('org_why_title')}</h2>
        <div className="sf-info-grid">
          {features.map((f, i) => (
            <div key={i} className="sf-info-card" data-testid={`org-feature-${i}`}>
              <div className="sf-info-card-num" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ color: 'var(--sf-gold)' }}>{f.icon}</span>
              </div>
              <div className="sf-info-card-title">{f.title}</div>
              <div className="sf-info-card-text">{f.text}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="sf-section" style={{ paddingTop: 0 }}>
        <div className="sf-whom" style={{ gap: '3rem' }}>
          <div>
            <div className="sf-section-tag">{t('org_tech_tag')}</div>
            <h2 className="sf-section-title" style={{ fontSize: '1.8rem' }}>{t('org_tech_title')}</h2>
            <ul className="sf-truck-list" style={{ marginTop: '1.5rem' }}>
              <li>{t('org_tech_1')}</li>
              <li>{t('org_tech_2')}</li>
              <li>{t('org_tech_3')}</li>
              <li>{t('org_tech_4')}</li>
              <li>{t('org_tech_5')}</li>
              <li>{t('org_tech_6')}</li>
            </ul>
          </div>
          <div className="sf-whom-visual">
            <img src={TRUCK_IMG} alt="Truck" className="sf-whom-img-main" />
            <div className="sf-whom-badge">
              <a href={`${process.env.REACT_APP_BACKEND_URL}/api/download/veranstalter-pdf`} target="_blank" rel="noopener noreferrer" style={{ color: 'inherit', textDecoration: 'none' }} data-testid="org-pdf-download">
                {t('org_pdf')}
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="sf-cta">
        <div className="sf-cta-eyebrow">{t('org_cta_eyebrow')}</div>
        <h2 className="sf-cta-title">{t('org_cta_title')}</h2>
        <div className="sf-cta-actions">
          <Link href="/anfrage" className="sf-btn-primary">{t('nav_cta')}</Link>
        </div>
      </section>
    </div>
  );
}
