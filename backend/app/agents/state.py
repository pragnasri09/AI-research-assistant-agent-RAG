from typing import List, Dict, Any, Optional, TypedDict

class ResearchState(TypedDict):
    session_id: str
    original_question: str
    analyzed_intent: str
    generated_queries: List[str]
    raw_search_results: List[Dict[str, Any]]
    deduplicated_sources: List[Dict[str, Any]]
    extracted_sources: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    chunks: List[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    source_summaries: List[Dict[str, Any]]
    draft_report: Optional[Dict[str, Any]]
    full_markdown_report: str
    citations_valid: bool
    citation_errors: List[str]
    research_status: str
    progress_step: str
    progress_percent: int
    iteration_count: int
    max_iterations: int
    error: Optional[str]
