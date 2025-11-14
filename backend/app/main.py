"""
FastAPI application entry point.
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.api.routes import tests, optimizations, feedback
from core.database.client import supabase_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Network Analyzer API",
    description="API for network testing and AI-powered analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(tests.router)
app.include_router(optimizations.router)
app.include_router(feedback.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting AI Network Analyzer API")
    
    # Validate configuration
    try:
        settings.validate_required()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    # Test database connection
    if supabase_client.health_check():
        logger.info("Database connection healthy")
    else:
        logger.warning("Database connection check failed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down AI Network Analyzer API")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = supabase_client.health_check()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database_connected": db_healthy,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Network Analyzer API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.environment == "development" else "An error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
