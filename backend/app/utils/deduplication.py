from typing import List, Dict, Any
from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    """Normalizes URL by stripping trailing slashes, fragments, and tracking query params."""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    # Remove standard tracking query params like utm_*
    clean_query = "&".join([q for q in parsed.query.split("&") if not q.startswith("utm_")]) if parsed.query else ""
    clean_path = parsed.path.rstrip('/')
    return urlunparse((parsed.scheme, parsed.netloc.lower(), clean_path, parsed.params, clean_query, ''))

def deduplicate_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates sources based on normalized URL and content similarity."""
    seen_urls = set()
    unique_sources = []
    
    for src in sources:
        url = src.get("url", "")
        norm_url = normalize_url(url)
        if not norm_url or norm_url in seen_urls:
            continue
        
        seen_urls.add(norm_url)
        src["url"] = norm_url
        unique_sources.append(src)
        
    return unique_sources
