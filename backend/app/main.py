"""FastAPI application factory — registers routers, middleware, and lifecycle events."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import get_settings
from app.models.schemas import HealthResponse
from app.routers import chat, documents, mcq, summary
from app.services.embedding_service import get_embedding_model
from app.services.llm_service import check_llm_available
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: warm up embedding model. Shutdown: nothing needed."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    try:
        get_embedding_model()  # load model into memory at startup
        logger.info("Embedding model warmed up")
    except Exception as e:
        logger.warning(f"Embedding model warmup failed: {e}")
    yield
    logger.info("Shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Production-ready RAG API for academic PDF Q&A with citations, summaries, and MCQ generation.",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(documents.router)
    app.include_router(chat.router)
    app.include_router(summary.router)
    app.include_router(mcq.router)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Service health check — verifies embedding model and LLM availability."""
        return HealthResponse(
            status="ok",
            version=settings.app_version,
            services={
                "embedding_model": settings.embedding_model,
                "llm": settings.gemini_model,
                "llm_configured": check_llm_available(),
            },
        )

    @app.get("/", tags=["Health"])
    async def root():
        return {"message": f"Welcome to {settings.app_name} API", "docs": "/docs"}

    return app


app = create_app()
