import React, { useState, useEffect } from 'react';
import { Loader2, Check, Clock } from 'lucide-react';

const PIPELINE_STAGES = [
  { label: 'Analyze Research Intent', minPercent: 10 },
  { label: 'Generate Targeted Search Queries', minPercent: 25 },
  { label: 'Autonomous Web Search', minPercent: 40 },
  { label: 'Extract & Filter High-Quality Content', minPercent: 55 },
  { label: 'Vector Indexing & RAG Chunking', minPercent: 70 },
  { label: 'Synthesize Per-Source Findings', minPercent: 80 },
  { label: 'Draft Report & Validate Citations', minPercent: 90 },
];

export function ProgressTracker({ sessionStatus, onCancel }) {
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const percent = sessionStatus?.progress_percent ?? 5;
  const currentStep = sessionStatus?.progress_step || 'Starting research pipeline...';
  const question = sessionStatus?.question || '';
  const sourcesCount = sessionStatus?.sources_count ?? 0;

  return (
    <div className="progress-card">
      <div className="progress-header">
        <div>
          <div className="progress-query">"{question}"</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Autonomous agent pipeline active
          </div>
        </div>
        <div className="progress-status-badge">
          <Clock size={13} />
          <span>{secondsElapsed}s elapsed</span>
        </div>
      </div>

      <div className="progress-bar-track">
        <div
          className="progress-bar-fill"
          style={{ width: `${Math.min(Math.max(percent, 4), 100)}%` }}
        />
      </div>

      <div className="progress-meta">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Loader2 size={15} style={{ animation: 'spin 1.5s linear infinite' }} />
          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{currentStep}</span>
        </div>
        <div>
          <span style={{ fontWeight: 600, color: 'var(--accent-text)' }}>{percent}%</span>
          {sourcesCount > 0 && (
            <span style={{ marginLeft: '12px', color: 'var(--text-muted)' }}>
              ({sourcesCount} sources analyzed)
            </span>
          )}
        </div>
      </div>

      <div className="pipeline-steps">
        {PIPELINE_STAGES.map((stage, idx) => {
          const isDone = percent > stage.minPercent;
          const isActive = percent <= stage.minPercent && (idx === 0 || percent > PIPELINE_STAGES[idx - 1].minPercent);

          return (
            <div
              key={idx}
              className={`step-item ${isDone ? 'completed' : ''} ${isActive ? 'active' : ''}`}
            >
              <div className="step-marker">
                {isDone ? <Check size={12} /> : idx + 1}
              </div>
              <span>{stage.label}</span>
            </div>
          );
        })}
      </div>

      {onCancel && (
        <div style={{ marginTop: '20px', textAlign: 'right' }}>
          <button
            type="button"
            className="btn-secondary"
            onClick={onCancel}
            style={{ fontSize: '0.82rem', padding: '6px 12px' }}
          >
            Cancel / Start Over
          </button>
        </div>
      )}
    </div>
  );
}
