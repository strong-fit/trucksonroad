import { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';

export default function FAQPage() {
  const { lang, t } = useLanguage();
  const [faqs, setFaqs] = useState([]);
  const [openFaq, setOpenFaq] = useState(null);

  useEffect(() => {
    api.get('/faqs').then(r => setFaqs(r.data)).catch(() => {});
  }, []);

  return (
    <div data-testid="faq-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag">{t('faq_tag')}</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>{t('faq_title')}</h1>
        <p className="sf-page-hero-desc">
          {lang === 'de'
            ? 'Hier findest du Antworten auf die häufigsten Fragen rund um unsere Foodtrucks, Buchungen und Abläufe.'
            : 'Here you will find answers to the most common questions about our food trucks, bookings, and processes.'}
        </p>
      </div>
      <section className="sf-section" style={{ paddingTop: '2rem' }}>
        <div className="sf-faq-grid">
          {faqs.map((faq) => (
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
      </section>
    </div>
  );
}
