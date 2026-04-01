import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { Menu, X, User } from 'lucide-react';

export default function Navbar() {
  const { lang, setLang, t } = useLanguage();
  const { user } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const links = [
    { to: '/', label: t('nav_home') },
    { to: '/#trucks', label: t('nav_trucks'), isHash: true },
    { to: '/fuer-veranstalter', label: t('nav_organizers') },
    { to: '/private-events', label: t('nav_private') },
    { to: '/ueber-uns', label: t('nav_about') },
    { to: '/kontakt', label: t('nav_contact') },
    { to: '/faq', label: t('nav_faq') },
  ];

  const handleHashLink = (hash) => {
    setMobileOpen(false);
    if (location.pathname === '/') {
      const el = document.getElementById(hash);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    } else {
      window.location.href = '/' + hash;
    }
  };

  return (
    <nav className="sf-nav" data-testid="main-navbar">
      <div className="sf-nav-inner">
        <Link to="/" className="sf-nav-logo" data-testid="nav-logo">
          <span className="sf-logo-accent">TRUCK</span>
          <span className="sf-logo-text">ON</span>
          <span className="sf-logo-accent">ROAD</span>
        </Link>

        <div className="sf-nav-links">
          {links.map((link) =>
            link.isHash ? (
              <button key={link.to} onClick={() => handleHashLink('trucks')} className="sf-nav-link" data-testid={`nav-link-trucks`}>
                {link.label}
              </button>
            ) : (
              <Link key={link.to} to={link.to} className={`sf-nav-link ${location.pathname === link.to ? 'active' : ''}`} data-testid={`nav-link-${link.to.replace('/', '') || 'home'}`}>
                {link.label}
              </Link>
            )
          )}
        </div>

        <div className="sf-nav-actions">
          <button
            className="sf-lang-toggle"
            onClick={() => setLang(lang === 'de' ? 'en' : 'de')}
            data-testid="language-toggle"
          >
            {lang === 'de' ? 'EN' : 'DE'}
          </button>
          {user && user.role !== 'admin' ? (
            <Link to="/konto" className="sf-nav-account" data-testid="nav-account-btn">
              <User size={15} /> {lang === 'de' ? 'Mein Konto' : 'My Account'}
            </Link>
          ) : !user ? (
            <Link to="/konto/login" className="sf-nav-account" data-testid="nav-login-btn">
              <User size={15} /> {lang === 'de' ? 'Anmelden' : 'Login'}
            </Link>
          ) : null}
          <Link to="/anfrage" className="sf-nav-cta" data-testid="nav-cta-button">
            {t('nav_cta')}
          </Link>
          <button
            className="sf-mobile-toggle"
            onClick={() => setMobileOpen(!mobileOpen)}
            data-testid="mobile-menu-toggle"
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="sf-mobile-menu" data-testid="mobile-menu">
          {links.map((link) =>
            link.isHash ? (
              <button key={link.to} onClick={() => handleHashLink('trucks')} className="sf-mobile-link">
                {link.label}
              </button>
            ) : (
              <Link key={link.to} to={link.to} className="sf-mobile-link" onClick={() => setMobileOpen(false)}>
                {link.label}
              </Link>
            )
          )}
          <Link to="/anfrage" className="sf-btn-primary" style={{ width: '100%', textAlign: 'center', marginTop: '1rem' }} onClick={() => setMobileOpen(false)}>
            {t('nav_cta')}
          </Link>
        </div>
      )}
    </nav>
  );
}
