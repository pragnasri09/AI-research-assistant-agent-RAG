import logging
import json
import re
from google import genai
from app.config import settings
from app.agents.state import ResearchState

logger = logging.getLogger(__name__)

async def generate_search_queries_node(state: ResearchState) -> ResearchState:
    question = state["original_question"]
    logger.info(f"Generating search queries for: {question}")
    
    # Default fallback structured query generation
    default_queries = [
        f"{question} overview background analysis",
        f"{question} key productivity metrics empirical findings",
        f"{question} technical challenges risks and limitations",
        f"{question} future trends and industry adoption report",
        f"{question} recent research paper benchmarks 2025 2026"
    ]
    
    generated = default_queries
    
    if settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = (
                f"You are a senior academic researcher. For the question: '{question}', generate 5 distinct, highly targeted web search queries.\n"
                f"Coverage needed: 1) General background & state-of-the-art, 2) Quantitative/empirical metrics, 3) Challenges/risks, 4) Real-world implementations, 5) Recent academic findings.\n"
                f"Return ONLY a raw JSON array of 5 query strings. Example format: [\"query 1\", \"query 2\", \"query 3\", \"query 4\", \"query 5\"]"
            )
            response = client.models.generate_content(
                model=settings.MODEL_NAME,
                contents=prompt
            )
            if response and response.text:
                text = response.text.strip()
                # Clean code blocks if present
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\n|\n```$", "", text, flags=re.MULTILINE).strip()
                parsed = json.loads(text)
                if isinstance(parsed, list) and len(parsed) >= 3:
                    generated = [str(q).strip() for q in parsed[:6]]
        except Exception as e:
            logger.warning(f"Query generation LLM call failed: {e}. Using robust default queries.")

    state["generated_queries"] = generated
    state["progress_step"] = f"Generated {len(generated)} targeted web search queries"
    state["progress_percent"] = 20
    return state
