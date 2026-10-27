import httpx
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any, Optional
from app.utils.text_cleaner import clean_text, extract_domain
from app.config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

async def fetch_and_extract_webpage(url: str, timeout: int = settings.REQUEST_TIMEOUT) -> Dict[str, Any]:
    """
    Fetches HTML content from URL and extracts readable body text.
    Handles errors gracefully without crashing the pipeline.
    """
    result = {
        "url": url,
        "domain": extract_domain(url),
        "title": "",
        "content": "",
        "success": False,
        "error": None
    }
    
    if not url or not url.startswith("http"):
        result["error"] = "Invalid URL format"
        return result

    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text

        # Try Trafilatura if available for high quality extraction
        try:
            import trafilatura
            extracted_text = trafilatura.extract(html)
            if extracted_text and len(extracted_text.strip()) > 100:
                soup = BeautifulSoup(html, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else url
                result["title"] = title
                result["content"] = clean_text(extracted_text)
                result["success"] = True
                return result
        except Exception:
            pass

        # Fallback to BeautifulSoup parsing
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "form", "svg"]):
            element.decompose()
            
        title = soup.title.string.strip() if soup.title and soup.title.string else extract_domain(url)
        
        # Collect paragraph text
        paragraphs = [p.get_text().strip() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']) if len(p.get_text().strip()) > 20]
        full_text = "\n\n".join(paragraphs)
        cleaned = clean_text(full_text)
        
        if len(cleaned) < 50:
            # Try raw body text
            cleaned = clean_text(soup.get_text())
            
        result["title"] = title
        result["content"] = cleaned[:15000] # Limit per source text length
        result["success"] = len(result["content"]) > 50
        
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {str(e)}")
        result["error"] = str(e)
        
    return result
