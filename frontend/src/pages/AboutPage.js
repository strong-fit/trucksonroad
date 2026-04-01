import { useLanguage } from '@/contexts/LanguageContext';
import { Users, Award, Heart, MapPin } from 'lucide-react';

export default function AboutPage() {
  const { t } = useLanguage();

  return (
    <div className="sf-page" data-testid="about-page">
      <section className="sf-section">
        <div className="sf-section-inner" style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div className="sf-tag" data-testid="about-tag">{t('about_tag')}</div>
          <h1 className="sf-section-title">
            {t('about_title_1')} <span className="gold">{t('about_title_2')}</span>
          </h1>
          <p className="sf-section-desc" style={{ maxWidth: '700px' }}>{t('about_intro')}</p>
        </div>
      </section>

      <section className="sf-section">
        <div className="sf-section-inner" style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div className="sf-about-story" data-testid="about-story">
            <h2 className="sf-subsection-title">{t('about_story_title')}</h2>
            <p className="sf-text-body">{t('about_story_1')}</p>
            <p className="sf-text-body">{t('about_story_2')}</p>
          </div>

          <div className="sf-about-values" data-testid="about-values">
            <h2 className="sf-subsection-title">{t('about_values_title')}</h2>
            <div className="sf-about-values-grid">
              <div className="sf-about-value-card">
                <div className="sf-about-value-icon"><Award size={22} /></div>
                <h3>{t('about_val_1_title')}</h3>
                <p>{t('about_val_1_text')}</p>
              </div>
              <div className="sf-about-value-card">
                <div className="sf-about-value-icon"><Heart size={22} /></div>
                <h3>{t('about_val_2_title')}</h3>
                <p>{t('about_val_2_text')}</p>
              </div>
              <div className="sf-about-value-card">
                <div className="sf-about-value-icon"><Users size={22} /></div>
                <h3>{t('about_val_3_title')}</h3>
                <p>{t('about_val_3_text')}</p>
              </div>
              <div className="sf-about-value-card">
                <div className="sf-about-value-icon"><MapPin size={22} /></div>
                <h3>{t('about_val_4_title')}</h3>
                <p>{t('about_val_4_text')}</p>
              </div>
            </div>
          </div>

          <div className="sf-about-numbers" data-testid="about-numbers">
            <div className="sf-about-number">
              <span className="sf-about-number-value">6</span>
              <span className="sf-about-number-label">{t('about_num_1')}</span>
            </div>
            <div className="sf-about-number">
              <span className="sf-about-number-value">500+</span>
              <span className="sf-about-number-label">{t('about_num_2')}</span>
            </div>
            <div className="sf-about-number">
              <span className="sf-about-number-value">CH</span>
              <span className="sf-about-number-label">{t('about_num_3')}</span>
            </div>
            <div className="sf-about-number">
              <span className="sf-about-number-value">24h</span>
              <span className="sf-about-number-label">{t('about_num_4')}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
