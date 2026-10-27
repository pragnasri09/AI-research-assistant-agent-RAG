import uuid
import asyncio
import logging
from typing import Dict, Any, Optional
from app.models.database import save_session, update_session_error, get_session
from app.agents.graph import research_graph_app
from app.agents.state import ResearchState

logger = logging.getLogger(__name__)

# Active background task dictionary
_active_tasks: Dict[str, asyncio.Task] = {}

async def run_research_pipeline(session_id: str, question: str):
    logger.info(f"Starting research task background execution for session: {session_id}")
    
    initial_state: ResearchState = {
        "session_id": session_id,
        "original_question": question,
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
        "progress_step": "Initializing research agent",
        "progress_percent": 5,
        "iteration_count": 0,
        "max_iterations": 2,
        "error": None
    }
    
    try:
        # Save initial session in DB
        save_session(session_id, question, "running", "Initializing research pipeline", 5)
        
        # Invoke LangGraph async pipeline
        final_state = await research_graph_app.ainvoke(initial_state)
        logger.info(f"LangGraph execution finished for session: {session_id}")
    except Exception as e:
        logger.exception(f"Research pipeline execution failed for session {session_id}: {e}")
        update_session_error(session_id, str(e))
    finally:
        if session_id in _active_tasks:
            del _active_tasks[session_id]

def start_research_task(question: str) -> str:
    session_id = str(uuid.uuid4())
    logger.info(f"Creating new research session {session_id} for question: '{question}'")
    
    # Save initial pending status
    save_session(session_id, question, "running", "Starting background worker", 2)
    
    # Spawn background task
    task = asyncio.create_task(run_research_pipeline(session_id, question))
    _active_tasks[session_id] = task
    
    return session_id
