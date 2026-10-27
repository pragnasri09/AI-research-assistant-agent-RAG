import logging
from typing import List
from chromadb.utils import embedding_functions
from app.config import settings

logger = logging.getLogger(__name__)

def get_embedding_function():
    """Returns ChromaDB compatible embedding function (Gemini or Default Onnx/MiniLM)."""
    if settings.GEMINI_API_KEY:
        try:
            # Check if Google GenAI Embedding function is available
            from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
            return GoogleGenerativeAiEmbeddingFunction(api_key=settings.GEMINI_API_KEY, model_name="models/embedding-001")
        except Exception as e:
            logger.warning(f"Could not initialize GoogleGenerativeAiEmbeddingFunction: {e}. Falling back to default ONNX MiniLM embedding function.")
            
    # Default local lightweight embedding function
    return embedding_functions.DefaultEmbeddingFunction()
