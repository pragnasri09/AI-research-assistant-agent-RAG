from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Executes web search for a single query.
        Returns list of dicts with: title, url, snippet, domain, publication_date.
        """
        pass
