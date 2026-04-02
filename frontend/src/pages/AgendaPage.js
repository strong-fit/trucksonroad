import { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { CalendarDays, MapPin, Truck, Calendar } from 'lucide-react';

export default function AgendaPage() {
  const { t, lang } = useLanguage();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/agenda').then(r => { setEvents(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const dateFmt = (d) => {
    if (!d) return '–';
    try {
      const locale = lang === 'de' ? 'de-CH' : lang === 'fr' ? 'fr-CH' : lang === 'it' ? 'it-CH' : 'en-GB';
      return new Date(d).toLocaleDateString(locale, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    } catch { return d; }
  };

  return (
    <section className="sf-section" data-testid="agenda-page">
      <div className="sf-container" style={{ maxWidth: '900px' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <div className="sf-eyebrow" data-testid="agenda-eyebrow">
            <Calendar size={14} /> {t('agenda_upcoming')}
          </div>
          <h1 className="sf-section-title" data-testid="agenda-title">{t('agenda_title')}</h1>
          <p className="sf-section-subtitle" data-testid="agenda-subtitle">{t('agenda_subtitle')}</p>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--sf-gray)' }}>{t('loading')}</div>
        ) : events.length === 0 ? (
          <div className="sf-agenda-empty" data-testid="agenda-empty">
            <CalendarDays size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
            <p style={{ color: 'var(--sf-gray)' }}>{t('agenda_no_events')}</p>
          </div>
        ) : (
          <div className="sf-agenda-list" data-testid="agenda-list">
            {events.map((ev, i) => (
              <div key={ev.id || i} className="sf-agenda-item" data-testid={`agenda-event-${i}`}>
                <div className="sf-agenda-date-col">
                  <div className="sf-agenda-date-badge">
                    <CalendarDays size={14} />
                    <span>{dateFmt(ev.event_date)}</span>
                  </div>
                </div>
                <div className="sf-agenda-info">
                  <div className="sf-agenda-event-name">
                    {ev.event_name || ev.event_type || t('agenda_event_name')}
                  </div>
                  <div className="sf-agenda-meta">
                    {ev.location && (
                      <span className="sf-agenda-meta-item">
                        <MapPin size={13} /> {ev.location}
                      </span>
                    )}
                    {ev.selected_trucks?.length > 0 && (
                      <span className="sf-agenda-meta-item">
                        <Truck size={13} /> {ev.selected_trucks.join(', ')}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
