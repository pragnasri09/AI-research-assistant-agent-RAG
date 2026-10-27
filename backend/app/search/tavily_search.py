import logging
from typing import List, Dict, Any
from tavily import TavilyClient
from app.search.search_interface import BaseSearchProvider
from app.utils.text_cleaner import extract_domain
from app.config import settings

logger = logging.getLogger(__name__)

class TavilySearchProvider(BaseSearchProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.client:
            logger.warning("Tavily API key not found. TavilySearchProvider unavailable.")
            return []
            
        try:
            # Execute search
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_raw_content=True
            )
            
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", "Untitled Source"),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "domain": extract_domain(item.get("url", "")),
                    "publication_date": item.get("published_date") or "2026",
                    "search_query": query,
                    "raw_content": item.get("raw_content") or item.get("content") or ""
                })
            return results
        except Exception as e:
            logger.error(f"Tavily search failed for query '{query}': {str(e)}")
            return []
