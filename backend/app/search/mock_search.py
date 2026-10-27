import logging
from typing import List, Dict, Any
from app.search.search_interface import BaseSearchProvider
from app.utils.text_cleaner import extract_domain

logger = logging.getLogger(__name__)

class MockSearchProvider(BaseSearchProvider):
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"[MockSearch] Searching for query: {query}")
        
        # Generates realistic mock web search results based on query terms
        q_lower = query.lower()
        results = [
            {
                "title": f"Academic Overview & Research Analysis: {query.capitalize()}",
                "url": f"https://arxiv.org/html/paper_{hash(query) % 10000}",
                "snippet": f"Comprehensive study examining {query}. Research findings demonstrate structural shifts, key performance benchmarks, and empirical analysis across multiple domains.",
                "domain": "arxiv.org",
                "publication_date": "2026-02-14",
                "search_query": query,
                "raw_content": f"Full academic paper discussing {query}. Generative AI tools and autonomous systems offer substantial advantages in developer throughput, code safety, and workflow automation. Quantitative metrics indicate up to 40% speedup in routine tasks."
            },
            {
                "title": f"Industry Survey and Technical Report on {query.capitalize()}",
                "url": f"https://research.stanford.edu/reports/{abs(hash(query)) % 999}",
                "snippet": f"Stanford Human-Centered AI report analyzing the state of {query}. Includes empirical surveys, architectural patterns, and practical evaluation metrics.",
                "domain": "stanford.edu",
                "publication_date": "2026-01-20",
                "search_query": query,
                "raw_content": f"Stanford Institute for Human-Centered AI report on {query}. Systematic investigation reveals widespread adoption of assistant technology across software engineering teams. Key challenges include maintaining code context, security auditability, and verifying citation evidence."
            },
            {
                "title": f"IEEE Technical Insights: Enterprise Implementation of {query.capitalize()}",
                "url": f"https://ieexplore.ieee.org/document/{abs(hash(query)) % 8888}",
                "snippet": f"IEEE Software engineering framework exploring implementation metrics, automated verification, and retrieval-augmented generation strategies for {query}.",
                "domain": "ieee.org",
                "publication_date": "2025-11-10",
                "search_query": query,
                "raw_content": f"IEEE Software Journal special issue on {query}. Incorporating retrieval-augmented generation (RAG) models dramatically reduces hallucination risks while retaining real-time search capabilities. Rigorous document chunking and vector index retrieval remain critical."
            },
            {
                "title": f"MIT Technology Review: Future Outlook of {query.capitalize()}",
                "url": f"https://technologyreview.com/2026/insight-{abs(hash(query)) % 777}",
                "snippet": f"Analytical deep dive into market trends, technological limitations, and strategic roadmap for {query} over the next decade.",
                "domain": "technologyreview.com",
                "publication_date": "2026-03-01",
                "search_query": query,
                "raw_content": f"MIT Technology Review analysis of {query}. Industry adoption highlights key trade-offs between rapid prototyping and long-term codebase maintainability. Experts emphasize the necessity of deterministic citation grounding and multi-source verification."
            }
        ]
        return results[:max_results]
