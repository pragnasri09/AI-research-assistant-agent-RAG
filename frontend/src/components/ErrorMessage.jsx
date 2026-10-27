import React from 'react';
import { AlertCircle, RefreshCw, X } from 'lucide-react';

export function ErrorMessage({ error, onRetry, onDismiss }) {
  if (!error) return null;

  const message = typeof error === 'string' ? error : error.message || 'An unexpected error occurred.';

  return (
    <div className="alert-banner" role="alert">
      <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div style={{ flex: 1 }}>
        <div className="alert-title">Request Notice</div>
        <div className="alert-desc">{message}</div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        {onRetry && (
          <button
            type="button"
            className="btn-secondary"
            onClick={onRetry}
            style={{ padding: '4px 10px', fontSize: '0.8rem' }}
          >
            <RefreshCw size={13} />
            <span>Retry</span>
          </button>
        )}
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            style={{ color: 'inherit', padding: '4px', display: 'flex', alignItems: 'center' }}
            aria-label="Dismiss message"
          >
            <X size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
