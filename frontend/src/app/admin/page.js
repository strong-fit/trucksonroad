"use client";
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AdminPage() {
  const router = useRouter();
  
  useEffect(() => {
    router.replace('/admin/dashboard');
  }, [router]);
  
  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--sf-bg)' }}>
      <div className="sf-spinner" />
    </div>
  );
}
