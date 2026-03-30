import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { ArrowLeft } from 'lucide-react';

export default function TruckDetailPage() {
  const { slug } = useParams();
  const { lang, t } = useLanguage();
  const [truck, setTruck] = useState(null);

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
      <div className="sf-truck-hero">
        <img src={truck.image} alt={name} />
        <div className="sf-truck-hero-overlay" />
      </div>

      <div className="sf-truck-detail">
        <Link to="/#trucks" style={{ color: 'var(--sf-gray)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem', fontSize: '0.85rem' }}>
          <ArrowLeft size={16} /> {lang === 'de' ? 'Zurück zu allen Trucks' : 'Back to all trucks'}
        </Link>

        {truck.tag && <div className="sf-truck-tag-badge">{truck.tag}</div>}
        <h1 className="sf-truck-name">{name}</h1>
        <div className="sf-truck-tagline">{tagline}</div>
        <p className="sf-truck-desc">{desc}</p>

        <div className="sf-truck-grid">
          <div>
            <h3 className="sf-section-tag" style={{ marginBottom: '1rem' }}>{t('truck_menu')}</h3>
            <ul className="sf-truck-list">
              {menu.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
          <div>
            <h3 className="sf-section-tag" style={{ marginBottom: '1rem' }}>{t('truck_suitable')}</h3>
            <ul className="sf-truck-list">
              {suitable.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        </div>

        <h3 className="sf-section-tag" style={{ marginBottom: '1rem' }}>{t('truck_tech')}</h3>
        <div className="sf-tech-grid">
          <div className="sf-tech-item">
            <div className="sf-tech-label">{t('truck_capacity')}</div>
            <div className="sf-tech-value">{truck.capacity}</div>
          </div>
          <div className="sf-tech-item">
            <div className="sf-tech-label">{t('truck_space')}</div>
            <div className="sf-tech-value">{truck.space_required}</div>
          </div>
          <div className="sf-tech-item">
            <div className="sf-tech-label">{t('truck_power')}</div>
            <div className="sf-tech-value">{truck.power}</div>
          </div>
          <div className="sf-tech-item">
            <div className="sf-tech-label">{t('truck_water')}</div>
            <div className="sf-tech-value">{truck.water}</div>
          </div>
          <div className="sf-tech-item">
            <div className="sf-tech-label">{t('truck_setup')}</div>
            <div className="sf-tech-value">{truck.setup_time}</div>
          </div>
        </div>

        <div style={{ marginTop: '3rem', textAlign: 'center' }}>
          <Link to={`/anfrage?truck=${slug}`} className="sf-btn-primary" data-testid="truck-inquiry-btn" style={{ padding: '1rem 3rem', fontSize: '1rem' }}>
            {t('truck_cta')} &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}
