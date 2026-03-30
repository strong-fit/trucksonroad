import { Link } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { Zap, Users, Shield, Eye, Clock, Truck } from 'lucide-react';

const TRUCK_IMG = "https://customer-assets.emergentagent.com/job_c07f57bf-6530-44da-b908-62d9516a565b/artifacts/apahq84l_Bildschirmfoto%202026-03-23%20um%2017.15.39.png";

export default function EventOrganizersPage() {
  const { lang, t } = useLanguage();
  const isDE = lang === 'de';

  const features = [
    { icon: <Zap size={20} />, title: isDE ? 'Schnelle Ausgabe' : 'Fast Service', text: isDE ? 'Bis zu 300 G\u00e4ste pro Stunde \u2013 keine Staus, keine langen Wartezeiten.' : 'Up to 300 guests per hour \u2013 no queues, no long waiting times.' },
    { icon: <Users size={20} />, title: isDE ? 'Erfahrenes Team' : 'Experienced Team', text: isDE ? 'Professionelles, eingespieltes Personal f\u00fcr reibungslose Abl\u00e4ufe.' : 'Professional, well-coordinated staff for smooth operations.' },
    { icon: <Shield size={20} />, title: isDE ? 'Saubere Abl\u00e4ufe' : 'Clean Processes', text: isDE ? 'Klare Strukturen von Aufbau bis Abbau \u2013 ihr k\u00f6nnt euch auf uns verlassen.' : 'Clear structures from setup to teardown \u2013 you can rely on us.' },
    { icon: <Eye size={20} />, title: isDE ? 'Auff\u00e4llige Optik' : 'Eye-catching Look', text: isDE ? 'Unsere Trucks sind ein Hingucker und machen jedes Event besonders.' : 'Our trucks are eye-catchers and make every event special.' },
    { icon: <Truck size={20} />, title: isDE ? 'Mehrere Konzepte' : 'Multiple Concepts', text: isDE ? '6 spezialisierte Trucks \u2013 kombinierbar f\u00fcr maximale Vielfalt.' : '6 specialized trucks \u2013 combinable for maximum variety.' },
    { icon: <Clock size={20} />, title: isDE ? 'Zuverl\u00e4ssig' : 'Reliable', text: isDE ? 'P\u00fcnktlicher Aufbau, professionelle Durchf\u00fchrung, sauberer Abbau.' : 'Punctual setup, professional execution, clean teardown.' },
  ];

  return (
    <div data-testid="organizers-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag">{t('org_tag')}</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>{t('org_title')}</h1>
        <p className="sf-page-hero-desc">{t('org_desc')}</p>
        <Link to="/anfrage" className="sf-btn-primary" data-testid="org-inquiry-btn">{t('nav_cta')}</Link>
      </div>

      <section className="sf-section">
        <div className="sf-section-tag">{isDE ? 'Warum Veranstalter uns w\u00e4hlen' : 'Why organizers choose us'}</div>
        <h2 className="sf-section-title">{isDE ? 'Eventbereit.\nProfessionell.' : 'Event-ready.\nProfessional.'}</h2>
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
            <div className="sf-section-tag">{isDE ? 'Technische Daten' : 'Technical Data'}</div>
            <h2 className="sf-section-title" style={{ fontSize: '1.8rem' }}>{isDE ? 'Was Veranstalter\nwissen m\u00fcssen' : 'What organizers\nneed to know'}</h2>
            <ul className="sf-truck-list" style={{ marginTop: '1.5rem' }}>
              <li>{isDE ? 'Platzbedarf: 4\u20136m x 2.5\u20133m je Truck' : 'Space: 4-6m x 2.5-3m per truck'}</li>
              <li>{isDE ? 'Strom: 230V / 16A pro Truck' : 'Power: 230V / 16A per truck'}</li>
              <li>{isDE ? 'Wasser: Je nach Konzept' : 'Water: Depends on concept'}</li>
              <li>{isDE ? 'Aufbauzeit: 30\u201360 Minuten' : 'Setup: 30-60 minutes'}</li>
              <li>{isDE ? 'Ausgabe: bis 400 G\u00e4ste/h' : 'Output: up to 400 guests/h'}</li>
              <li>{isDE ? 'Einsatzgebiet: Ganze Schweiz' : 'Service area: All of Switzerland'}</li>
            </ul>
          </div>
          <div className="sf-whom-visual">
            <img src={TRUCK_IMG} alt="Truck" className="sf-whom-img-main" />
            <div className="sf-whom-badge">{isDE ? 'Download: PDF auf Anfrage' : 'Download: PDF on request'}</div>
          </div>
        </div>
      </section>

      <section className="sf-cta">
        <div className="sf-cta-eyebrow">{isDE ? 'F\u00fcr Veranstalter' : 'For Organizers'}</div>
        <h2 className="sf-cta-title">
          {isDE ? 'Interesse? Wir senden euch gerne unsere Unterlagen.' : 'Interested? We\'ll gladly send you our documents.'}
        </h2>
        <div className="sf-cta-actions">
          <Link to="/anfrage" className="sf-btn-primary">{t('nav_cta')}</Link>
        </div>
      </section>
    </div>
  );
}
