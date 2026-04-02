import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Calendar } from '@/components/ui/calendar';
import { Trash2, CalendarX } from 'lucide-react';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

export default function AdminCalendar() {
  const { t } = useLanguage();
  const [trucks, setTrucks] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [selectedTruck, setSelectedTruck] = useState('');
  const [selectedDate, setSelectedDate] = useState(undefined);
  const [blockStatus, setBlockStatus] = useState('blocked');
  const [blockNotes, setBlockNotes] = useState('');

  const load = () => {
    api.get('/admin/trucks').then(r => {
      setTrucks(r.data);
      if (r.data.length > 0 && !selectedTruck) setSelectedTruck(r.data[0].slug);
    }).catch(() => {});
    api.get('/admin/calendar').then(r => setBlocks(r.data)).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const truckBlocks = blocks.filter(b => b.truck_slug === selectedTruck);
  const blockedDates = truckBlocks.map(b => new Date(b.date));

  const addBlock = async () => {
    if (!selectedDate || !selectedTruck) return;
    try {
      await api.post('/admin/calendar', {
        truck_slug: selectedTruck,
        date: format(selectedDate, 'yyyy-MM-dd'),
        status: blockStatus,
        notes: blockNotes,
      });
      toast.success('Datum blockiert');
      setBlockNotes('');
      load();
    } catch { toast.error('Fehler'); }
  };

  const removeBlock = async (blockId) => {
    try {
      await api.delete(`/admin/calendar/${blockId}`);
      toast.success('Block entfernt');
      load();
    } catch { toast.error('Fehler'); }
  };

  const dayModifiers = { blocked: blockedDates };
  const dayModifiersStyles = {
    blocked: { backgroundColor: 'rgba(239,68,68,0.12)', color: '#dc2626', borderRadius: '6px' },
  };

  return (
    <AdminLayout title={t('admin_calendar')}>
      <div className="adm-filters" style={{ marginBottom: '1.25rem' }} data-testid="calendar-truck-selector">
        {trucks.map(t => (
          <button
            key={t.slug}
            className={`adm-filter-btn ${selectedTruck === t.slug ? 'active' : ''}`}
            onClick={() => setSelectedTruck(t.slug)}
            data-testid={`cal-truck-${t.slug}`}
          >
            {t.name_de}
          </button>
        ))}
      </div>

      <div className="adm-cal-wrap">
        <div>
          <div className="adm-cal-card" data-testid="calendar-card">
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={setSelectedDate}
              locale={de}
              modifiers={dayModifiers}
              modifiersStyles={dayModifiersStyles}
              data-testid="admin-calendar"
            />
          </div>

          {selectedDate && (
            <div className="adm-cal-card" style={{ marginTop: '1rem' }} data-testid="block-form">
              <h4>{format(selectedDate, 'dd.MM.yyyy')} blockieren</h4>
              <div style={{ marginBottom: '0.75rem' }}>
                <div className="adm-form-label">Status</div>
                <select className="adm-select" value={blockStatus} onChange={e => setBlockStatus(e.target.value)} data-testid="block-status-select">
                  <option value="blocked">Blockiert</option>
                  <option value="reserved">Reserviert</option>
                  <option value="confirmed">Bestaetigt</option>
                </select>
              </div>
              <div style={{ marginBottom: '0.75rem' }}>
                <div className="adm-form-label">Notizen</div>
                <input className="adm-input" value={blockNotes} onChange={e => setBlockNotes(e.target.value)} placeholder="Optional..." data-testid="block-notes-input" />
              </div>
              <button className="adm-btn adm-btn-primary adm-btn-sm" onClick={addBlock} data-testid="add-block-btn">
                Blockierung setzen
              </button>
            </div>
          )}
        </div>

        <div>
          <div className="adm-cal-card" data-testid="blocks-list-card">
            <h4>Blockierte Daten: {trucks.find(t => t.slug === selectedTruck)?.name_de || ''}</h4>
            {truckBlocks.length === 0 ? (
              <div className="adm-empty" data-testid="no-blocks-msg">
                <div className="adm-empty-icon"><CalendarX size={20} /></div>
                Keine Blockierungen fuer diesen Truck.
              </div>
            ) : (
              truckBlocks.sort((a, b) => a.date.localeCompare(b.date)).map(block => (
                <div key={block.id || block.date} className="adm-block-item" data-testid={`block-${block.date}`}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
                    <strong>{block.date}</strong>
                    <span className={`adm-badge adm-badge-${block.status === 'blocked' ? 'cancelled' : block.status === 'reserved' ? 'in_review' : 'confirmed'}`}>
                      <span className="adm-badge-dot" />
                      {block.status}
                    </span>
                    {block.notes && <span style={{ color: 'var(--adm-text-muted)', fontSize: '0.78rem' }}>{block.notes}</span>}
                  </div>
                  <button onClick={() => removeBlock(block.id)} data-testid={`remove-block-${block.date}`}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
