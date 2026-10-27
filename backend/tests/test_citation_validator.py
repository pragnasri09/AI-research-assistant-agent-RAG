import pytest
from app.utils.citation_utils import extract_citation_numbers, validate_and_clean_citations, generate_report_markdown

def test_extract_citation_numbers():
    text = "Generative AI improves software engineering productivity [1] and code quality [3][2]."
    nums = extract_citation_numbers(text)
    assert nums == [1, 2, 3]

def test_validate_and_clean_citations():
    # Valid source IDs are 1 and 2. Citation [99] is invalid/hallucinated and should be stripped.
    text = "AI code generation [1] increases speed [99] and test coverage [2]."
    cleaned, used = validate_and_clean_citations(text, valid_source_ids=[1, 2])
    assert "[1]" in cleaned
    assert "[2]" in cleaned
    assert "[99]" not in cleaned
    assert sorted(used) == [1, 2]

def test_generate_report_markdown():
    report = {
        "question": "Impact of AI on Software",
        "executive_summary": "Summary text [1].",
        "key_findings": ["Finding 1 [1]", "Finding 2 [2]"],
        "introduction": "Intro text.",
        "detailed_analysis": [{"title": "Analysis Sec", "content": "Detailed text [1]."}],
        "evidence_and_insights": "Evidence text.",
        "limitations": "Limitations text.",
        "conclusion": "Conclusion text.",
        "bibliography": [
            {"source_id": 1, "title": "Paper A", "domain": "arxiv.org", "url": "https://arxiv.org/1", "publication_date": "2026"},
            {"source_id": 2, "title": "Paper B", "domain": "stanford.edu", "url": "https://stanford.edu/2", "publication_date": "2026"}
        ]
    }
    sources = [
        {"source_id": 1, "title": "Paper A", "domain": "arxiv.org", "url": "https://arxiv.org/1"},
        {"source_id": 2, "title": "Paper B", "domain": "stanford.edu", "url": "https://stanford.edu/2"}
    ]
    md = generate_report_markdown(report, sources)
    assert "# Impact of AI on Software" in md
    assert "## References & Bibliography" in md
    assert "[1] **Paper A**" in md
