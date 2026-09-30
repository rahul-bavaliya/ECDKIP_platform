import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.tenants import router as tenants_router

# 💡 Direct file imports since subdirectories don't contain __init__.py files
# Ensure these files exist as: app/api/v1/tenants.py and app/api/v1/users.py
from app.api.v1.endpoints.users import router as users_router
from app.core import get_logger
from app.core.config import settings  # Import configuration toggles
from app.core.database import get_db

router = APIRouter()
logger = get_logger()

# ==============================================================================
# Dynamic Route Matrix Loading / Unloading Block
# ==============================================================================

logger.info("Loading Module Pipeline: Tenant Endpoints Enabled")
router.include_router(tenants_router, prefix="/tenants", tags=["Tenants"])
router.include_router(users_router, prefix="/users", tags=["Users"])

# ==============================================================================
# Core System Base Endpoints
# ==============================================================================


@router.get("/", tags=["Root"])
async def root():
    """Root entry point displaying API gateway index metadata."""
    return {
        "message": "Welcome to the Enterprise Cloud Document & Knowledge Intelligence Platform API",
        "docs_url": "/docs",
        "health_endpoint": "/api/v1/health",
        "modules_loaded": {
            "tenants": settings.enable_tenant_endpoints,
            "users": settings.enable_user_endpoints,
        },
    }


@router.get("/health", tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check verifying operational state and live database loops."""
    start_time = time.perf_counter()
    db_status = "connected"

    try:
        await db.execute(text("SELECT 1"))
    except Exception as db_error:
        db_status = f"disconnected: {db_error!s}"
        logger.error("Database health loop down", error=str(db_error))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "degraded", "database": db_status},
        )

    return {
        "status": "healthy",
        "service": "ecdkip-backend",
        "database": db_status,
        "api_status": "up",
    }
