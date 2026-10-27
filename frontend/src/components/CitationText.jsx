import React from 'react';

/**
 * Parses text containing inline citations like [1], [2], [1][2]
 * and converts them into interactive, clickable badges.
 */
export function CitationText({ text, onCitationClick }) {
  if (!text) return null;

  // Split by [number] pattern while preserving matches
  const parts = text.split(/(\[\d+\])/g);

  return (
    <span>
      {parts.map((part, index) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (match) {
          const sourceNum = parseInt(match[1], 10);
          return (
            <button
              key={index}
              type="button"
              className="citation-badge"
              onClick={() => onCitationClick && onCitationClick(sourceNum)}
              title={`View source [${sourceNum}] in bibliography`}
              aria-label={`Citation source ${sourceNum}`}
            >
              [{sourceNum}]
            </button>
          );
        }
        return <span key={index}>{part}</span>;
      })}
    </span>
  );
}
