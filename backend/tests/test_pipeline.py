import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import init_db, get_session
from app.agents.graph import research_graph_app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "project" in data

@pytest.mark.asyncio
async def test_end_to_end_langgraph_pipeline():
    init_db()
    session_id = "test_session_123"
    
    initial_state = {
        "session_id": session_id,
        "original_question": "What is the impact of generative AI on software engineering?",
        "analyzed_intent": "",
        "generated_queries": [],
        "raw_search_results": [],
        "deduplicated_sources": [],
        "extracted_sources": [],
        "documents": [],
        "chunks": [],
        "retrieved_chunks": [],
        "source_summaries": [],
        "draft_report": None,
        "full_markdown_report": "",
        "citations_valid": False,
        "citation_errors": [],
        "research_status": "running",
        "progress_step": "Init",
        "progress_percent": 5,
        "iteration_count": 0,
        "max_iterations": 2,
        "error": None
    }
    
    final_state = await research_graph_app.ainvoke(initial_state)
    
    assert final_state["research_status"] == "completed"
    assert final_state["progress_percent"] == 100
    assert len(final_state["extracted_sources"]) > 0
    assert final_state["draft_report"] is not None
    assert final_state["draft_report"]["is_validated"] is True
    
    # Check SQLite DB persistence
    saved = get_session(session_id)
    assert saved is not None
    assert saved["status"] == "completed"
    assert saved["sources_count"] > 0
