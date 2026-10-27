from fastapi import APIRouter, HTTPException, Path, status
from typing import List, Dict, Any
from app.models.schemas import ResearchRequest, ResearchStatusResponse, SourceSummary, ResearchReport
from app.services.research_service import start_research_task
from app.models.database import get_session, get_session_sources

router = APIRouter(prefix="/api/research", tags=["Research"])

@router.post("", response_model=Dict[str, str], status_code=status.HTTP_202_ACCEPTED)
async def create_research(request: ResearchRequest):
    """Submits a new research question to start autonomous research pipeline."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Research question cannot be empty.")
    
    session_id = start_research_task(question)
    return {"session_id": session_id, "status": "started"}

@router.get("/{session_id}", response_model=ResearchStatusResponse)
async def get_research_status(session_id: str = Path(..., description="Unique session ID")):
    """Retrieves live research status, progress step, percent, and full report when completed."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found.")
    
    report_data = None
    if session.get("report"):
        report_data = ResearchReport(**session["report"])
        
    return ResearchStatusResponse(
        session_id=session["session_id"],
        question=session["question"],
        status=session["status"],
        progress_step=session["progress_step"],
        progress_percent=session["progress_percent"],
        sources_count=session["sources_count"],
        created_at=session["created_at"],
        report=report_data,
        error=session.get("error")
    )

@router.get("/{session_id}/sources", response_model=List[SourceSummary])
async def get_research_sources(session_id: str = Path(..., description="Unique session ID")):
    """Retrieves detailed list of all extracted sources and summaries for a session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found.")
        
    sources = get_session_sources(session_id)
    return [SourceSummary(**s) for s in sources]
