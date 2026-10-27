from typing import List, Dict, Any
from app.config import settings

def chunk_text(text: str, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP) -> List[str]:
    """Splits plain text into overlapping chunks cleanly on paragraph or sentence boundaries."""
    if not text:
        return []
        
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue
            
        if len(current_chunk) + len(p_clean) + 2 <= chunk_size:
            current_chunk += ("\n\n" + p_clean) if current_chunk else p_clean
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # Handle case where paragraph itself exceeds chunk_size
            if len(p_clean) > chunk_size:
                words = p_clean.split(" ")
                sub_chunk = ""
                for word in words:
                    if len(sub_chunk) + len(word) + 1 <= chunk_size:
                        sub_chunk += (" " + word) if sub_chunk else word
                    else:
                        chunks.append(sub_chunk)
                        # Keep overlap from end of sub_chunk
                        overlap_start = max(0, len(sub_chunk) - overlap)
                        sub_chunk = sub_chunk[overlap_start:] + " " + word
                if sub_chunk:
                    current_chunk = sub_chunk
            else:
                # Keep overlap from previous chunk
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + p_clean
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def chunk_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chunks all sources while preserving source metadata on every chunk."""
    all_chunks = []
    chunk_global_id = 0
    
    for src in sources:
        source_id = src.get("source_id", 1)
        title = src.get("title", "Untitled Source")
        url = src.get("url", "")
        domain = src.get("domain", "")
        content = src.get("content", "")
        
        text_chunks = chunk_text(content)
        for idx, text in enumerate(text_chunks):
            chunk_global_id += 1
            all_chunks.append({
                "chunk_id": f"src_{source_id}_c_{idx}",
                "global_id": chunk_global_id,
                "source_id": source_id,
                "title": title,
                "url": url,
                "domain": domain,
                "content": text
            })
            
    return all_chunks
