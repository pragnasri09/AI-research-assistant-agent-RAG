import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { ResearchForm } from './components/ResearchForm';
import { ProgressTracker } from './components/ProgressTracker';
import { ReportView } from './components/ReportView';
import { HistoryView } from './components/HistoryView';
import { ErrorMessage } from './components/ErrorMessage';
import { api } from './services/api';
import './App.css';

export default function App() {
  // Navigation: 'research' | 'history' | 'report'
  const [activeTab, setActiveTab] = useState('research');

  // Backend Health & System Info
  const [health, setHealth] = useState(null);
  const [globalError, setGlobalError] = useState(null);

  // Active Research Session State
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [sessionStatus, setSessionStatus] = useState(null);
  const [isStartingResearch, setIsStartingResearch] = useState(false);

  // Completed Report & Sources Data
  const [currentReport, setCurrentReport] = useState(null);
  const [currentSources, setCurrentSources] = useState([]);

  // Research History
  const [history, setHistory] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Polling ref to clear timers
  const pollTimerRef = useRef(null);

  // 1. Backend Health Check & History Load Functions
  const checkBackendHealth = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
      setGlobalError(null);
    } catch (err) {
      console.warn('Backend health check warning:', err.message);
      setHealth({ status: 'offline' });
      setGlobalError(err.message);
    }
  };

  const fetchHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const list = await api.getHistory();
      setHistory(list);
    } catch (err) {
      console.warn('History fetch warning:', err.message);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Initial mount effect
  useEffect(() => {
    checkBackendHealth();
    fetchHistory();

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
      }
    };
  }, []);

  // 2. Start a New Research Task
  const handleStartResearch = async (question) => {
    setIsStartingResearch(true);
    setGlobalError(null);
    setCurrentReport(null);
    setCurrentSources([]);
    setSessionStatus({
      question,
      status: 'running',
      progress_step: 'Submitting question to autonomous agent pipeline...',
      progress_percent: 5,
      sources_count: 0,
    });
    setActiveTab('research');

    try {
      const res = await api.createResearch(question);
      const sessionId = res.session_id;
      setActiveSessionId(sessionId);
      startPollingSession(sessionId);
    } catch (err) {
      setGlobalError(err.message || 'Failed to initialize research task.');
      setSessionStatus(null);
    } finally {
      setIsStartingResearch(false);
    }
  };

  // 3. Poll session status until completed or failed
  const startPollingSession = (sessionId) => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
    }

    const poll = async () => {
      try {
        const statusData = await api.getStatus(sessionId);
        setSessionStatus(statusData);

        if (statusData.status === 'completed') {
          clearInterval(pollTimerRef.current);
          pollTimerRef.current = null;

          // Research completed! Load full report and extracted sources
          if (statusData.report) {
            setCurrentReport(statusData.report);
          }

          // Fetch extracted sources
          try {
            const sourcesData = await api.getSources(sessionId);
            setCurrentSources(sourcesData);
          } catch (sourceErr) {
            console.warn('Failed to load extracted sources:', sourceErr);
          }

          // Switch to Report view and refresh history
          setActiveTab('report');
          fetchHistory();
        } else if (statusData.status === 'failed') {
          clearInterval(pollTimerRef.current);
          pollTimerRef.current = null;
          setGlobalError(statusData.error || 'The research agent encountered an unrecoverable error during execution.');
        }
      } catch (err) {
        console.warn('Polling error:', err);
        // Do not immediately kill polling on a transient network glitch, but track error
      }
    };

    // Immediate first poll, then interval every 1200ms
    poll();
    pollTimerRef.current = setInterval(poll, 1200);
  };

  const handleCancelSession = () => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    setActiveSessionId(null);
    setSessionStatus(null);
  };

  // 4. Open an existing report from History
  const handleOpenReportFromHistory = async (sessionId) => {
    setGlobalError(null);
    try {
      const statusData = await api.getStatus(sessionId);
      if (statusData.report) {
        setCurrentReport(statusData.report);
        setActiveSessionId(sessionId);
        setSessionStatus(statusData);

        // Fetch sources
        try {
          const sourcesData = await api.getSources(sessionId);
          setCurrentSources(sourcesData);
        } catch {
          setCurrentSources([]);
        }

        setActiveTab('report');
      } else {
        setGlobalError('Selected session does not have a completed report.');
      }
    } catch (err) {
      setGlobalError(`Failed to load report: ${err.message}`);
    }
  };

  // 5. Delete session from history
  const handleDeleteSession = async (sessionId) => {
    try {
      await api.deleteSession(sessionId);
      setHistory((prev) => prev.filter((item) => item.session_id !== sessionId));
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
        setCurrentReport(null);
        setCurrentSources([]);
        setActiveTab('history');
      }
    } catch (err) {
      setGlobalError(`Failed to delete session: ${err.message}`);
    }
  };

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          if (tab === 'history') {
            fetchHistory();
          }
        }}
        historyCount={history.length}
        health={health}
        backendUrl={api.getBaseUrl()}
      />

      <main className="content-container" style={{ flex: 1, paddingBottom: '48px' }}>
        {globalError && (
          <div style={{ marginTop: '20px' }}>
            <ErrorMessage
              error={globalError}
              onRetry={checkBackendHealth}
              onDismiss={() => setGlobalError(null)}
            />
          </div>
        )}

        {/* VIEW 1: RESEARCH HOME (Input + Active Progress) */}
        {activeTab === 'research' && (
          <>
            {sessionStatus && sessionStatus.status === 'running' ? (
              <ProgressTracker
                sessionStatus={sessionStatus}
                onCancel={handleCancelSession}
              />
            ) : (
              <ResearchForm
                onSubmit={handleStartResearch}
                isLoading={isStartingResearch}
              />
            )}
          </>
        )}

        {/* VIEW 2: FULL REPORT */}
        {activeTab === 'report' && (
          <ReportView
            report={currentReport}
            sources={currentSources}
            onBackToSearch={() => {
              setActiveTab('research');
              setSessionStatus(null);
            }}
          />
        )}

        {/* VIEW 3: RESEARCH HISTORY */}
        {activeTab === 'history' && (
          <HistoryView
            history={history}
            isLoading={isLoadingHistory}
            onRefresh={fetchHistory}
            onOpenReport={handleOpenReportFromHistory}
            onDeleteSession={handleDeleteSession}
          />
        )}
      </main>

      <footer className="app-footer">
        <div className="content-container footer-inner">
          <div>
            <strong>AI Research Assistant Agent</strong> &bull; LangGraph Autonomous Pipeline &bull; Chroma RAG
          </div>
          <div>
            Backend: {health?.status === 'healthy' ? api.getBaseUrl() : 'Disconnected'}
          </div>
        </div>
      </footer>
    </div>
  );
}
