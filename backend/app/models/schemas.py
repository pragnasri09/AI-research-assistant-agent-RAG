from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000, description="The research question or topic")

class SourceSummary(BaseModel):
    source_id: int
    title: str
    url: str
    domain: str
    publication_date: Optional[str] = "Unknown"
    summary: str
    key_findings: List[str] = []
    quality_score: float = 0.0

class CitationItem(BaseModel):
    source_id: int
    title: str
    url: str

class BibliographyItem(BaseModel):
    source_id: int
    title: str
    domain: str
    url: str
    publication_date: Optional[str] = "Unknown"

class SectionContent(BaseModel):
    title: str
    content: str
    citations: List[int] = []

class ResearchReport(BaseModel):
    session_id: str
    question: str
    executive_summary: str
    key_findings: List[str]
    introduction: str
    detailed_analysis: List[SectionContent]
    evidence_and_insights: str
    contrasting_perspectives: Optional[str] = ""
    limitations: str
    conclusion: str
    bibliography: List[BibliographyItem]
    is_validated: bool = True
    full_markdown: str = ""

class ResearchStatusResponse(BaseModel):
    session_id: str
    question: str
    status: str
    progress_step: str
    progress_percent: int
    sources_count: int = 0
    created_at: str
    report: Optional[ResearchReport] = None
    error: Optional[str] = None

class ResearchHistoryItem(BaseModel):
    session_id: str
    question: str
    status: str
    sources_count: int
    created_at: str
    executive_summary_preview: Optional[str] = ""
