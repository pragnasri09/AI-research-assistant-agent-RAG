import React, { useState } from 'react';
import { 
  Download, 
  Copy, 
  Check, 
  ArrowLeft, 
  BookOpen, 
  Layers, 
  Globe, 
  ExternalLink,
  ShieldCheck,
  Calendar,
  FileText
} from 'lucide-react';
import { CitationText } from './CitationText';
import { SourcesView } from './SourcesView';

export function ReportView({ report, sources = [], onBackToSearch }) {
  const [activeSubTab, setActiveSubTab] = useState('report'); // 'report' | 'sources'
  const [copied, setCopied] = useState(false);
  const [highlightedSid, setHighlightedSid] = useState(null);

  if (!report) {
    return (
      <div className="empty-state">
        <div className="empty-state-title">No report found</div>
        <div className="empty-state-desc">This session does not have a generated report yet.</div>
        <button type="button" className="btn-secondary" onClick={onBackToSearch}>
          Back to Research
        </button>
      </div>
    );
  }

  // Handle citation click: scrolls smoothly to bibliography item and highlights it
  const handleCitationClick = (sourceId) => {
    setHighlightedSid(sourceId);
    if (activeSubTab !== 'report') {
      setActiveSubTab('report');
    }

    setTimeout(() => {
      const el = document.getElementById(`bib-source-${sourceId}`) || document.getElementById(`source-card-${sourceId}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 50);

    setTimeout(() => {
      setHighlightedSid(null);
    }, 3500);
  };

  // Download Markdown file
  const handleDownloadMarkdown = () => {
    const markdownContent = report.full_markdown || `# ${report.question}\n\n## Executive Summary\n${report.executive_summary}\n`;
    const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const safeName = (report.question || 'research-report')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .slice(0, 40);
    link.href = url;
    link.setAttribute('download', `${safeName}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Copy Markdown to clipboard
  const handleCopyMarkdown = async () => {
    const markdownContent = report.full_markdown || `# ${report.question}\n\n## Executive Summary\n${report.executive_summary}\n`;
    try {
      await navigator.clipboard.writeText(markdownContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy markdown:', err);
    }
  };

  const bibliography = report.bibliography || [];
  const detailedAnalysis = report.detailed_analysis || [];

  return (
    <article className="report-page">
      {/* Top action bar */}
      <div className="report-top-bar">
        <button type="button" className="btn-secondary" onClick={onBackToSearch}>
          <ArrowLeft size={16} />
          <span>New Research</span>
        </button>

        <div className="report-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={handleCopyMarkdown}
            title="Copy full report as Markdown"
          >
            {copied ? <Check size={15} style={{ color: 'var(--accent)' }} /> : <Copy size={15} />}
            <span>{copied ? 'Copied' : 'Copy MD'}</span>
          </button>

          <button
            type="button"
            className="btn-primary"
            onClick={handleDownloadMarkdown}
            title="Download full report as Markdown file"
          >
            <Download size={15} />
            <span>Download Report (.md)</span>
          </button>
        </div>
      </div>

      {/* Header card with metadata */}
      <div className="report-header-card">
        <h1 className="report-title">{report.question}</h1>
        <div className="report-meta-row">
          <span className="badge-neutral">
            <BookOpen size={13} />
            <span>Autonomous Synthesis</span>
          </span>
          {report.is_validated && (
            <span className="badge-validated">
              <ShieldCheck size={13} />
              <span>Verified Citations</span>
            </span>
          )}
          <span className="badge-neutral">
            <Globe size={13} />
            <span>{bibliography.length || sources.length} Sources Cited</span>
          </span>
        </div>
      </div>

      {/* Sub-tabs for switching between Synthesized Report and Extracted Sources */}
      <div className="tabs-container">
        <button
          type="button"
          className={`tab-btn ${activeSubTab === 'report' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('report')}
        >
          <FileText size={16} />
          <span>Synthesized Report</span>
        </button>
        <button
          type="button"
          className={`tab-btn ${activeSubTab === 'sources' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('sources')}
        >
          <Layers size={16} />
          <span>All Extracted Sources ({sources.length || bibliography.length})</span>
        </button>
      </div>

      {activeSubTab === 'sources' ? (
        <SourcesView sources={sources} highlightedSourceId={highlightedSid} />
      ) : (
        <div className="report-body">
          {/* Executive Summary */}
          {report.executive_summary && (
            <section className="report-section" id="section-executive-summary">
              <h2 className="section-heading">Executive Summary</h2>
              <div className="section-text">
                <CitationText
                  text={report.executive_summary}
                  onCitationClick={handleCitationClick}
                />
              </div>
            </section>
          )}

          {/* Key Findings */}
          {report.key_findings && report.key_findings.length > 0 && (
            <section className="report-section" id="section-key-findings">
              <h2 className="section-heading">Key Findings</h2>
              <ul className="key-findings-list">
                {report.key_findings.map((finding, idx) => (
                  <li key={idx} className="key-finding-item">
                    <span className="finding-bullet">{idx + 1}</span>
                    <div style={{ flex: 1 }}>
                      <CitationText
                        text={finding}
                        onCitationClick={handleCitationClick}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Introduction */}
          {report.introduction && (
            <section className="report-section" id="section-introduction">
              <h2 className="section-heading">Introduction & Context</h2>
              <div className="section-text">
                <CitationText
                  text={report.introduction}
                  onCitationClick={handleCitationClick}
                />
              </div>
            </section>
          )}

          {/* Detailed Analysis Sections */}
          {detailedAnalysis.length > 0 && (
            <section className="report-section" id="section-detailed-analysis">
              <h2 className="section-heading">Detailed Analysis</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {detailedAnalysis.map((sec, idx) => (
                  <div key={idx} style={{ borderBottom: idx < detailedAnalysis.length - 1 ? '1px solid var(--border-subtle)' : 'none', paddingBottom: '16px' }}>
                    <h3 style={{ fontSize: '1.08rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                      {sec.title}
                    </h3>
                    <div className="section-text">
                      <CitationText
                        text={sec.content}
                        onCitationClick={handleCitationClick}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Evidence and Insights */}
          {report.evidence_and_insights && (
            <section className="report-section" id="section-evidence">
              <h2 className="section-heading">Evidence & Synthesis</h2>
              <div className="section-text">
                <CitationText
                  text={report.evidence_and_insights}
                  onCitationClick={handleCitationClick}
                />
              </div>
            </section>
          )}

          {/* Contrasting Perspectives */}
          {report.contrasting_perspectives && report.contrasting_perspectives.trim() && (
            <section className="report-section" id="section-perspectives">
              <h2 className="section-heading">Contrasting Perspectives & Nuance</h2>
              <div className="section-text">
                <CitationText
                  text={report.contrasting_perspectives}
                  onCitationClick={handleCitationClick}
                />
              </div>
            </section>
          )}

          {/* Limitations */}
          {report.limitations && (
            <section className="report-section" id="section-limitations">
              <h2 className="section-heading">Scope & Methodological Limitations</h2>
              <div className="section-text">
                <CitationText
                  text={report.limitations}
                  onCitationClick={handleCitationClick}
                />
              </div>
            </section>
          )}

          {/* Conclusion */}
          {report.conclusion && (
            <section className="report-section" id="section-conclusion">
              <h2 className="section-heading">Conclusion</h2>
              <div className="section-text">
                <CitationText
                  text={report.conclusion}
                  onCitationClick={handleCitationClick}
                />
              </div>
            </section>
          )}

          {/* Bibliography */}
          {bibliography.length > 0 && (
            <section className="report-section" id="section-bibliography">
              <h2 className="section-heading">Bibliography & References</h2>
              <div className="bibliography-list">
                {bibliography.map((item) => {
                  const isHighlighted = highlightedSid === item.source_id;
                  return (
                    <div
                      key={item.source_id}
                      id={`bib-source-${item.source_id}`}
                      className={`bib-item ${isHighlighted ? 'highlighted' : ''}`}
                    >
                      <span className="bib-number">[{item.source_id}]</span>
                      <div className="bib-content">
                        <div className="bib-title">{item.title}</div>
                        <div className="bib-meta">
                          <span className="badge-neutral" style={{ textTransform: 'lowercase' }}>
                            <Globe size={11} />
                            <span>{item.domain}</span>
                          </span>
                          {item.publication_date && item.publication_date !== 'Unknown' && (
                            <span className="badge-neutral">
                              <Calendar size={11} />
                              <span>{item.publication_date}</span>
                            </span>
                          )}
                          {item.url && item.url !== '#' && (
                            <a
                              href={item.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="bib-link"
                            >
                              <span>Visit Source</span>
                              <ExternalLink size={12} />
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          )}
        </div>
      )}
    </article>
  );
}
