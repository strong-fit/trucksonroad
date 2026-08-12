"use client";

/**
 * LegalRenderer - renders a legal document with title, subtitle, and sections.
 * Sections support light markdown:
 *   - Lines starting with "- " become bullet items
 *   - **bold**
 *   - [text](url) links
 *   - Blank lines create paragraph breaks
 */

function renderInline(text) {
  if (!text) return null;
  const parts = [];
  const linkRe = /\[([^\]]+)\]\(([^)]+)\)/g;
  let lastIdx = 0;
  let match;
  let key = 0;
  while ((match = linkRe.exec(text)) !== null) {
    if (match.index > lastIdx) {
      parts.push(...renderBold(text.slice(lastIdx, match.index), key++));
    }
    parts.push(
      <a
        key={`l-${key++}`}
        href={match[2]}
        className="sf-legal-link"
        target={match[2].startsWith('http') ? '_blank' : undefined}
        rel={match[2].startsWith('http') ? 'noopener noreferrer' : undefined}
      >
        {match[1]}
      </a>
    );
    lastIdx = match.index + match[0].length;
  }
  if (lastIdx < text.length) {
    parts.push(...renderBold(text.slice(lastIdx), key++));
  }
  return parts;
}

function renderBold(text, baseKey) {
  const out = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  parts.forEach((p, i) => {
    if (p.startsWith('**') && p.endsWith('**')) {
      out.push(<strong key={`b-${baseKey}-${i}`}>{p.slice(2, -2)}</strong>);
    } else if (p) {
      out.push(<span key={`t-${baseKey}-${i}`}>{p}</span>);
    }
  });
  return out;
}

function renderContent(content) {
  if (!content) return null;
  const lines = content.split('\n');
  const blocks = [];
  let currentList = null;
  let currentPara = [];

  const flushPara = () => {
    if (currentPara.length) {
      blocks.push(
        <p key={`p-${blocks.length}`}>
          {renderInline(currentPara.join(' '))}
        </p>
      );
      currentPara = [];
    }
  };
  const flushList = () => {
    if (currentList) {
      blocks.push(
        <ul key={`u-${blocks.length}`}>
          {currentList.map((item, i) => (
            <li key={i}>{renderInline(item)}</li>
          ))}
        </ul>
      );
      currentList = null;
    }
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushPara();
      flushList();
      return;
    }
    if (trimmed.startsWith('- ')) {
      flushPara();
      if (!currentList) currentList = [];
      currentList.push(trimmed.slice(2));
    } else {
      flushList();
      currentPara.push(trimmed);
    }
  });
  flushPara();
  flushList();
  return blocks;
}

export default function LegalRenderer({ doc, badgeLabel = 'Rechtliches', testIdPrefix = 'legal' }) {
  if (!doc) {
    return (
      <div className="sf-page sf-legal" data-testid={`${testIdPrefix}-empty`}>
        <div className="sf-page-hero">
          <h1 className="sf-section-title">Dokument nicht verfügbar</h1>
        </div>
      </div>
    );
  }

  const updatedDate = doc.updated_at
    ? new Date(doc.updated_at).toLocaleDateString('de-CH', { day: '2-digit', month: 'long', year: 'numeric' })
    : null;

  return (
    <div className="sf-page sf-legal" data-testid={`${testIdPrefix}-page`}>
      <div className="sf-page-hero">
        <div className="sf-section-tag" data-testid={`${testIdPrefix}-tag`}>{badgeLabel}</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>
          {doc.title}
        </h1>
        {doc.subtitle && (
          <p className="sf-page-hero-desc">{doc.subtitle}</p>
        )}
      </div>

      <section className="sf-section" style={{ paddingTop: '2rem' }}>
        <div className="sf-legal-content" data-testid={`${testIdPrefix}-content`}>
          {(doc.sections || []).map((s, idx) => (
            <div key={idx} data-testid={`${testIdPrefix}-section-${idx}`}>
              <h2>{s.heading}</h2>
              {renderContent(s.content)}
            </div>
          ))}

          <div className="sf-legal-meta" data-testid={`${testIdPrefix}-meta`}>
            <p>
              {updatedDate && (
                <>Letzte Aktualisierung: <strong>{updatedDate}</strong> · Version {doc.version}<br /></>
              )}
              <strong>TRUCKSonROAD</strong> · Bahnhofstrasse 75 · 8620 Wetzikon · Schweiz<br />
              <a href="mailto:info@trucksonroad.ch">info@trucksonroad.ch</a> · +41 79 696 98 99
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
