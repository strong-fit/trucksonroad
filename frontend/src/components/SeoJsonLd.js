"use client";
import { useEffect } from 'react';
import api from '@/lib/api';

export default function SeoJsonLd() {
  useEffect(() => {
    let script = document.getElementById('dynamic-jsonld');
    api.get('/seo/structured-data').then(r => {
      if (!script) {
        script = document.createElement('script');
        script.id = 'dynamic-jsonld';
        script.type = 'application/ld+json';
        document.head.appendChild(script);
      }
      script.textContent = JSON.stringify(r.data);
    }).catch(() => {});
    // Google verification
    api.get('/seo/google-verification').then(r => {
      if (r.data.code) {
        let meta = document.getElementById('google-site-verification');
        if (!meta) {
          meta = document.createElement('meta');
          meta.id = 'google-site-verification';
          meta.name = 'google-site-verification';
          document.head.appendChild(meta);
        }
        meta.content = r.data.code;
      }
    }).catch(() => {});
    return () => { if (script) script.remove(); };
  }, []);
  return null;
}
