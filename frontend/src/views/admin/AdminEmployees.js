"use client";
import { useState, useEffect } from 'react';
import { AdminLayout } from '@/views/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Save, Plus, Trash2, Users, Edit2 } from 'lucide-react';

export default function AdminEmployees() {
  const { t } = useLanguage();
  const [employees, setEmployees] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', phone: '', role: '', notes: '', is_active: true });

  const load = () => api.get('/admin/employees').then(r => setEmployees(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const startNew = () => {
    setEditing('new');
    setForm({ name: '', phone: '', role: '', notes: '', is_active: true });
  };

  const startEdit = (emp) => {
    setEditing(emp.id);
    setForm({ name: emp.name, phone: emp.phone || '', role: emp.role || '', notes: emp.notes || '', is_active: emp.is_active !== false });
  };

  const cancel = () => setEditing(null);

  const save = async () => {
    if (!form.name) { toast.error('Name ist Pflichtfeld'); return; }
    try {
      if (editing === 'new') {
        await api.post('/admin/employees', form);
        toast.success('Mitarbeiter erstellt');
      } else {
        await api.put(`/admin/employees/${editing}`, form);
        toast.success('Mitarbeiter aktualisiert');
      }
      cancel();
      load();
    } catch { toast.error('Fehler'); }
  };

  const remove = async (id) => {
    if (!window.confirm('Mitarbeiter wirklich loeschen?')) return;
    try {
      await api.delete(`/admin/employees/${id}`);
      toast.success('Mitarbeiter geloescht');
      load();
    } catch { toast.error('Fehler'); }
  };

  return (
    <AdminLayout title={t('admin_employees')}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <p style={{ color: 'var(--adm-text-secondary)', fontSize: '0.85rem' }}>{employees.length} Mitarbeiter</p>
        <button className="adm-btn adm-btn-primary" onClick={startNew} data-testid="add-employee-btn">
          <Plus size={15} /> Neuer Mitarbeiter
        </button>
      </div>

      {editing && (
        <div className="adm-detail" style={{ marginBottom: '1.25rem' }} data-testid="employee-edit-form">
          <div className="adm-detail-header">
            <span className="adm-detail-title">{editing === 'new' ? 'Neuer Mitarbeiter' : 'Bearbeiten'}</span>
            <button className="adm-detail-close" onClick={cancel}>&times;</button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div>
              <div className="adm-form-label">Name *</div>
              <input className="adm-input" value={form.name} onChange={e => setForm({...form, name: e.target.value})} data-testid="emp-name-input" />
            </div>
            <div>
              <div className="adm-form-label">Telefon</div>
              <input className="adm-input" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} data-testid="emp-phone-input" />
            </div>
            <div>
              <div className="adm-form-label">Rolle</div>
              <input className="adm-input" value={form.role} onChange={e => setForm({...form, role: e.target.value})} placeholder="z.B. Koch, Service, Fahrer" data-testid="emp-role-input" />
            </div>
            <div>
              <div className="adm-form-label">Notizen</div>
              <input className="adm-input" value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} data-testid="emp-notes-input" />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={form.is_active} onChange={e => setForm({...form, is_active: e.target.checked})} /> Aktiv
            </label>
            <div style={{ flex: 1 }} />
            <button className="adm-btn adm-btn-secondary" onClick={cancel}>Abbrechen</button>
            <button className="adm-btn adm-btn-primary" onClick={save} data-testid="emp-save-btn"><Save size={14} /> Speichern</button>
          </div>
        </div>
      )}

      <div className="adm-table-wrap" data-testid="employees-table-wrap">
        {employees.length === 0 ? (
          <div className="adm-empty">
            <div className="adm-empty-icon"><Users size={22} /></div>
            Noch keine Mitarbeiter erfasst.
          </div>
        ) : (
          <table className="adm-table" data-testid="employees-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Telefon</th>
                <th>Rolle</th>
                <th>Notizen</th>
                <th>Status</th>
                <th style={{ width: '120px' }}></th>
              </tr>
            </thead>
            <tbody>
              {employees.map(emp => (
                <tr key={emp.id} data-testid={`emp-row-${emp.id}`}>
                  <td style={{ fontWeight: 500 }}>{emp.name}</td>
                  <td>{emp.phone || '-'}</td>
                  <td>{emp.role || '-'}</td>
                  <td style={{ color: 'var(--adm-text-muted)', fontSize: '0.78rem' }}>{emp.notes || '-'}</td>
                  <td>
                    <span className={`adm-badge ${emp.is_active !== false ? 'adm-badge-confirmed' : 'adm-badge-cancelled'}`}>
                      <span className="adm-badge-dot" />
                      {emp.is_active !== false ? 'Aktiv' : 'Inaktiv'}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.3rem' }}>
                      <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => startEdit(emp)} data-testid={`emp-edit-${emp.id}`}><Edit2 size={12} /></button>
                      <button className="adm-btn adm-btn-danger adm-btn-sm" onClick={() => remove(emp.id)} data-testid={`emp-delete-${emp.id}`} style={{ padding: '0.25rem 0.4rem' }}><Trash2 size={13} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </AdminLayout>
  );
}
