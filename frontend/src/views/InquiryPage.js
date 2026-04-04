"use client";
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Calendar } from '@/components/ui/calendar';
import { Mail, Phone, MapPin, Upload } from 'lucide-react';
import { format } from 'date-fns';
import { de, fr, it } from 'date-fns/locale';
import FileUpload from '@/components/FileUpload';

const TRUCK_OPTIONS = ["Burger Truck", "Chicken Burger", "Bowl Truck", "Pocket Bowl", "Empanadas", "Retro Trailer", "Mehrere Trucks"];

export default function InquiryPage() {
  const { lang, t } = useLanguage();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const preselectedTruck = searchParams.get('truck') || '';
  const preselectedTypeIndex = searchParams.get('type');
  const eventTypes = t('form_event_types');
  const preselectedType = preselectedTypeIndex !== null && eventTypes[parseInt(preselectedTypeIndex)] ? eventTypes[parseInt(preselectedTypeIndex)] : '';
  const [calendarBlocks, setCalendarBlocks] = useState([]);
  const [selectedDate, setSelectedDate] = useState(undefined);
  const [selectedTrucks, setSelectedTrucks] = useState(preselectedTruck ? [preselectedTruck.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())] : []);
  const [extras, setExtras] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [inquiryId, setInquiryId] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [form, setForm] = useState({
    first_name: '', last_name: '', company: '', email: '', phone: '',
    event_time: '', location: '', guest_count: '', event_type: preselectedType,
    indoor_outdoor: 'Outdoor', budget: '', remarks: '',
    privacy_accepted: false, is_organizer: false
  });

  useEffect(() => {
    api.get('/availability').then(r => setCalendarBlocks(r.data)).catch(() => {});
  }, []);

  const toggleTruck = (name) => {
    setSelectedTrucks(prev => prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name]);
  };

  const toggleExtra = (name) => {
    setExtras(prev => prev.includes(name) ? prev.filter(e => e !== name) : [...prev, name]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.privacy_accepted) { toast.error(t('form_privacy_error')); return; }
    setSubmitting(true);
    try {
      const res = await api.post('/inquiries', {
        ...form,
        guest_count: parseInt(form.guest_count) || 0,
        event_date: selectedDate ? format(selectedDate, 'yyyy-MM-dd') : '',
        selected_trucks: selectedTrucks,
        extras,
        lang,
      });
      toast.success(t('form_success'));
      setInquiryId(res.data.id);
      setSubmitted(true);
    } catch (err) {
      toast.error(t('form_send_error'));
    } finally {
      setSubmitting(false);
    }
  };

  const blockedDates = calendarBlocks.filter(b => b.status === 'blocked' || b.status === 'confirmed').map(b => {
    const parts = b.date.split('-');
    return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
  });

  const dayModifiers = {
    booked: blockedDates,
  };

  const dayModifiersStyles = {
    booked: { backgroundColor: 'rgba(239,68,68,0.2)', color: '#f87171', borderRadius: '4px' },
  };

  if (submitted) {
    return (
      <div style={{ minHeight: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem' }} data-testid="inquiry-success">
        <h2 className="sf-section-title" style={{ textAlign: 'center', marginBottom: '1rem' }}>
          {t('form_thank_you')}
        </h2>
        <p style={{ color: 'var(--sf-gray)', textAlign: 'center', maxWidth: 500 }}>{t('form_success')}</p>

        {inquiryId && (
          <div style={{ width: '100%', maxWidth: 500, marginTop: '2rem' }} data-testid="inquiry-upload-section">
            <h3 style={{ color: 'var(--sf-cream)', fontSize: '1rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Upload size={18} /> {t('form_upload_title')}
            </h3>
            <p style={{ color: 'var(--sf-gray)', fontSize: '0.82rem', marginBottom: '1rem' }}>
              {t('form_upload_desc')}
            </p>
            <FileUpload inquiryId={inquiryId} files={uploadedFiles} onFilesChange={setUploadedFiles} />
          </div>
        )}

        {user && user.role === 'customer' && (
          <Link href="/konto" className="sf-btn-primary" style={{ marginTop: '1.5rem', textDecoration: 'none' }} data-testid="go-to-portal-btn">
            {t('form_go_portal')}
          </Link>
        )}
        {!user && (
          <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
            <p style={{ color: 'var(--sf-gray)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
              {t('form_register_hint')}
            </p>
            <Link href="/konto/registrieren" className="sf-btn-outline" style={{ textDecoration: 'none' }} data-testid="register-after-inquiry">
              {t('form_register_btn')}
            </Link>
          </div>
        )}
      </div>
    );
  }

  return (
    <div data-testid="inquiry-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag">{t('form_tag')}</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>{t('form_title')}</h1>
        <p className="sf-page-hero-desc">{t('form_desc')}</p>
      </div>

      <div className="sf-form-section">
        <div className="sf-form-info">
          <div className="sf-section-tag">{t('avail_tag')}</div>
          <h3 className="sf-section-title" style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>
            {t('form_choose_date')}
          </h3>
          <div style={{ background: 'var(--sf-surface)', border: '1px solid var(--sf-border)', borderRadius: '12px', padding: '1rem', display: 'inline-block' }}>
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={setSelectedDate}
              locale={lang === 'de' ? de : lang === 'fr' ? fr : lang === 'it' ? it : undefined}
              modifiers={dayModifiers}
              modifiersStyles={dayModifiersStyles}
              disabled={{ before: new Date() }}
              data-testid="availability-calendar"
            />
          </div>
          <div className="sf-avail-legend" style={{ marginTop: '1rem' }}>
            <span><span className="sf-avail-dot available" /> {t('avail_available')}</span>
            <span><span className="sf-avail-dot partial" /> {t('avail_partial')}</span>
            <span><span className="sf-avail-dot booked" /> {t('avail_booked')}</span>
          </div>

          <div style={{ marginTop: '3rem' }}>
            <div className="sf-form-contact"><Mail size={16} className="sf-form-contact-icon" /> <span>info@trucksonroad.ch</span></div>
            <div className="sf-form-contact"><Phone size={16} className="sf-form-contact-icon" /> <span>+41 xx xxx xx xx</span></div>
            <div className="sf-form-contact"><MapPin size={16} className="sf-form-contact-icon" /> <span>Zürich & ganze Schweiz</span></div>
          </div>
        </div>

        <form className="sf-form" onSubmit={handleSubmit} data-testid="inquiry-form">
          <div className="sf-form-row">
            <div className="sf-form-group">
              <label>{t('form_first_name')} *</label>
              <input required value={form.first_name} onChange={e => setForm({...form, first_name: e.target.value})} placeholder="Max" data-testid="input-first-name" />
            </div>
            <div className="sf-form-group">
              <label>{t('form_last_name')} *</label>
              <input required value={form.last_name} onChange={e => setForm({...form, last_name: e.target.value})} placeholder="Mustermann" data-testid="input-last-name" />
            </div>
          </div>
          <div className="sf-form-row">
            <div className="sf-form-group">
              <label>{t('form_email')} *</label>
              <input type="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="max@firma.ch" data-testid="input-email" />
            </div>
            <div className="sf-form-group">
              <label>{t('form_phone')} *</label>
              <input type="tel" required value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} placeholder="+41 79 xxx xx xx" data-testid="input-phone" />
            </div>
          </div>
          <div className="sf-form-group">
            <label>{t('form_company')}</label>
            <input value={form.company} onChange={e => setForm({...form, company: e.target.value})} placeholder="optional" data-testid="input-company" />
          </div>
          <div className="sf-form-row">
            <div className="sf-form-group">
              <label>{t('form_date')} *</label>
              <input type="text" readOnly value={selectedDate ? format(selectedDate, 'dd.MM.yyyy') : ''} placeholder={t('form_select_calendar')} data-testid="input-date" />
            </div>
            <div className="sf-form-group">
              <label>{t('form_time')}</label>
              <input value={form.event_time} onChange={e => setForm({...form, event_time: e.target.value})} placeholder="z.B. 12:00 – 20:00" data-testid="input-time" />
            </div>
          </div>
          <div className="sf-form-row">
            <div className="sf-form-group">
              <label>{t('form_location')} *</label>
              <input required value={form.location} onChange={e => setForm({...form, location: e.target.value})} placeholder="Zürich, Halle 7..." data-testid="input-location" />
            </div>
            <div className="sf-form-group">
              <label>{t('form_guests')} *</label>
              <input type="number" required value={form.guest_count} onChange={e => setForm({...form, guest_count: e.target.value})} placeholder="z.B. 200" data-testid="input-guests" />
            </div>
          </div>
          <div className="sf-form-group">
            <label>{t('form_event_type')} *</label>
            <select required value={form.event_type} onChange={e => setForm({...form, event_type: e.target.value})} data-testid="select-event-type">
              <option value="">{t('form_please_select')}</option>
              {t('form_event_types').map(type => <option key={type} value={type}>{type}</option>)}
            </select>
          </div>
          <div className="sf-form-group">
            <label>{t('form_trucks_label')}</label>
            <div className="sf-form-trucks">
              {TRUCK_OPTIONS.map(name => (
                <button key={name} type="button" className={`sf-truck-btn ${selectedTrucks.includes(name) ? 'active' : ''}`} onClick={() => toggleTruck(name)} data-testid={`truck-btn-${name.toLowerCase().replace(/\s/g, '-')}`}>
                  {name}
                </button>
              ))}
            </div>
          </div>
          <div className="sf-form-group">
            <label>{t('form_indoor')}</label>
            <select value={form.indoor_outdoor} onChange={e => setForm({...form, indoor_outdoor: e.target.value})} data-testid="select-indoor">
              {t('form_indoor_opts').map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
          <div className="sf-form-group">
            <label>{t('form_extras_label')}</label>
            <div className="sf-form-trucks">
              {t('form_extras').map(name => (
                <button key={name} type="button" className={`sf-truck-btn ${extras.includes(name) ? 'active' : ''}`} onClick={() => toggleExtra(name)} data-testid={`extra-btn-${name.toLowerCase().replace(/[\s/]/g, '-')}`}>
                  {name}
                </button>
              ))}
            </div>
          </div>
          <div className="sf-form-group">
            <label>{t('form_budget')}</label>
            <select value={form.budget} onChange={e => setForm({...form, budget: e.target.value})} data-testid="select-budget">
              {t('form_budget_opts').map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
          <div className="sf-form-group">
            <label>{t('form_remarks')}</label>
            <textarea value={form.remarks} onChange={e => setForm({...form, remarks: e.target.value})} placeholder={t('form_more_info')} data-testid="input-remarks" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label className="sf-form-check">
              <input type="checkbox" checked={form.privacy_accepted} onChange={e => setForm({...form, privacy_accepted: e.target.checked})} data-testid="checkbox-privacy" />
              {t('form_privacy')} *
            </label>
            <label className="sf-form-check">
              <input type="checkbox" checked={form.is_organizer} onChange={e => setForm({...form, is_organizer: e.target.checked})} data-testid="checkbox-organizer" />
              {t('form_is_organizer')}
            </label>
          </div>
          <button type="submit" className="sf-btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} disabled={submitting} data-testid="submit-inquiry-btn">
            {submitting ? t('form_sending') : t('form_submit')} &rarr;
          </button>
        </form>
      </div>
    </div>
  );
}
