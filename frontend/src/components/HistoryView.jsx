import React from 'react';
import { Clock, Globe, ArrowRight, Trash2, History, RefreshCw } from 'lucide-react';

export function HistoryView({ 
  history = [], 
  isLoading, 
  onRefresh, 
  onOpenReport, 
  onDeleteSession 
}) {
  const formatDate = (isoString) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <section className="history-section">
      <div className="history-header">
        <div>
          <h2 className="history-title">Research History</h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Past research investigations, retrieved sources, and generated reports.
          </p>
        </div>

        <button
          type="button"
          className="btn-secondary"
          onClick={onRefresh}
          disabled={isLoading}
          title="Refresh history list"
        >
          <RefreshCw size={14} style={{ animation: isLoading ? 'spin 1s linear infinite' : 'none' }} />
          <span>Refresh</span>
        </button>
      </div>

      {history.length === 0 ? (
        <div className="empty-state">
          <History size={36} className="empty-state-icon" />
          <h3 className="empty-state-title">No research history found</h3>
          <p className="empty-state-desc">
            Submit your first research topic above. Completed investigations and citations will be preserved here.
          </p>
        </div>
      ) : (
        <div className="history-list">
          {history.map((item) => {
            const isCompleted = item.status === 'completed';
            const isFailed = item.status === 'failed';

            return (
              <div key={item.session_id} className="history-item-card">
                <div className="history-card-top">
                  <div style={{ flex: 1 }}>
                    <h3
                      className="history-question"
                      onClick={() => onOpenReport(item.session_id)}
                      title="Click to view full research report"
                    >
                      {item.question}
                    </h3>
                  </div>

                  <span
                    className={
                      isCompleted
                        ? 'badge-neutral'
                        : isFailed
                        ? 'alert-banner'
                        : 'badge-validated'
                    }
                    style={{
                      margin: 0,
                      padding: '2px 8px',
                      fontSize: '0.78rem',
                      display: 'inline-flex',
                      alignItems: 'center',
                    }}
                  >
                    {item.status}
                  </span>
                </div>

                {item.executive_summary_preview ? (
                  <p className="history-preview">{item.executive_summary_preview}</p>
                ) : (
                  <p className="history-preview" style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    {isFailed ? 'Session halted due to an execution error.' : 'No preview summary generated.'}
                  </p>
                )}

                <div className="history-meta-row">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <Clock size={13} />
                      <span>{formatDate(item.created_at)}</span>
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <Globe size={13} />
                      <span>{item.sources_count} sources analyzed</span>
                    </span>
                  </div>

                  <div className="history-actions">
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => onOpenReport(item.session_id)}
                      style={{ padding: '6px 12px', fontSize: '0.82rem' }}
                    >
                      <span>Open Report</span>
                      <ArrowRight size={13} />
                    </button>

                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => {
                        if (window.confirm(`Delete research record for "${item.question}"?`)) {
                          onDeleteSession(item.session_id);
                        }
                      }}
                      style={{ padding: '6px 10px', color: 'var(--danger-text)' }}
                      title="Delete this session"
                      aria-label="Delete session"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
