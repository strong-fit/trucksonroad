"use client";
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { useCookieConsent } from '@/contexts/CookieConsentContext';
import { Mail, Phone, MapPin, Cookie } from 'lucide-react';

export default function Footer() {
  const { t } = useLanguage();
  const { openBanner } = useCookieConsent();

  return (
    <>
      <footer className="sf-footer" data-testid="main-footer">
        <div>
          <div className="sf-nav-logo" style={{ marginBottom: '0.8rem' }}>
            <span className="sf-logo-accent">TRUCKS</span>
            <span className="sf-logo-text">on</span>
            <span className="sf-logo-accent">ROAD</span>
          </div>
          <p className="sf-footer-desc">{t('footer_desc')}</p>
        </div>

        <div>
          <div className="sf-footer-heading">Trucks</div>
          <Link href="/trucks/burger-truck" className="sf-footer-link">Burger Truck</Link>
          <Link href="/trucks/chicken-burger" className="sf-footer-link">Chicken Burger</Link>
          <Link href="/trucks/bowl-truck" className="sf-footer-link">Bowl Truck</Link>
          <Link href="/trucks/pocket-bowl" className="sf-footer-link">Pocket Bowl</Link>
          <Link href="/trucks/empanadas" className="sf-footer-link">Empanadas</Link>
          <Link href="/trucks/retro-trailer" className="sf-footer-link">Retro Trailer</Link>
        </div>

        <div>
          <div className="sf-footer-heading">Events</div>
          <Link href="/fuer-veranstalter" className="sf-footer-link">{t('nav_organizers')}</Link>
          <Link href="/private-events" className="sf-footer-link">{t('nav_private')}</Link>
          <Link href="/anfrage" className="sf-footer-link">{t('nav_inquiry')}</Link>
          <Link href="/faq" className="sf-footer-link">{t('nav_faq')}</Link>
          <Link href="/blog" className="sf-footer-link">{t('nav_blog')}</Link>
        </div>

        <div>
          <div className="sf-footer-heading">{t('footer_contact')}</div>
          <div className="sf-footer-contact">
            <Mail size={14} /> <span>info@trucksonroad.ch</span>
          </div>
          <div className="sf-footer-contact">
            <Phone size={14} /> <span>+41 79 696 98 99</span>
          </div>
          <div className="sf-footer-contact">
            <MapPin size={14} /> <span>Bahnhofstrasse 75, 8620 Wetzikon</span>
          </div>
        </div>
      </footer>

      <div className="sf-footer-bottom" data-testid="footer-bottom">
        <span>&copy; 2026 TRUCKSonROAD &ndash; {t('footer_rights')}</span>
        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <Link href="/datenschutz" data-testid="footer-link-privacy">{t('footer_privacy')}</Link>
          <Link href="/impressum" data-testid="footer-link-imprint">{t('footer_imprint')}</Link>
          <Link href="/agb" data-testid="footer-link-terms">{t('footer_terms')}</Link>
          <button
            type="button"
            onClick={openBanner}
            data-testid="footer-cookie-settings"
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'inherit', fontSize: 'inherit', font: 'inherit',
              padding: 0, display: 'inline-flex', alignItems: 'center', gap: '0.35rem'
            }}
          >
            <Cookie size={13} /> Cookie-Einstellungen
          </button>
          <Link href="/admin/login" style={{ opacity: 0.4 }}>Admin</Link>
        </div>
      </div>

      <a
        href="https://api.whatsapp.com/send/?phone=41796969899&text&type=phone_number&app_absent=0"
        className="sf-whatsapp-btn"
        target="_blank"
        rel="noopener noreferrer"
        data-testid="whatsapp-button"
        title="WhatsApp"
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="white">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
      </a>
    </>
  );
}
