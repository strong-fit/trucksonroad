import { createContext, useContext, useState, useCallback } from 'react';
import { translations } from '@/lib/translations';

const LanguageContext = createContext();
const SUPPORTED_LANGS = ['de', 'en', 'fr', 'it'];

function getInitialLang() {
  const stored = localStorage.getItem('truckonroad_lang');
  if (stored && SUPPORTED_LANGS.includes(stored)) return stored;
  return 'de';
}

export function LanguageProvider({ children }) {
  const [lang, setLangState] = useState(getInitialLang);
  const setLang = useCallback((l) => {
    if (SUPPORTED_LANGS.includes(l)) {
      setLangState(l);
      localStorage.setItem('truckonroad_lang', l);
      document.documentElement.lang = l;
    }
  }, []);
  const t = useCallback((key) => translations[lang]?.[key] || translations['de']?.[key] || key, [lang]);
  return (
    <LanguageContext.Provider value={{ lang, setLang, t, SUPPORTED_LANGS }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
