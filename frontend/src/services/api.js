/**
 * API service for communicating with the FastAPI AI Research Assistant backend.
 */

const resolveBaseUrl = () => {
  // 1. Explicit environment variable: VITE_API_BASE_URL (or VITE_API_URL fallback)
  const envUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim() !== '') {
    return envUrl.trim().replace(/\/+$/, '');
  }

  // 2. Deployed production fallback:
  // When running in production (Vercel) or on any non-local domain, default to the deployed Render backend
  if (
    import.meta.env.PROD ||
    (typeof window !== 'undefined' &&
      window.location.hostname !== 'localhost' &&
      window.location.hostname !== '127.0.0.1')
  ) {
    return 'https://ai-research-assistant-backend-shcr.onrender.com';
  }

  // 3. Local development fallback only
  return 'http://127.0.0.1:8000';
};

const BASE_URL = resolveBaseUrl();

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      let errorData = null;
      try {
        errorData = await response.json();
      } catch {
        // Response might not be JSON
      }
      const message = errorData?.detail || errorData?.message || `Request failed with status ${response.status}`;
      throw new ApiError(message, response.status, errorData);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    // Network or server offline error
    throw new ApiError(
      `Unable to connect to backend server at ${BASE_URL}. Ensure FastAPI is running.`,
      0,
      { originalError: err.message }
    );
  }
}

export const api = {
  /**
   * Get resolved base URL
   */
  getBaseUrl() {
    return BASE_URL;
  },

  /**
   * Health check endpoint
   */
  async getHealth() {
    return request('/api/health');
  },

  /**
   * Submit a new research question
   * @param {string} question
   * @returns {Promise<{session_id: string, status: string}>}
   */
  async createResearch(question) {
    return request('/api/research', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  },

  /**
   * Get research status, progress, and full report when complete
   * @param {string} sessionId
   * @returns {Promise<ResearchStatusResponse>}
   */
  async getStatus(sessionId) {
    return request(`/api/research/${encodeURIComponent(sessionId)}`);
  },

  /**
   * Get all extracted sources for a session
   * @param {string} sessionId
   * @returns {Promise<Array<SourceSummary>>}
   */
  async getSources(sessionId) {
    return request(`/api/research/${encodeURIComponent(sessionId)}/sources`);
  },

  /**
   * Get past research session history
   * @returns {Promise<Array<ResearchHistoryItem>>}
   */
  async getHistory() {
    return request('/api/research/history');
  },

  /**
   * Delete a research session from history
   * @param {string} sessionId
   * @returns {Promise<{message: string}>}
   */
  async deleteSession(sessionId) {
    return request(`/api/research/${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
  },
};
