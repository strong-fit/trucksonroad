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
    return () => { if (script) script.remove(); };
  }, []);
  return null;
}
