import re
from typing import List, Dict, Any, Tuple

def extract_citation_numbers(text: str) -> List[int]:
    """Extracts all [N] citation numbers from text."""
    if not text:
        return []
    matches = re.findall(r'\[(\d+)\]', text)
    return sorted(list(set(int(m) for m in matches)))

def validate_and_clean_citations(text: str, valid_source_ids: List[int]) -> Tuple[str, List[int]]:
    """
    Ensures every [N] in text is in valid_source_ids.
    Removes invalid citation references.
    Returns cleaned text and list of used valid citation IDs.
    """
    if not text:
        return "", []
    
    valid_set = set(valid_source_ids)
    used_ids = set()

    def replace_citation(match):
        num = int(match.group(1))
        if num in valid_set:
            used_ids.add(num)
            return f"[{num}]"
        else:
            return ""

    cleaned_text = re.sub(r'\[(\d+)\]', replace_citation, text)
    # Clean up double spaces created by removal
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    return cleaned_text.strip(), sorted(list(used_ids))

def generate_report_markdown(report_data: Dict[str, Any], sources: List[Dict[str, Any]]) -> str:
    """Formats full structured research report into Markdown."""
    lines = []
    lines.append(f"# {report_data.get('question', 'Research Report')}\n")
    
    lines.append("## Executive Summary")
    lines.append(f"{report_data.get('executive_summary', '')}\n")
    
    lines.append("## Key Findings")
    for idx, finding in enumerate(report_data.get("key_findings", []), start=1):
        lines.append(f"{idx}. {finding}")
    lines.append("")
    
    lines.append("## Introduction")
    lines.append(f"{report_data.get('introduction', '')}\n")
    
    lines.append("## Detailed Analysis")
    for sec in report_data.get("detailed_analysis", []):
        lines.append(f"### {sec.get('title', 'Analysis Section')}")
        lines.append(f"{sec.get('content', '')}\n")
        
    lines.append("## Evidence and Insights")
    lines.append(f"{report_data.get('evidence_and_insights', '')}\n")
    
    if report_data.get("contrasting_perspectives"):
        lines.append("## Contrasting Perspectives")
        lines.append(f"{report_data.get('contrasting_perspectives', '')}\n")
        
    lines.append("## Limitations")
    lines.append(f"{report_data.get('limitations', '')}\n")
    
    lines.append("## Conclusion")
    lines.append(f"{report_data.get('conclusion', '')}\n")
    
    lines.append("---")
    lines.append("## References & Bibliography")
    
    sources_dict = {s.get("source_id", idx + 1): s for idx, s in enumerate(sources)}
    
    for bib in report_data.get("bibliography", []):
        sid = bib.get("source_id")
        src = sources_dict.get(sid, bib)
        title = src.get("title", "Untitled Source")
        url = src.get("url", "#")
        domain = src.get("domain", "")
        pub_date = src.get("publication_date", "Unknown")
        lines.append(f"[{sid}] **{title}** - *{domain}* ({pub_date})\n  URL: [{url}]({url})\n")
        
    return "\n".join(lines)
