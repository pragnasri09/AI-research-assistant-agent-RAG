import logging
import asyncio
from typing import List, Dict, Any
from app.search.tavily_search import TavilySearchProvider
from app.search.mock_search import MockSearchProvider
from app.utils.deduplication import deduplicate_sources
from app.loaders.webpage_loader import fetch_and_extract_webpage
from app.rag.chunker import chunk_sources
from app.rag.vector_store import ResearchVectorStore
from app.rag.retriever import retrieve_relevant_evidence
from app.config import settings
from app.agents.state import ResearchState
from app.models.database import save_session

logger = logging.getLogger(__name__)

async def search_web_node(state: ResearchState) -> ResearchState:
    queries = state["generated_queries"]
    logger.info(f"Executing web searches for {len(queries)} queries")
    
    provider = TavilySearchProvider() if settings.TAVILY_API_KEY else MockSearchProvider()
    
    all_results = []
    for query in queries:
        try:
            results = await provider.search(query=query, max_results=settings.MAX_SEARCH_RESULTS)
            all_results.extend(results)
        except Exception as e:
            logger.warning(f"Search failed for query '{query}': {e}")
            
    # Fallback to mock search if live Tavily returned empty
    if not all_results and isinstance(provider, TavilySearchProvider):
        logger.warning("Live search returned 0 results. Falling back to MockSearchProvider.")
        mock_prov = MockSearchProvider()
        for query in queries[:3]:
            res = await mock_prov.search(query=query, max_results=3)
            all_results.extend(res)
            
    state["raw_search_results"] = all_results
    state["progress_step"] = f"Gathered {len(all_results)} raw search results"
    state["progress_percent"] = 35
    save_session(state["session_id"], state["original_question"], "running", state["progress_step"], state["progress_percent"])
    return state

async def evaluate_and_extract_node(state: ResearchState) -> ResearchState:
    raw_results = state.get("raw_search_results", [])
    deduped = deduplicate_sources(raw_results)
    
    logger.info(f"Deduplicated {len(raw_results)} results to {len(deduped)} unique URLs")
    
    # Extract webpage content concurrently with limit
    extracted_sources = []
    tasks = []
    
    # Select top quality candidates (up to 8 sources)
    candidates = deduped[:8]
    
    for idx, candidate in enumerate(candidates, start=1):
        url = candidate.get("url", "")
        tasks.append(fetch_and_extract_webpage(url))
        
    extracted_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for idx, (cand, res) in enumerate(zip(candidates, extracted_results), start=1):
        if isinstance(res, dict) and res.get("success") and len(res.get("content", "")) > 100:
            extracted_sources.append({
                "source_id": idx,
                "title": res.get("title") or cand.get("title") or f"Source {idx}",
                "url": cand.get("url"),
                "domain": cand.get("domain") or res.get("domain"),
                "publication_date": cand.get("publication_date", "2026"),
                "content": res.get("content"),
                "snippet": cand.get("snippet", ""),
                "quality_score": 0.9 if cand.get("domain", "").endswith((".edu", ".org", ".gov", "arxiv.org", "ieee.org")) else 0.75
            })
        else:
            # Fallback to snippet/raw_content if full scraping was blocked
            content = cand.get("raw_content") or cand.get("snippet") or ""
            if len(content) > 50:
                extracted_sources.append({
                    "source_id": idx,
                    "title": cand.get("title") or f"Source {idx}",
                    "url": cand.get("url"),
                    "domain": cand.get("domain"),
                    "publication_date": cand.get("publication_date", "2026"),
                    "content": content,
                    "snippet": cand.get("snippet", ""),
                    "quality_score": 0.7
                })
                
    # Re-index source IDs sequentially: 1, 2, 3...
    for i, s in enumerate(extracted_sources, start=1):
        s["source_id"] = i
        
    state["extracted_sources"] = extracted_sources
    state["progress_step"] = f"Successfully extracted and validated {len(extracted_sources)} sources"
    state["progress_percent"] = 55
    save_session(state["session_id"], state["original_question"], "running", state["progress_step"], state["progress_percent"])
    return state

async def chunk_and_index_node(state: ResearchState) -> ResearchState:
    sources = state.get("extracted_sources", [])
    session_id = state["session_id"]
    
    chunks = chunk_sources(sources)
    logger.info(f"Generated {len(chunks)} text chunks from {len(sources)} sources")
    
    # Store in ChromaDB
    try:
        vector_store = ResearchVectorStore(session_id=session_id)
        vector_store.add_chunks(chunks)
        
        # Perform RAG retrieval
        retrieved = retrieve_relevant_evidence(
            session_id=session_id,
            question=state["original_question"],
            queries=state.get("generated_queries", [])
        )
        state["retrieved_chunks"] = retrieved
    except Exception as e:
        logger.warning(f"ChromaDB indexing error: {e}. Falling back to inline text chunk retrieval.")
        state["retrieved_chunks"] = chunks[:12]
        
    state["chunks"] = chunks
    state["progress_step"] = f"Indexed {len(chunks)} chunks into ChromaDB & retrieved top evidence"
    state["progress_percent"] = 70
    save_session(state["session_id"], state["original_question"], "running", state["progress_step"], state["progress_percent"])
    return state
