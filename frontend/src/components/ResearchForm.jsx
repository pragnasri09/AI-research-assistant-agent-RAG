import React, { useState } from 'react';
import { ArrowRight, HelpCircle } from 'lucide-react';

const EXAMPLE_TOPICS = [
  "What are the architectural trade-offs in modern RAG systems?",
  "How does speculative decoding improve LLM inference latency?",
  "Security implications and sandboxing for autonomous AI agents",
  "Comparing vector databases vs graph databases for enterprise knowledge retrieval"
];

export function ResearchForm({ onSubmit, isLoading }) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (trimmed.length < 5 || isLoading) return;
    onSubmit(trimmed);
  };

  const handleSelectExample = (example) => {
    setQuestion(example);
  };

  return (
    <section className="hero-section">
      <h1 className="hero-title">AI Research Assistant</h1>
      <p className="hero-subtitle">
        Research any topic using autonomous web search, RAG, and citations.
      </p>

      <div className="search-card">
        <form onSubmit={handleSubmit} className="search-input-wrapper">
          <textarea
            className="search-textarea"
            placeholder="Enter your research question or topic (e.g., What are the architectural trade-offs in modern RAG systems?)..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={isLoading}
            rows={3}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                handleSubmit(e);
              }
            }}
          />

          <div className="search-actions">
            <div className="search-hints">
              {question.trim().length < 5 && question.length > 0 ? (
                <span>Minimum 5 characters required</span>
              ) : (
                <span>Press Ctrl+Enter or click Start Research</span>
              )}
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={question.trim().length < 5 || isLoading}
            >
              <span>{isLoading ? 'Starting...' : 'Start Research'}</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </form>
      </div>

      <div className="examples-section">
        <div className="examples-title">Example Research Questions</div>
        <div className="examples-grid">
          {EXAMPLE_TOPICS.map((topic, idx) => (
            <button
              key={idx}
              type="button"
              className="example-card"
              onClick={() => handleSelectExample(topic)}
              disabled={isLoading}
            >
              <HelpCircle size={15} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--accent)' }} />
              <span>{topic}</span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
