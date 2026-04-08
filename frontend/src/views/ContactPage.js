"use client";
import { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import Link from 'next/link';
import { Mail, Phone, MapPin, Clock, Send } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function ContactPage({ initialInfo }) {
  const { lang, t } = useLanguage();
  const [info, setInfo] = useState({
    company_name: 'TRUCKSonROAD GmbH',
    address: 'Bahnhofstrasse 75, 8620 Wetzikon',
    phone: '+41 79 696 98 99',
    email: 'info@trucksonroad.ch',
    ...(initialInfo || {}),
  });
  const [form, setForm] = useState({ name: '', email: '', phone: '', message: '' });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (initialInfo?.company_name || initialInfo?.email || initialInfo?.phone) return;
    api.get('/contact-info').then(r => setInfo(r.data)).catch(() => {});
  }, [initialInfo]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await api.post('/inquiries', {
        first_name: form.name, last_name: '', email: form.email, phone: form.phone,
        event_date: '-', location: '-', guest_count: 0, event_type: 'Kontaktanfrage',
        remarks: form.message, selected_trucks: [], extras: [], privacy_accepted: true, lang,
      });
      toast.success(t('contact_success'));
      setForm({ name: '', email: '', phone: '', message: '' });
    } catch {
      toast.error('Fehler beim Senden');
    }
    setSending(false);
  };

  return (
    <div className="sf-page" data-testid="contact-page">
      <section className="sf-section">
        <div className="sf-section-inner" style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div className="sf-tag" data-testid="contact-tag">{t('contact_tag')}</div>
          <h1 className="sf-section-title">
            {t('contact_title_1')} <span className="gold">{t('contact_title_2')}</span>
          </h1>
          <p className="sf-section-desc">{t('contact_desc')}</p>

          <div className="sf-contact-grid" data-testid="contact-grid">
            <div className="sf-contact-info" data-testid="contact-info-card">
              <h2 className="sf-subsection-title">{t('contact_info_title')}</h2>

              <div className="sf-contact-item" data-testid="contact-address">
                <div className="sf-contact-item-icon"><MapPin size={18} /></div>
                <div>
                  <div className="sf-contact-item-label">{t('contact_address')}</div>
                  <div className="sf-contact-item-value">
                    {info.company_name}<br/>{info.address}<br/>
                    <span style={{ fontSize: '0.8rem', color: 'var(--sf-gray)' }}>Geschäftsführer: Alexander Araujo</span>
                  </div>
                </div>
              </div>

              <div className="sf-contact-item" data-testid="contact-phone">
                <div className="sf-contact-item-icon"><Phone size={18} /></div>
                <div>
                  <div className="sf-contact-item-label">{t('contact_phone')}</div>
                  <div className="sf-contact-item-value">
                    <a href={`tel:${info.phone.replace(/\s/g, '')}`} style={{ color: 'var(--sf-cream)' }}>{info.phone}</a>
                  </div>
                </div>
              </div>

              <div className="sf-contact-item" data-testid="contact-email">
                <div className="sf-contact-item-icon"><Mail size={18} /></div>
                <div>
                  <div className="sf-contact-item-label">{t('contact_email_label')}</div>
                  <div className="sf-contact-item-value">
                    <a href={`mailto:${info.email}`} style={{ color: 'var(--sf-cream)' }}>{info.email}</a>
                  </div>
                </div>
              </div>

              <div className="sf-contact-item" data-testid="contact-hours">
                <div className="sf-contact-item-icon"><Clock size={18} /></div>
                <div>
                  <div className="sf-contact-item-label">{t('contact_hours')}</div>
                  <div className="sf-contact-item-value">{t('contact_hours_value')}</div>
                </div>
              </div>
            </div>

            <form className="sf-contact-form" onSubmit={handleSubmit} data-testid="contact-form">
              <h2 className="sf-subsection-title">{t('contact_form_title')}</h2>
              <div className="sf-contact-form-group">
                <label>{t('contact_form_name')}</label>
                <input type="text" required value={form.name} onChange={e => setForm({...form, name: e.target.value})} data-testid="contact-name-input" />
              </div>
              <div className="sf-contact-form-row">
                <div className="sf-contact-form-group">
                  <label>{t('contact_form_email')}</label>
                  <input type="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})} data-testid="contact-email-input" />
                </div>
                <div className="sf-contact-form-group">
                  <label>{t('contact_form_phone')}</label>
                  <input type="tel" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} data-testid="contact-phone-input" />
                </div>
              </div>
              <div className="sf-contact-form-group">
                <label>{t('contact_form_message')}</label>
                <textarea rows="5" required value={form.message} onChange={e => setForm({...form, message: e.target.value})} data-testid="contact-message-input" />
              </div>
              <button type="submit" className="sf-btn-primary" disabled={sending} data-testid="contact-submit-btn" style={{ width: '100%' }}>
                <Send size={16} style={{ marginRight: '0.5rem' }} />
                {sending ? t('contact_sending') : t('contact_send')}
              </button>
            </form>
          </div>
        </div>
      </section>
    </div>
  );
}
