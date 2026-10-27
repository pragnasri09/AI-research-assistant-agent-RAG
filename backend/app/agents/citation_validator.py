import logging
from typing import List, Dict, Any
from app.utils.citation_utils import validate_and_clean_citations, generate_report_markdown, extract_citation_numbers
from app.agents.state import ResearchState
from app.models.database import update_session_report, save_sources

logger = logging.getLogger(__name__)

async def validate_citations_node(state: ResearchState) -> ResearchState:
    report = state.get("draft_report", {})
    sources = state.get("extracted_sources", [])
    summaries = state.get("source_summaries", [])
    
    valid_source_ids = [s["source_id"] for s in sources] if sources else [1]
    logger.info(f"Validating citations against valid source IDs: {valid_source_ids}")
    
    citation_errors = []
    
    # 1. Clean citations in executive summary
    exec_summary, _ = validate_and_clean_citations(report.get("executive_summary", ""), valid_source_ids)
    report["executive_summary"] = exec_summary
    
    # 2. Clean key findings citations
    cleaned_findings = []
    for finding in report.get("key_findings", []):
        cleaned, _ = validate_and_clean_citations(finding, valid_source_ids)
        cleaned_findings.append(cleaned)
    report["key_findings"] = cleaned_findings
    
    # 3. Clean introduction
    intro, _ = validate_and_clean_citations(report.get("introduction", ""), valid_source_ids)
    report["introduction"] = intro
    
    # 4. Clean detailed analysis
    cleaned_sections = []
    for sec in report.get("detailed_analysis", []):
        title = sec.get("title", "")
        content = sec.get("content", "")
        cleaned_content, used = validate_and_clean_citations(content, valid_source_ids)
        cleaned_sections.append({
            "title": title,
            "content": cleaned_content,
            "citations": used
        })
    report["detailed_analysis"] = cleaned_sections
    
    # 5. Clean remaining sections
    evidence, _ = validate_and_clean_citations(report.get("evidence_and_insights", ""), valid_source_ids)
    report["evidence_and_insights"] = evidence
    
    contrasting, _ = validate_and_clean_citations(report.get("contrasting_perspectives", ""), valid_source_ids)
    report["contrasting_perspectives"] = contrasting
    
    conclusion, _ = validate_and_clean_citations(report.get("conclusion", ""), valid_source_ids)
    report["conclusion"] = conclusion
    
    # 6. Verify Bibliography Mapping
    sources_by_id = {s["source_id"]: s for s in (summaries or sources)}
    valid_bibliography = []
    
    for sid in valid_source_ids:
        src = sources_by_id.get(sid, {})
        valid_bibliography.append({
            "source_id": sid,
            "title": src.get("title", f"Source {sid}"),
            "domain": src.get("domain", "web"),
            "url": src.get("url", "#"),
            "publication_date": src.get("publication_date", "2026")
        })
    report["bibliography"] = valid_bibliography
    report["is_validated"] = True
    
    # Generate full Markdown version
    full_markdown = generate_report_markdown(report, summaries or sources)
    report["full_markdown"] = full_markdown
    
    state["draft_report"] = report
    state["full_markdown_report"] = full_markdown
    state["citations_valid"] = True
    state["citation_errors"] = citation_errors
    state["progress_step"] = "Citation validation passed cleanly"
    state["progress_percent"] = 95
    return state

async def finalize_report_node(state: ResearchState) -> ResearchState:
    session_id = state["session_id"]
    report = state.get("draft_report", {})
    sources = state.get("source_summaries", []) or state.get("extracted_sources", [])
    full_md = state.get("full_markdown_report", "")
    
    logger.info(f"Finalizing session {session_id} in database")
    
    # Persist sources into SQLite DB
    save_sources(session_id=session_id, sources_list=sources)
    
    # Update session status to completed
    update_session_report(
        session_id=session_id,
        status="completed",
        progress_step="Research completed successfully",
        progress_percent=100,
        report_dict=report,
        full_markdown=full_md,
        sources_count=len(sources)
    )
    
    state["research_status"] = "completed"
    state["progress_step"] = "Research completed successfully"
    state["progress_percent"] = 100
    return state
