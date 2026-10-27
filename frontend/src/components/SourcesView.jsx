import React from 'react';
import { ExternalLink, Globe, Calendar, Award } from 'lucide-react';

export function SourcesView({ sources = [], highlightedSourceId }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-title">No sources available</div>
        <div className="empty-state-desc">
          Extracted sources will appear here once the research agent completes its search and indexing stages.
        </div>
      </div>
    );
  }

  return (
    <div className="sources-grid">
      {sources.map((source) => {
        const isHighlighted = highlightedSourceId === source.source_id;
        return (
          <article
            key={source.source_id}
            id={`source-card-${source.source_id}`}
            className="source-card"
            style={{
              borderColor: isHighlighted ? 'var(--accent)' : 'var(--border-default)',
              backgroundColor: isHighlighted ? 'var(--accent-bg)' : 'var(--bg-card)',
              transition: 'all 0.2s ease',
            }}
          >
            <div className="source-card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="bib-number">[{source.source_id}]</span>
                <span className="badge-neutral" style={{ textTransform: 'lowercase' }}>
                  <Globe size={11} />
                  <span>{source.domain || 'web'}</span>
                </span>
                {source.publication_date && source.publication_date !== 'Unknown' && (
                  <span className="badge-neutral">
                    <Calendar size={11} />
                    <span>{source.publication_date}</span>
                  </span>
                )}
                {source.quality_score > 0 && (
                  <span className="badge-neutral">
                    <Award size={11} />
                    <span>Quality {Math.round(source.quality_score * 100)}%</span>
                  </span>
                )}
              </div>
            </div>

            <h3 className="source-card-title">
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                title={`Open ${source.url}`}
              >
                <span>{source.title}</span>
                <ExternalLink size={14} style={{ flexShrink: 0 }} />
              </a>
            </h3>

            {source.summary && (
              <p className="source-summary-text">{source.summary}</p>
            )}

            {source.key_findings && source.key_findings.length > 0 && (
              <div className="source-takeaways">
                <div className="source-takeaways-title">Key Findings Extracted</div>
                <ul className="takeaways-list">
                  {source.key_findings.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </article>
        );
      })}
    </div>
  );
}
