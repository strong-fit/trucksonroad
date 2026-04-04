"use client";
import { AdminLayout } from '@/views/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import { Download, FileText, CalendarDays, Users, HelpCircle, Truck } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function AdminExport() {
  const { t } = useLanguage();
  const EXPORTS = [
    { key: 'inquiries', label: t('admin_inquiries'), icon: FileText },
    { key: 'employees', label: t('admin_employees'), icon: Users },
    { key: 'calendar', label: t('admin_calendar'), icon: CalendarDays },
    { key: 'trucks', label: t('admin_trucks'), icon: Truck },
    { key: 'faqs', label: t('admin_faqs'), icon: HelpCircle },
  ];
  return (
    <AdminLayout title={t('admin_export')}>
      <p style={{ color: 'var(--adm-text-secondary)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
        Exportieren Sie alle Daten als CSV oder PDF.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
        {EXPORTS.map(exp => (
          <div key={exp.key} className="adm-detail" data-testid={`export-card-${exp.key}`} style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.6rem' }}>
              <div className="adm-stat-icon gold"><exp.icon size={16} /></div>
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{exp.label}</span>
            </div>
            <p style={{ color: 'var(--adm-text-muted)', fontSize: '0.78rem', marginBottom: '1rem', lineHeight: 1.5 }}>{exp.desc}</p>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <a href={`${API}/api/admin/export/${exp.key}?format=csv`} className="adm-btn adm-btn-secondary adm-btn-sm" data-testid={`export-csv-${exp.key}`} style={{ textDecoration: 'none' }}>
                <Download size={13} /> CSV
              </a>
              <a href={`${API}/api/admin/export/${exp.key}?format=pdf`} className="adm-btn adm-btn-primary adm-btn-sm" data-testid={`export-pdf-${exp.key}`} style={{ textDecoration: 'none' }}>
                <Download size={13} /> PDF
              </a>
            </div>
          </div>
        ))}
      </div>
    </AdminLayout>
  );
}
