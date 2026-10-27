import React from 'react';
import { BookOpen, History, Search } from 'lucide-react';

export function Navbar({ activeTab, onSelectTab, historyCount = 0, health }) {
  const isHealthy = health?.status === 'healthy';
  const isTavily = health?.tavily_configured;

  return (
    <header className="navbar">
      <div className="content-container navbar-inner">
        <a
          href="#home"
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            onSelectTab('research');
          }}
        >
          <div className="brand-icon-box">
            <BookOpen size={18} />
          </div>
          <span>AI Research Assistant</span>
        </a>

        <div className="nav-links">
          <button
            type="button"
            className={`nav-link ${activeTab === 'research' ? 'active' : ''}`}
            onClick={() => onSelectTab('research')}
          >
            <Search size={16} />
            <span>Research</span>
          </button>

          <button
            type="button"
            className={`nav-link ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => onSelectTab('history')}
          >
            <History size={16} />
            <span>History</span>
            {historyCount > 0 && <span className="nav-badge">{historyCount}</span>}
          </button>

          <div
            className="backend-status-pill"
            title={
              isHealthy
                ? `FastAPI Backend online (v${health.version}) - Mode: ${health.search_mode}`
                : 'Backend is unreachable at http://127.0.0.1:8000'
            }
          >
            <span className={`status-dot ${isHealthy ? '' : 'offline'}`} />
            <span>
              {isHealthy
                ? isTavily
                  ? 'Live Tavily Search'
                  : 'Offline RAG Mode'
                : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
