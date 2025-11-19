
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from ..database.redis import redis_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", summary="Basic health check")
async def get_health():

    return {
        "status": "healthy",
        "service": "shortpath-api",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/detailed", summary="Detailed health check")
async def get_detailed_health():

    redis_status = "ok"
    redis_error = None
    try:
        redis_manager.health_check()
    except Exception as e:
        redis_status = "error"
        redis_error = str(e)
        logger.error(f"Detailed health check failed for Redis: {e}")

    overall_status = "ok" if redis_status == "ok" else "degraded"
    if overall_status == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": overall_status,
                "services": {
                    "redis": {"status": redis_status, "error": redis_error}
                }
            }
        )

    return {
        "status": overall_status,
        "services": {
            "redis": {"status": redis_status, "error": redis_error}
        }
    }

@router.get("/health/ready", summary="Readiness probe")
async def get_readiness():

    try:
        redis_manager.health_check()
        return {"status": "ready"}
    except Exception as e:
        logger.warning(f"Readiness probe failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready: Redis connection failed"
        )

@router.get("/health/live", summary="Liveness probe")
async def get_liveness():

    return {"status": "live"}