import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.database import init_db
from app.api.research import router as research_router
from app.api.history import router as history_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SQLite database...")
    init_db()
    logger.info(f"{settings.PROJECT_NAME} backend started successfully.")
    yield
    logger.info("Shutting down backend server.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous AI Research Assistant Agent API powered by LangGraph & RAG",
    lifespan=lifespan
)

# Enable CORS for frontend Vite dev server & production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(history_router)
app.include_router(research_router)

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint displaying system status and API configuration status."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "tavily_configured": bool(settings.TAVILY_API_KEY),
        "search_mode": "Live Tavily Web Search" if settings.TAVILY_API_KEY else "Mock Search Engine (Offline Fallback)"
    }
