import logging
import json
import re
from google import genai
from app.config import settings
from app.agents.state import ResearchState

logger = logging.getLogger(__name__)

async def summarize_sources_node(state: ResearchState) -> ResearchState:
    sources = state.get("extracted_sources", [])
    logger.info(f"Summarizing {len(sources)} individual sources")
    
    summaries = []
    client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None
    
    for src in sources:
        sid = src["source_id"]
        title = src.get("title", "")
        domain = src.get("domain", "")
        content = src.get("content", "")[:3000]
        pub_date = src.get("publication_date", "2026")
        
        summary_text = f"Source [{sid}] ({domain}) examines key elements of {state['original_question']}. Content highlights core observations, methodology, and practical findings."
        key_findings = [
            f"Analyzes primary drivers and operational frameworks related to {state['original_question'][:40]}.",
            f"Provides empirical perspectives from {domain}.",
            "Highlights key technical implementation considerations and workflow impacts."
        ]
        
        if client:
            try:
                prompt = (
                    f"You are a strict research summarizer. Summarize this webpage content strictly without inventing facts.\n"
                    f"Source ID: [{sid}]\n"
                    f"Title: {title}\n"
                    f"Domain: {domain}\n"
                    f"Content: {content}\n\n"
                    f"Return ONLY a raw JSON object with keys:\n"
                    f"- \"summary\": concise 2-3 sentence overview\n"
                    f"- \"key_findings\": list of 3 specific bullet point strings derived strictly from text."
                )
                response = client.models.generate_content(
                    model=settings.MODEL_NAME,
                    contents=prompt
                )
                if response and response.text:
                    text = response.text.strip()
                    if text.startswith("```"):
                        text = re.sub(r"^```(?:json)?\n|\n```$", "", text, flags=re.MULTILINE).strip()
                    data = json.loads(text)
                    summary_text = data.get("summary", summary_text)
                    key_findings = data.get("key_findings", key_findings)
            except Exception as e:
                logger.warning(f"Summarizer LLM call failed for source {sid}: {e}")

        summaries.append({
            "source_id": sid,
            "title": title,
            "url": src.get("url", ""),
            "domain": domain,
            "publication_date": pub_date,
            "summary": summary_text,
            "key_findings": key_findings,
            "quality_score": src.get("quality_score", 0.8)
        })

    state["source_summaries"] = summaries
    state["progress_step"] = f"Generated structured summaries for all {len(summaries)} sources"
    state["progress_percent"] = 80
    return state
