import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import ConflictException, NotFoundException
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate


class TenantService:
    @staticmethod
    async def create_tenant(db: AsyncSession, tenant_in: TenantCreate) -> Tenant:
        # Check if tenant already exists
        existing = await db.execute(select(Tenant).where(Tenant.name == tenant_in.name))
        if existing.scalars().first():
            raise ConflictException(message="Tenant with this name already exists")

        tenant = Tenant(name=tenant_in.name, tier=tenant_in.tier)
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        return tenant

    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
        tenant = await db.get(Tenant, tenant_id)
        if not tenant:
            raise NotFoundException(message="Tenant not found")
        return tenant

    @staticmethod
    async def list_tenants(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Tenant]:
        result = await db.execute(select(Tenant).offset(skip).limit(limit))
        return result.scalars().all()
