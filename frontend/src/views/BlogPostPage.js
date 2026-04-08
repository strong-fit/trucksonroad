"use client";
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { ArrowLeft, Calendar, Tag, User } from 'lucide-react';

export default function BlogPostPage({ slug: propSlug, initialPost = null, initialRelatedPosts = [] }) {
  const params = useParams();
  const slug = propSlug || params?.slug;
  const { lang, t } = useLanguage();
  const [post, setPost] = useState(initialPost);
  const [relatedPosts, setRelatedPosts] = useState(initialRelatedPosts);
  const [loading, setLoading] = useState(!initialPost);

  useEffect(() => {
    if (initialPost?.slug === slug) {
      setPost(initialPost);
      setRelatedPosts(initialRelatedPosts);
      setLoading(false);
      return;
    }

    setLoading(true);
    api.get(`/blog/${slug}`)
      .then(r => {
        setPost(r.data);
        // Fetch related posts from same category, fallback to latest
        api.get(`/blog?category=${r.data.category}&limit=4`)
          .then(rel => {
            const filtered = (rel.data.posts || []).filter(p => p.slug !== slug).slice(0, 3);
            if (filtered.length > 0) {
              setRelatedPosts(filtered);
            } else {
              // Fallback: latest posts from any category
              api.get('/blog?limit=4')
                .then(all => setRelatedPosts((all.data.posts || []).filter(p => p.slug !== slug).slice(0, 3)))
                .catch(() => {});
            }
          })
          .catch(() => {});
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [initialPost, initialRelatedPosts, slug]);

  if (loading) return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--sf-gray)' }}>{t('loading')}</div>;
  if (!post) return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
      <h2 style={{ color: 'var(--sf-text)', fontSize: '1.5rem' }}>{t('blog_not_found')}</h2>
      <Link href="/blog" className="sf-btn-primary" data-testid="blog-back-link">{t('blog_back')}</Link>
    </div>
  );

  const title = post[`title_${lang}`] || post.title_de;
  const content = post[`content_${lang}`] || post.content_de;
  const excerpt = post[`excerpt_${lang}`] || post.excerpt_de;
  const renderInlineLinks = (text) => {
    // Parse [text](/path) markdown links
    const parts = text.split(/(\[[^\]]+\]\([^)]+\))/g);
    return parts.map((part, j) => {
      const match = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (match) {
        return <Link key={j} href={match[2]} style={{ color: 'var(--sf-gold)', textDecoration: 'underline', fontWeight: 600 }}>{match[1]}</Link>;
      }
      return part;
    });
  };

  const renderMarkdown = (text) => {
    return text
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('#### ')) return <h4 key={i} style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--sf-text)', marginTop: '1.8rem', marginBottom: '0.5rem' }}>{line.slice(5)}</h4>;
        if (line.startsWith('### ')) return <h3 key={i} style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--sf-text)', marginTop: '2rem', marginBottom: '0.6rem' }}>{line.slice(4)}</h3>;
        if (line.startsWith('## ')) return <h2 key={i} style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--sf-text)', marginTop: '2.5rem', marginBottom: '0.8rem' }}>{line.slice(3)}</h2>;
        if (line.startsWith('- **')) {
          const parts = line.slice(2).split('**');
          return <li key={i} style={{ marginBottom: '0.4rem', lineHeight: 1.7, color: 'var(--sf-gray)' }}><strong style={{ color: 'var(--sf-text)' }}>{parts[1]}</strong>{renderInlineLinks(parts[2] || '')}</li>;
        }
        if (line.startsWith('- ')) return <li key={i} style={{ marginBottom: '0.4rem', lineHeight: 1.7, color: 'var(--sf-gray)' }}>{renderInlineLinks(line.slice(2))}</li>;
        if (line.match(/^\d+\. \*\*/)) {
          const parts = line.split('**');
          return <li key={i} style={{ marginBottom: '0.4rem', lineHeight: 1.7, color: 'var(--sf-gray)', listStyleType: 'decimal' }}><strong style={{ color: 'var(--sf-text)' }}>{parts[1]}</strong>{renderInlineLinks(parts[2] || '')}</li>;
        }
        if (line.match(/^\d+\. /)) return <li key={i} style={{ marginBottom: '0.4rem', lineHeight: 1.7, color: 'var(--sf-gray)', listStyleType: 'decimal' }}>{renderInlineLinks(line.replace(/^\d+\. /, ''))}</li>;
        if (line.startsWith('**') && line.endsWith('**')) return <p key={i} style={{ fontWeight: 700, color: 'var(--sf-text)', marginTop: '1rem' }}>{line.slice(2, -2)}</p>;
        if (line.trim() === '') return <br key={i} />;
        return <p key={i} style={{ marginBottom: '0.6rem', lineHeight: 1.8, color: 'var(--sf-gray)' }}>{renderInlineLinks(line)}</p>;
      });
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--sf-bg)' }}>
      
      {/* Hero image */}
      <div style={{ position: 'relative', height: '400px', overflow: 'hidden' }}>
        <img src={post.image} alt={title} style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'brightness(0.5)' }} />
        <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
          <Link href="/blog" style={{ color: 'var(--sf-gold)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem', marginBottom: '1rem' }} data-testid="blog-detail-back">
            <ArrowLeft size={16} /> {t('blog_back')}
          </Link>
        </div>
      </div>

      {/* Content */}
      <article style={{ maxWidth: '780px', margin: '-3rem auto 0', padding: '2.5rem', position: 'relative', zIndex: 2, background: 'rgba(20,20,18,0.95)', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.08)' }} data-testid="blog-post-content">
        {/* Meta */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--sf-gold)', background: 'rgba(var(--sf-gold-rgb, 100,200,180), 0.1)', padding: '3px 10px', borderRadius: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            <Tag size={10} style={{ marginRight: '3px', display: 'inline' }} /> {post.category}
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--sf-gray)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Calendar size={13} /> {new Date(post.created_at).toLocaleDateString(lang === 'de' ? 'de-CH' : 'en-GB')}
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--sf-gray)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <User size={13} /> {post.author}
          </span>
        </div>

        {/* Title */}
        <h1 style={{ fontSize: 'clamp(1.5rem, 4vw, 2.2rem)', fontWeight: 800, color: 'var(--sf-text)', lineHeight: 1.25, marginBottom: '1rem' }} data-testid="blog-post-title">
          {title}
        </h1>
        <p style={{ fontSize: '1.05rem', color: 'var(--sf-gray)', lineHeight: 1.7, marginBottom: '2rem', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '1.5rem' }}>
          {excerpt}
        </p>

        {/* Body */}
        <div style={{ fontSize: '0.95rem' }} data-testid="blog-post-body">
          {renderMarkdown(content)}
        </div>

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <div style={{ marginTop: '2.5rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {post.tags.map((tag, i) => (
                <span key={i} style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: '10px', background: 'rgba(255,255,255,0.06)', color: 'var(--sf-gray)' }}>
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <div style={{ marginTop: '2.5rem', padding: '1.5rem', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', textAlign: 'center' }}>
          <p style={{ color: 'var(--sf-text)', fontWeight: 600, marginBottom: '0.6rem' }}>{t('blog_cta_text')}</p>
          <Link href="/anfrage" className="sf-btn-primary" style={{ display: 'inline-flex', textDecoration: 'none' }} data-testid="blog-post-cta">
            {t('nav_cta')}
          </Link>
        </div>
      </article>

      {/* Related Posts */}
      {relatedPosts.length > 0 && (
        <section style={{ maxWidth: '780px', margin: '2rem auto', padding: '0 1rem' }} data-testid="related-posts">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--sf-text)', marginBottom: '1rem' }}>{t('blog_related')}</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '1rem' }}>
            {relatedPosts.map(rp => (
              <Link key={rp.id} href={`/blog/${rp.slug}`} style={{ textDecoration: 'none', color: 'inherit' }} data-testid={`related-${rp.slug}`}>
                <div className="sf-blog-card" style={{ borderRadius: '10px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.03)' }}>
                  {rp.image && <img src={rp.image} alt={rp[`title_${lang}`] || rp.title_de} style={{ width: '100%', height: '120px', objectFit: 'cover' }} loading="lazy" />}
                  <div style={{ padding: '0.8rem' }}>
                    <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--sf-text)', lineHeight: 1.3 }}>
                      {(rp[`title_${lang}`] || rp.title_de || '').slice(0, 60)}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      <div style={{ height: '4rem' }} />
    </div>
  );
}
