import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from structlog._generic import BoundLogger

from app.api.v1.endpoints.tenants import router as tenants_router

# 💡 Direct file imports since subdirectories don't contain __init__.py files
# Ensure these files exist as: app/api/v1/tenants.py and app/api/v1/users.py
from app.core import get_logger
from app.core.database import get_db
from app.schemas.response import ResponseEnvelope

router = APIRouter()
logger: BoundLogger = get_logger()

# ==============================================================================
# Dynamic Route Matrix Loading / Unloading Block
# ==============================================================================

""" Start Loading Module Pipeline: Tenant Endpoints Enabled"""
router.include_router(tenants_router, prefix="/tenants")
""" End Loading Module Pipeline"""
# ==============================================================================
# Core System Base Endpoints
# ==============================================================================


@router.get(path="/", tags=["Root"])
async def root():
    """Root entry point displaying API gateway index metadata."""
    return ResponseEnvelope.success_response(
        data={
            "message": "Welcome to the Enterprise Cloud Document & Knowledge Intelligence Platform API",
            "docs_url": "/docs",
            "health_endpoint": "/api/v1/health",
            "modules_loaded": {
                "tenants": True if tenants_router is not None else False,
            },
        },
        message="Endpoint working confimation.",
    )


@router.get(path="/health", tags=["System"])
async def health_check(db: AsyncSession = Depends(dependency=get_db)):
    """Comprehensive health check verifying operational state and live database loops."""
    start_time: float = time.perf_counter()
    db_status = "connected"

    try:
        await db.execute(statement=text(text="SELECT 1"))
    except Exception as db_error:
        db_status = f"disconnected: {db_error!s}"
        logger.error("Database health loop down", error=str(object=db_error))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "degraded", "database": db_status},
        )

    return ResponseEnvelope.success_response(
        data={
            "status": "healthy",
            "service": "ecdkip-backend",
            "database": db_status,
            "api_status": "up",
        },
        message="Endpoint working confimation.",
    )
