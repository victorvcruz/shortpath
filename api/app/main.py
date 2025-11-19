import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.redis import redis_manager
from .services.cleanup import cleanup_service
from .routers.health import router as health_router
from .routers.graphs import router as graphs_router
from .routers.paths import router as paths_router
from .middleware.validation import setup_error_handlers, setup_middleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ShortPath API...")
    
    try:
        redis_manager.health_check()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    await cleanup_service.start_cleanup_task()
    logger.info("ShortPath API startup complete")
    
    yield
    
    logger.info("Shutting down ShortPath API...")
    await cleanup_service.stop_cleanup_task()
    redis_manager.close()
    logger.info("ShortPath API shutdown complete")

def create_app() -> FastAPI:
    app = FastAPI(
        title="ShortPath API",
        description="Public REST API for shortest path calculations in graphs",
        version="1.0.0",
        lifespan=lifespan
    )
    
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    if production_origins := os.getenv("CORS_ORIGINS"):
        allowed_origins.extend(production_origins.split(","))
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    setup_middleware(app)
    setup_error_handlers(app)
    
    app.include_router(health_router, tags=["system"])
    app.include_router(graphs_router)
    app.include_router(paths_router)
    
    @app.get("/", tags=["system"])
    async def root():
        return {
            "message": "ShortPath API",
            "version": "1.0.0",
            "description": "Public REST API for shortest path calculations in graphs"
        }
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
