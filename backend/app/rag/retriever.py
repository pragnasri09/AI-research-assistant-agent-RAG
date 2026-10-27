from typing import List, Dict, Any
from app.rag.vector_store import ResearchVectorStore
from app.config import settings

def retrieve_relevant_evidence(session_id: str, question: str, queries: List[str], top_k: int = settings.RETRIEVAL_TOP_K) -> List[Dict[str, Any]]:
    """Retrieves top relevant evidence chunks across original research question and sub-queries."""
    vector_store = ResearchVectorStore(session_id=session_id)
    seen_chunk_ids = set()
    all_retrieved = []
    
    # Query main question first
    search_queries = [question] + queries[:3]
    k_per_query = max(2, top_k // len(search_queries))
    
    for q in search_queries:
        chunks = vector_store.query(query_text=q, top_k=k_per_query)
        for c in chunks:
            cid = c["chunk_id"]
            if cid not in seen_chunk_ids:
                seen_chunk_ids.add(cid)
                all_retrieved.append(c)
                
    return all_retrieved
