import re

def clean_text(text: str) -> str:
    """Cleans extracted text by normalizing whitespace, stripping junk characters, and preserving structure."""
    if not text:
        return ""
    # Remove HTML residual tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize multiple whitespace / newlines
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_domain(url: str) -> str:
    """Extracts clean domain name from URL."""
    if not url:
        return "unknown"
    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if match:
        return match.group(1).lower()
    return url.lower()
