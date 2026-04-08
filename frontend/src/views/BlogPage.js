"use client";
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { ArrowRight, Calendar, Tag, ChevronRight } from 'lucide-react';

export default function BlogPage({ initialPosts = [], initialCategories = {} }) {
  const { lang, t } = useLanguage();
  const [posts, setPosts] = useState(initialPosts);
  const [categories, setCategories] = useState(initialCategories);
  const [activeCategory, setActiveCategory] = useState(null);
  const [loading, setLoading] = useState(!initialPosts.length);

  useEffect(() => {
    if (activeCategory === null && initialPosts.length && Object.keys(initialCategories).length) {
      setPosts(initialPosts);
      setCategories(initialCategories);
      setLoading(false);
      return;
    }

    setLoading(true);
    const params = activeCategory ? `?category=${activeCategory}` : '';
    api.get(`/blog${params}`)
      .then(r => { setPosts(r.data.posts); setCategories(r.data.categories); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [activeCategory, initialCategories, initialPosts]);

  const getTitle = (p) => p[`title_${lang}`] || p.title_de;
  const getExcerpt = (p) => p[`excerpt_${lang}`] || p.excerpt_de;
  const getCategoryLabel = (key) => (categories[key] || {})[lang] || (categories[key] || {}).de || key;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--sf-bg)' }}>
      
      {/* Hero */}
      <section style={{ padding: '8rem 1.5rem 3rem', textAlign: 'center' }}>
        <div className="sf-tag" data-testid="blog-tag">{t('blog_tag')}</div>
        <h1 style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)', fontWeight: 800, color: 'var(--sf-text)', letterSpacing: '-0.03em', marginBottom: '0.8rem' }}>
          {t('blog_title')}
        </h1>
        <p style={{ color: 'var(--sf-gray)', maxWidth: '600px', margin: '0 auto', fontSize: '1rem', lineHeight: 1.7 }}>
          {t('blog_subtitle')}
        </p>
      </section>

      {/* Category Filter */}
      <section style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 1.5rem 2rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', justifyContent: 'center' }} data-testid="blog-category-filter">
          <button
            onClick={() => setActiveCategory(null)}
            style={{
              padding: '0.45rem 1.1rem', borderRadius: '20px', border: '1px solid',
              borderColor: !activeCategory ? 'var(--sf-gold)' : 'rgba(255,255,255,0.15)',
              background: !activeCategory ? 'var(--sf-gold)' : 'transparent',
              color: !activeCategory ? '#000' : 'var(--sf-gray)',
              fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s'
            }}
            data-testid="blog-filter-all"
          >
            {t('blog_all')}
          </button>
          {Object.entries(categories).map(([key]) => (
            <button
              key={key}
              onClick={() => setActiveCategory(key)}
              style={{
                padding: '0.45rem 1.1rem', borderRadius: '20px', border: '1px solid',
                borderColor: activeCategory === key ? 'var(--sf-gold)' : 'rgba(255,255,255,0.15)',
                background: activeCategory === key ? 'var(--sf-gold)' : 'transparent',
                color: activeCategory === key ? '#000' : 'var(--sf-gray)',
                fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s'
              }}
              data-testid={`blog-filter-${key}`}
            >
              {getCategoryLabel(key)}
            </button>
          ))}
        </div>
      </section>

      {/* Posts Grid */}
      <section style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 1.5rem 5rem' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--sf-gray)', padding: '3rem' }}>{t('loading')}</div>
        ) : posts.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--sf-gray)', padding: '3rem' }} data-testid="blog-empty">
            {t('blog_no_posts')}
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '1.5rem'
          }} data-testid="blog-grid">
            {posts.map(post => (
              <Link
                key={post.id}
                href={`/blog/${post.slug}`}
                style={{ textDecoration: 'none', color: 'inherit' }}
                data-testid={`blog-card-${post.slug}`}
              >
                <article style={{
                  borderRadius: '12px', overflow: 'hidden',
                  border: '1px solid rgba(255,255,255,0.08)',
                  background: 'rgba(255,255,255,0.03)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                  className="sf-blog-card"
                >
                  <div style={{ height: '200px', overflow: 'hidden' }}>
                    <img
                      src={post.image}
                      alt={getTitle(post)}
                      style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.4s' }}
                      loading="lazy"
                    />
                  </div>
                  <div style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.6rem' }}>
                      <span style={{
                        fontSize: '0.7rem', fontWeight: 600, color: 'var(--sf-gold)',
                        background: 'rgba(var(--sf-gold-rgb, 100,200,180), 0.1)',
                        padding: '2px 8px', borderRadius: '10px', textTransform: 'uppercase', letterSpacing: '0.05em'
                      }}>
                        <Tag size={10} style={{ marginRight: '3px', display: 'inline' }} />
                        {getCategoryLabel(post.category)}
                      </span>
                      <span style={{ fontSize: '0.72rem', color: 'var(--sf-gray)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Calendar size={11} />
                        {new Date(post.created_at).toLocaleDateString(lang === 'de' ? 'de-CH' : lang === 'fr' ? 'fr-CH' : lang === 'it' ? 'it-CH' : 'en-GB')}
                      </span>
                    </div>
                    <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--sf-text)', marginBottom: '0.5rem', lineHeight: 1.35 }}>
                      {getTitle(post)}
                    </h2>
                    <p style={{ fontSize: '0.84rem', color: 'var(--sf-gray)', lineHeight: 1.6, marginBottom: '0.8rem' }}>
                      {getExcerpt(post)}
                    </p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--sf-gold)', fontSize: '0.82rem', fontWeight: 600 }}>
                      {t('blog_read_more')} <ChevronRight size={14} />
                    </div>
                  </div>
                </article>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
