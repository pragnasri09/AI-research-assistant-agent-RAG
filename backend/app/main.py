import os
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

# Enable CORS for frontend Vite dev server & deployed Vercel frontend
allowed_origins = [
    "https://frontend-beige-two-53.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

cors_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if cors_origins_env:
    for o in cors_origins_env.split(","):
        o_clean = o.strip()
        if o_clean and o_clean not in allowed_origins:
            allowed_origins.append(o_clean)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
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
