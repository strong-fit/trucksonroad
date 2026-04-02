import { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { Menu, X, User, ChevronDown } from 'lucide-react';

const LANG_LABELS = { de: 'DE', en: 'EN', fr: 'FR', it: 'IT' };

export default function Navbar() {
  const { lang, setLang, t, SUPPORTED_LANGS } = useLanguage();
  const { user } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [langOpen, setLangOpen] = useState(false);
  const langRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    const handler = (e) => { if (langRef.current && !langRef.current.contains(e.target)) setLangOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const links = [
    { to: '/', label: t('nav_home') },
    { to: '/#trucks', label: t('nav_trucks'), isHash: true },
    { to: '/fuer-veranstalter', label: t('nav_organizers') },
    { to: '/private-events', label: t('nav_private') },
    { to: '/ueber-uns', label: t('nav_about') },
    { to: '/kontakt', label: t('nav_contact') },
    { to: '/faq', label: t('nav_faq') },
    { to: '/agenda', label: t('nav_agenda') },
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
          <span className="sf-logo-accent">TRUCKS</span>
          <span className="sf-logo-text">ON</span>
          <span className="sf-logo-accent">ROAD</span>
        </Link>

        <div className="sf-nav-links">
          {links.map((link) =>
            link.isHash ? (
              <button key={link.to} onClick={() => handleHashLink('trucks')} className="sf-nav-link" data-testid="nav-link-trucks">
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
          <div className="sf-lang-dropdown" ref={langRef} data-testid="language-selector">
            <button
              className="sf-lang-toggle"
              onClick={() => setLangOpen(!langOpen)}
              data-testid="language-toggle"
            >
              {LANG_LABELS[lang]} <ChevronDown size={12} style={{ marginLeft: '2px', transition: 'transform 0.2s', transform: langOpen ? 'rotate(180deg)' : 'none' }} />
            </button>
            {langOpen && (
              <div className="sf-lang-menu" data-testid="language-menu">
                {SUPPORTED_LANGS.map((l) => (
                  <button
                    key={l}
                    className={`sf-lang-option ${l === lang ? 'active' : ''}`}
                    onClick={() => { setLang(l); setLangOpen(false); }}
                    data-testid={`lang-option-${l}`}
                  >
                    {LANG_LABELS[l]}
                  </button>
                ))}
              </div>
            )}
          </div>
          {user && user.role !== 'admin' ? (
            <Link to="/konto" className="sf-nav-account" data-testid="nav-account-btn">
              <User size={15} /> {t('nav_account')}
            </Link>
          ) : !user ? (
            <Link to="/konto/login" className="sf-nav-account" data-testid="nav-login-btn">
              <User size={15} /> {t('nav_login')}
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
          <div className="sf-mobile-lang" data-testid="mobile-lang-selector">
            {SUPPORTED_LANGS.map((l) => (
              <button
                key={l}
                className={`sf-mobile-lang-btn ${l === lang ? 'active' : ''}`}
                onClick={() => { setLang(l); }}
                data-testid={`mobile-lang-${l}`}
              >
                {LANG_LABELS[l]}
              </button>
            ))}
          </div>
          <Link to="/anfrage" className="sf-btn-primary" style={{ width: '100%', textAlign: 'center', marginTop: '1rem' }} onClick={() => setMobileOpen(false)}>
            {t('nav_cta')}
          </Link>
        </div>
      )}
    </nav>
  );
}
