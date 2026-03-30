import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Calendar } from '@/components/ui/calendar';
import { Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

export default function AdminCalendar() {
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

  const dayModifiers = {
    blocked: blockedDates,
  };

  const dayModifiersStyles = {
    blocked: { backgroundColor: 'rgba(239,68,68,0.2)', color: '#f87171', borderRadius: '4px' },
  };

  return (
    <AdminLayout title="Kalender">
      <div className="sf-cal-truck-selector">
        {trucks.map(t => (
          <button key={t.slug} className={`sf-truck-btn ${selectedTruck === t.slug ? 'active' : ''}`} onClick={() => setSelectedTruck(t.slug)} data-testid={`cal-truck-${t.slug}`}>
            {t.name_de}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <div>
          <div style={{ background: 'var(--sf-surface)', border: '1px solid var(--sf-border)', borderRadius: '12px', padding: '1rem', display: 'inline-block' }}>
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
            <div style={{ marginTop: '1.5rem', background: 'var(--sf-surface)', border: '1px solid var(--sf-border)', borderRadius: '8px', padding: '1.5rem' }}>
              <h4 style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, marginBottom: '1rem' }}>
                {format(selectedDate, 'dd.MM.yyyy')} blockieren
              </h4>
              <div className="sf-form-group" style={{ marginBottom: '0.8rem' }}>
                <label>Status</label>
                <select value={blockStatus} onChange={e => setBlockStatus(e.target.value)} style={{ background: 'var(--sf-bg)', border: '1px solid var(--sf-border)', borderRadius: '6px', padding: '0.5rem', color: 'var(--sf-white)' }} data-testid="block-status-select">
                  <option value="blocked">Blockiert</option>
                  <option value="reserved">Reserviert</option>
                  <option value="confirmed">Best\u00e4tigt</option>
                </select>
              </div>
              <div className="sf-form-group" style={{ marginBottom: '0.8rem' }}>
                <label>Notizen</label>
                <input value={blockNotes} onChange={e => setBlockNotes(e.target.value)} placeholder="Optional..." style={{ background: 'var(--sf-bg)', border: '1px solid var(--sf-border)', borderRadius: '6px', padding: '0.5rem', color: 'var(--sf-white)', width: '100%' }} data-testid="block-notes-input" />
              </div>
              <button className="sf-btn-primary sf-btn-sm" onClick={addBlock} data-testid="add-block-btn">
                Blockierung setzen
              </button>
            </div>
          )}
        </div>

        <div>
          <h4 style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, marginBottom: '1rem' }}>
            Blockierte Daten: {trucks.find(t => t.slug === selectedTruck)?.name_de || ''}
          </h4>
          <div className="sf-cal-block-list">
            {truckBlocks.length === 0 ? (
              <p style={{ color: 'var(--sf-gray)', fontSize: '0.85rem' }}>Keine Blockierungen f\u00fcr diesen Truck.</p>
            ) : (
              truckBlocks.sort((a, b) => a.date.localeCompare(b.date)).map(block => (
                <div key={block.id || block.date} className="sf-cal-block-item" data-testid={`block-${block.date}`}>
                  <div>
                    <strong>{block.date}</strong>
                    <span style={{ marginLeft: '0.8rem' }} className={`sf-status-badge sf-status-${block.status}`}>{block.status}</span>
                    {block.notes && <span style={{ marginLeft: '0.8rem', color: 'var(--sf-gray)', fontSize: '0.8rem' }}>{block.notes}</span>}
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
