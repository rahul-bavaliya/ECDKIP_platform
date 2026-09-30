import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.tenant import Tenant
from app.schemas.response import ResponseEnvelope

# 💡 Assuming you add TenantUpdate schema next
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.services.tenant import TenantService

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post(
    path="/",
    response_model=ResponseEnvelope[TenantResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_tenant(
    tenant_in: TenantCreate, db: AsyncSession = Depends(dependency=get_db)
):
    tenant: Tenant = await TenantService.create_tenant(db=db, tenant_in=tenant_in)
    return ResponseEnvelope.success_response(
        data=TenantResponse.model_validate(tenant),
        message="Tenant created successfully",
    )


@router.get(path="/", response_model=ResponseEnvelope[list[TenantResponse]])
async def list_tenants(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(dependency=get_db)
):
    tenants: list[Tenant] = await TenantService.list_tenants(
        db=db, skip=skip, limit=limit
    )
    tenant_responses: list[TenantResponse] = [
        TenantResponse.model_validate(obj=t) for t in tenants
    ]
    return ResponseEnvelope.success_response(
        data=tenant_responses, message="Tenants retrieved successfully"
    )


@router.get(path="/{tenant_id}", response_model=ResponseEnvelope[TenantResponse])
async def get_tenant(
    tenant_id: uuid.UUID, db: AsyncSession = Depends(dependency=get_db)
):
    tenant: Tenant = await TenantService.get_tenant_by_id(db=db, tenant_id=tenant_id)
    return ResponseEnvelope.success_response(
        data=TenantResponse.model_validate(obj=tenant),
        message="Tenant retrieved successfully",
    )


# ==============================================================================
# 💡 New: Update Tenant Endpoint
# ==============================================================================
@router.patch(path="/{tenant_id}", response_model=ResponseEnvelope[TenantResponse])
async def update_tenant(
    tenant_id: uuid.UUID,
    tenant_in: TenantUpdate,
    db: AsyncSession = Depends(dependency=get_db),
):
    """Partially update an existing tenant's properties (e.g. name or tier)."""
    tenant: Tenant = await TenantService.update_tenant(
        db=db, tenant_id=tenant_id, tenant_in=tenant_in
    )
    return ResponseEnvelope.success_response(
        data=TenantResponse.model_validate(obj=tenant),
        message="Tenant updated successfully",
    )


# ==============================================================================
# 💡 New: Delete Tenant Endpoint
# ==============================================================================
@router.delete(path="/{tenant_id}", response_model=ResponseEnvelope[dict])
async def delete_tenant(tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Permanently delete a tenant workspace and clear its metadata properties."""
    await TenantService.delete_tenant(db=db, tenant_id=tenant_id)
    return ResponseEnvelope.success_response(
        data={"id": str(object=tenant_id)},
        message="Tenant deleted successfully",
    )
