from fastapi import APIRouter, HTTPException, Path, status
from typing import List, Dict, Any
from app.models.schemas import ResearchHistoryItem
from app.models.database import get_history, delete_session, get_session

router = APIRouter(prefix="/api/research", tags=["History"])

@router.get("/history", response_model=List[ResearchHistoryItem])
async def list_research_history():
    """Lists all past research sessions."""
    history_items = get_history()
    return [ResearchHistoryItem(**item) for item in history_items]

@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
async def delete_research_session(session_id: str = Path(..., description="Session ID to delete")):
    """Deletes a research session and its associated sources from history."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found.")
        
    delete_session(session_id)
    return {"message": f"Session {session_id} deleted successfully."}
