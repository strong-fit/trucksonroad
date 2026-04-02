import { useState, useEffect } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { DollarSign, TrendingUp, TrendingDown, BarChart3, Save } from 'lucide-react';

export default function AdminFinance() {
  const { t } = useLanguage();
  const [overview, setOverview] = useState(null);
  const [inquiries, setInquiries] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({});

  const load = () => {
    api.get('/admin/finance/overview').then(r => setOverview(r.data)).catch(() => {});
    api.get('/admin/inquiries').then(r => setInquiries(r.data.filter(i => i.status === 'confirmed' || i.status === 'offer_sent'))).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const startEdit = (inq) => {
    setEditing(inq.id);
    setForm({
      revenue: inq.revenue || 0, personnel_cost: inq.personnel_cost || 0,
      material_cost: inq.material_cost || 0, travel_cost: inq.travel_cost || 0,
      other_cost: inq.other_cost || 0, finance_notes: inq.finance_notes || '',
    });
  };

  const saveFinance = async () => {
    try {
      await api.put(`/admin/inquiries/${editing}/finance`, form);
      toast.success('Finanzdaten gespeichert');
      setEditing(null);
      load();
    } catch { toast.error('Fehler'); }
  };

  const fmt = (n) => `CHF ${(n || 0).toLocaleString('de-CH', { minimumFractionDigits: 0 })}`;

  return (
    <AdminLayout title={t('admin_finance')}>
      {overview && (
        <div className="adm-stats" data-testid="finance-stats">
          <div className="adm-stat-card">
            <div className="adm-stat-label">Gesamtumsatz</div>
            <div className="adm-stat-row">
              <div className="adm-stat-num" style={{ fontSize: '1.8rem', color: 'var(--adm-text)' }} data-testid="total-revenue">{fmt(overview.total_revenue)}</div>
              <div className="adm-stat-icon green"><TrendingUp size={18} /></div>
            </div>
          </div>
          <div className="adm-stat-card">
            <div className="adm-stat-label">Gesamtkosten</div>
            <div className="adm-stat-row">
              <div className="adm-stat-num" style={{ fontSize: '1.8rem', color: 'var(--adm-text)' }} data-testid="total-costs">{fmt(overview.total_costs)}</div>
              <div className="adm-stat-icon" style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444' }}><TrendingDown size={18} /></div>
            </div>
          </div>
          <div className="adm-stat-card">
            <div className="adm-stat-label">Gewinn</div>
            <div className="adm-stat-row">
              <div className="adm-stat-num" style={{ fontSize: '1.8rem', color: overview.total_profit >= 0 ? '#22c55e' : '#ef4444' }} data-testid="total-profit">{fmt(overview.total_profit)}</div>
              <div className="adm-stat-icon gold"><DollarSign size={18} /></div>
            </div>
          </div>
          <div className="adm-stat-card">
            <div className="adm-stat-label">Events erfasst</div>
            <div className="adm-stat-row">
              <div className="adm-stat-num" style={{ fontSize: '1.8rem' }} data-testid="events-count">{overview.events_with_finance}</div>
              <div className="adm-stat-icon blue"><BarChart3 size={18} /></div>
            </div>
          </div>
        </div>
      )}

      {/* By Truck */}
      {overview && Object.keys(overview.by_truck).length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.5rem' }}>
          <div className="adm-table-wrap" data-testid="finance-by-truck">
            <div className="adm-table-header"><span className="adm-table-title">Umsatz pro Truck</span></div>
            <table className="adm-table">
              <thead><tr><th>Truck</th><th>Events</th><th>Umsatz</th><th>Kosten</th><th>Gewinn</th></tr></thead>
              <tbody>
                {Object.entries(overview.by_truck).map(([name, d]) => (
                  <tr key={name}>
                    <td style={{ fontWeight: 500 }}>{name}</td>
                    <td>{d.count}</td>
                    <td style={{ color: '#22c55e' }}>{fmt(d.revenue)}</td>
                    <td style={{ color: '#ef4444' }}>{fmt(d.costs)}</td>
                    <td style={{ fontWeight: 600, color: d.revenue - d.costs >= 0 ? '#22c55e' : '#ef4444' }}>{fmt(d.revenue - d.costs)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="adm-table-wrap" data-testid="finance-by-month">
            <div className="adm-table-header"><span className="adm-table-title">Umsatz pro Monat</span></div>
            <table className="adm-table">
              <thead><tr><th>Monat</th><th>Events</th><th>Umsatz</th><th>Kosten</th><th>Gewinn</th></tr></thead>
              <tbody>
                {Object.entries(overview.by_month).map(([month, d]) => (
                  <tr key={month}>
                    <td style={{ fontWeight: 500 }}>{month}</td>
                    <td>{d.count}</td>
                    <td style={{ color: '#22c55e' }}>{fmt(d.revenue)}</td>
                    <td style={{ color: '#ef4444' }}>{fmt(d.costs)}</td>
                    <td style={{ fontWeight: 600, color: d.revenue - d.costs >= 0 ? '#22c55e' : '#ef4444' }}>{fmt(d.revenue - d.costs)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Events List */}
      <div className="adm-table-wrap" data-testid="finance-events-table">
        <div className="adm-table-header"><span className="adm-table-title">Events - Finanzdaten</span></div>
        <table className="adm-table">
          <thead>
            <tr><th>Event</th><th>Datum</th><th>Umsatz</th><th>Personal</th><th>Material</th><th>Fahrt</th><th>Sonstig</th><th>Gewinn</th><th></th></tr>
          </thead>
          <tbody>
            {inquiries.map(inq => {
              const rev = inq.revenue || 0;
              const costs = (inq.personnel_cost || 0) + (inq.material_cost || 0) + (inq.travel_cost || 0) + (inq.other_cost || 0);
              const profit = rev - costs;
              return (
                <tr key={inq.id} data-testid={`finance-row-${inq.id}`}>
                  <td style={{ fontWeight: 500 }}>{inq.first_name || inq.name} {inq.last_name || ''}</td>
                  <td>{inq.event_date || '-'}</td>
                  {editing === inq.id ? (
                    <>
                      <td><input className="adm-input" type="number" value={form.revenue} onChange={e => setForm({...form, revenue: parseFloat(e.target.value) || 0})} style={{ width: '80px' }} data-testid="fin-revenue" /></td>
                      <td><input className="adm-input" type="number" value={form.personnel_cost} onChange={e => setForm({...form, personnel_cost: parseFloat(e.target.value) || 0})} style={{ width: '70px' }} /></td>
                      <td><input className="adm-input" type="number" value={form.material_cost} onChange={e => setForm({...form, material_cost: parseFloat(e.target.value) || 0})} style={{ width: '70px' }} /></td>
                      <td><input className="adm-input" type="number" value={form.travel_cost} onChange={e => setForm({...form, travel_cost: parseFloat(e.target.value) || 0})} style={{ width: '70px' }} /></td>
                      <td><input className="adm-input" type="number" value={form.other_cost} onChange={e => setForm({...form, other_cost: parseFloat(e.target.value) || 0})} style={{ width: '70px' }} /></td>
                      <td style={{ fontWeight: 600, color: (form.revenue - form.personnel_cost - form.material_cost - form.travel_cost - form.other_cost) >= 0 ? '#22c55e' : '#ef4444' }}>
                        {fmt(form.revenue - form.personnel_cost - form.material_cost - form.travel_cost - form.other_cost)}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.3rem' }}>
                          <button className="adm-btn adm-btn-primary adm-btn-sm" onClick={saveFinance} data-testid="fin-save-btn"><Save size={12} /></button>
                          <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => setEditing(null)}>X</button>
                        </div>
                      </td>
                    </>
                  ) : (
                    <>
                      <td style={{ color: rev > 0 ? '#22c55e' : 'var(--adm-text-muted)' }}>{rev > 0 ? fmt(rev) : '-'}</td>
                      <td style={{ color: 'var(--adm-text-muted)', fontSize: '0.78rem' }}>{inq.personnel_cost > 0 ? fmt(inq.personnel_cost) : '-'}</td>
                      <td style={{ color: 'var(--adm-text-muted)', fontSize: '0.78rem' }}>{inq.material_cost > 0 ? fmt(inq.material_cost) : '-'}</td>
                      <td style={{ color: 'var(--adm-text-muted)', fontSize: '0.78rem' }}>{inq.travel_cost > 0 ? fmt(inq.travel_cost) : '-'}</td>
                      <td style={{ color: 'var(--adm-text-muted)', fontSize: '0.78rem' }}>{inq.other_cost > 0 ? fmt(inq.other_cost) : '-'}</td>
                      <td style={{ fontWeight: 600, color: profit >= 0 ? '#22c55e' : '#ef4444' }}>{(rev > 0 || costs > 0) ? fmt(profit) : '-'}</td>
                      <td><button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => startEdit(inq)} data-testid={`fin-edit-${inq.id}`}>Bearbeiten</button></td>
                    </>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </AdminLayout>
  );
}
