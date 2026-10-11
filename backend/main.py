import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.logger import get_logger
from backend.routes.clients import router as clients_router
from backend.routes.analysis import router as analysis_router
from backend.routes.checkpoint import router as checkpoint_router
from backend.routes.memory import router as memory_router

logger = get_logger("FastAPIApp")

app = FastAPI(
    title="Wealth Advisor Assistant API",
    description="Multi-agent institutional wealth advisory system powered by LangGraph & Gemini.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(clients_router)
app.include_router(analysis_router)
app.include_router(checkpoint_router)
app.include_router(memory_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Wealth Advisor Assistant Agent System",
        "gemini_model": settings.gemini_model,
        "gemini_api_key_configured": bool(settings.gemini_api_key)
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Wealth Advisor Assistant backend on {settings.backend_host}:{settings.backend_port}")
    uvicorn.run("backend.main:app", host=settings.backend_host, port=settings.backend_port, reload=True)
