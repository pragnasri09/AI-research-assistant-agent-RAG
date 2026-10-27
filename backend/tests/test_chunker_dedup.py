import pytest
from app.utils.text_cleaner import clean_text, extract_domain
from app.utils.deduplication import deduplicate_sources, normalize_url
from app.rag.chunker import chunk_text, chunk_sources

def test_text_cleaner():
    raw_html_text = "<p>Hello   World!</p>\n\n\n\n<script>alert(1)</script>   Test text."
    cleaned = clean_text(raw_html_text)
    assert "Hello World!" in cleaned
    assert "alert" not in cleaned

def test_extract_domain():
    assert extract_domain("https://www.stanford.edu/research/ai") == "stanford.edu"
    assert extract_domain("https://arxiv.org/abs/2401.1234") == "arxiv.org"

def test_deduplicate_sources():
    sources = [
        {"url": "https://example.com/paper?utm_source=twitter", "title": "Paper 1"},
        {"url": "https://example.com/paper", "title": "Paper 1 Duplicate"},
        {"url": "https://stanford.edu/study", "title": "Stanford Study"}
    ]
    unique = deduplicate_sources(sources)
    assert len(unique) == 2
    assert unique[0]["url"] == "https://example.com/paper"

def test_chunking():
    text = "Paragraph 1 sentence.\n\nParagraph 2 another long sentence.\n\nParagraph 3 final sentence."
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) >= 2
    
def test_chunk_sources():
    sources = [
        {"source_id": 1, "title": "Test Title", "url": "https://example.com", "domain": "example.com", "content": "This is content for source 1. " * 30}
    ]
    chunks = chunk_sources(sources)
    assert len(chunks) > 0
    assert chunks[0]["source_id"] == 1
    assert chunks[0]["url"] == "https://example.com"
