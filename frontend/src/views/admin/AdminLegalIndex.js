"use client";
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { AdminLayout } from '@/views/admin/AdminDashboard';
import api from '@/lib/api';
import { FileText, ChevronRight, ShieldCheck, Building2 } from 'lucide-react';

const DOC_META = [
  {
    key: 'agb',
    title: 'AGB',
    description: 'Allgemeine Geschäftsbedingungen — Buchung, Stornierung, Zahlung, Haftung.',
    icon: FileText,
    color: '#4db6ac',
  },
  {
    key: 'datenschutz',
    title: 'Datenschutzerklärung',
    description: 'DSGVO + nDSG-konform. Datenkategorien, Zwecke, Rechte, Cookies.',
    icon: ShieldCheck,
    color: '#d4af37',
  },
  {
    key: 'impressum',
    title: 'Impressum',
    description: 'Anbieterkennzeichnung, Haftungsausschluss, Urheberrechte.',
    icon: Building2,
    color: '#9c89b8',
  },
];

export default function AdminLegalIndex() {
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    api.get('/admin/legal').then(r => setDocs(r.data)).catch(() => {});
  }, []);

  const findDoc = (key) => docs.find(d => d.type === key);

  return (
    <AdminLayout title="Rechtliche Dokumente">
      <div className="adm-card" data-testid="admin-legal-intro">
        <h2 className="adm-card-title">Legal-Editor</h2>
        <p style={{ color: 'var(--adm-text-muted, #94a3b8)', marginTop: '0.5rem', fontSize: '0.92rem', lineHeight: 1.6 }}>
          Bearbeiten Sie AGB, Datenschutz und Impressum direkt im Admin-Bereich. Jede Speicherung erstellt
          automatisch eine neue, signierte Version mit Timestamp, Admin-Benutzer und Diff zur Vorversion —
          revDSG-/DSGVO-Audit-konform. Sie können jederzeit zu einer früheren Version zurückkehren.
        </p>
      </div>

      <div className="adm-grid-3" style={{ marginTop: '2rem' }} data-testid="admin-legal-grid">
        {DOC_META.map(meta => {
          const Icon = meta.icon;
          const doc = findDoc(meta.key);
          return (
            <Link
              key={meta.key}
              href={`/admin/legal/${meta.key}`}
              className="adm-card adm-legal-card"
              data-testid={`admin-legal-card-${meta.key}`}
            >
              <div className="adm-legal-card-header">
                <div className="adm-legal-card-icon" style={{ background: `${meta.color}22`, color: meta.color }}>
                  <Icon size={22} />
                </div>
                <ChevronRight size={18} style={{ color: 'var(--adm-text-muted, #94a3b8)' }} />
              </div>
              <h3 className="adm-legal-card-title">{meta.title}</h3>
              <p className="adm-legal-card-desc">{meta.description}</p>
              <div className="adm-legal-card-meta">
                {doc ? (
                  <>
                    <span className="adm-legal-version-badge">v{doc.version}</span>
                    <span style={{ color: 'var(--adm-text-muted, #94a3b8)', fontSize: '0.78rem' }}>
                      {doc.sections?.length || 0} Abschnitte
                    </span>
                  </>
                ) : (
                  <span style={{ color: 'var(--adm-text-muted, #94a3b8)', fontSize: '0.78rem' }}>Lädt…</span>
                )}
              </div>
            </Link>
          );
        })}
      </div>
    </AdminLayout>
  );
}
