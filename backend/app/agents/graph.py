import logging
from langgraph.graph import StateGraph, END
from app.agents.state import ResearchState
from app.agents.analyzer import analyze_question_node
from app.agents.planner import generate_search_queries_node
from app.agents.researcher import search_web_node, evaluate_and_extract_node, chunk_and_index_node
from app.agents.summarizer import summarize_sources_node
from app.agents.synthesizer import synthesize_report_node
from app.agents.citation_validator import validate_citations_node, finalize_report_node

logger = logging.getLogger(__name__)

def build_research_graph():
    """Builds and compiles the complete LangGraph research agent workflow."""
    workflow = StateGraph(ResearchState)

    # Add Nodes
    workflow.add_node("analyze_question", analyze_question_node)
    workflow.add_node("generate_search_queries", generate_search_queries_node)
    workflow.add_node("search_web", search_web_node)
    workflow.add_node("evaluate_and_extract", evaluate_and_extract_node)
    workflow.add_node("chunk_and_index", chunk_and_index_node)
    workflow.add_node("summarize_sources", summarize_sources_node)
    workflow.add_node("synthesize_report", synthesize_report_node)
    workflow.add_node("validate_citations", validate_citations_node)
    workflow.add_node("finalize_report", finalize_report_node)

    # Set Entry Point
    workflow.set_entry_point("analyze_question")

    # Define Linear & Conditional Edges
    workflow.add_edge("analyze_question", "generate_search_queries")
    workflow.add_edge("generate_search_queries", "search_web")
    workflow.add_edge("search_web", "evaluate_and_extract")
    workflow.add_edge("evaluate_and_extract", "chunk_and_index")
    workflow.add_edge("chunk_and_index", "summarize_sources")
    workflow.add_edge("summarize_sources", "synthesize_report")
    workflow.add_edge("synthesize_report", "validate_citations")
    workflow.add_edge("validate_citations", "finalize_report")
    workflow.add_edge("finalize_report", END)

    app = workflow.compile()
    return app

research_graph_app = build_research_graph()
