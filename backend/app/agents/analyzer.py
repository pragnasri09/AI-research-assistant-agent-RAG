import logging
import json
from google import genai
from app.config import settings
from app.agents.state import ResearchState

logger = logging.getLogger(__name__)

async def analyze_question_node(state: ResearchState) -> ResearchState:
    question = state["original_question"]
    logger.info(f"Analyzing question: {question}")
    
    intent_summary = f"Research inquiry focused on evaluating '{question}' across analytical, technical, practical, and empirical dimensions."
    
    if settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = (
                f"Analyze this research question for an academic AI Research Assistant: '{question}'.\n"
                f"Identify: 1) Core domain, 2) Key sub-topics to investigate, 3) Desired depth of evidence.\n"
                f"Respond with a concise 2-sentence summary of the research scope."
            )
            response = client.models.generate_content(
                model=settings.MODEL_NAME,
                contents=prompt
            )
            if response and response.text:
                intent_summary = response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini analysis call failed: {e}. Using structured default intent.")

    state["analyzed_intent"] = intent_summary
    state["progress_step"] = "Understood research question scope and domain context"
    state["progress_percent"] = 10
    return state
