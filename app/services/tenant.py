import uuid

from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import ConflictException, NotFoundException
from app.models.tenant import Tenant
from app.schemas.tenant import (  # 💡 Added TenantUpdate import
    TenantCreate,
    TenantUpdate,
)


class TenantService:
    @staticmethod
    async def create_tenant(db: AsyncSession, tenant_in: TenantCreate) -> Tenant:
        # Check if tenant already exists
        existing: Result[Tenant] = await db.execute(
            statement=select(Tenant).where(Tenant.name == tenant_in.name)
        )
        if existing.scalars().first():
            raise ConflictException(message="Tenant with this name already exists")

        tenant = Tenant(name=tenant_in.name, tier=tenant_in.tier)
        db.add(instance=tenant)
        await db.commit()
        await db.refresh(instance=tenant)
        return tenant

    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
        tenant: Tenant | None = await db.get(entity=Tenant, ident=tenant_id)
        if not tenant:
            raise NotFoundException(message="Tenant not found")
        return tenant

    @staticmethod
    async def list_tenants(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Tenant]:
        result: Result[Tenant] = await db.execute(
            statement=select(Tenant).offset(offset=skip).limit(limit)
        )
        return result.scalars().all()

    # ==============================================================================
    # 💡 New: Update Tenant Service Logic
    # ==============================================================================
    @staticmethod
    async def update_tenant(
        db: AsyncSession, tenant_id: uuid.UUID, tenant_in: TenantUpdate
    ) -> Tenant:
        """Fetches an existing tenant and dynamically applies partial updates."""
        # 1. Fetch the tenant or let it raise a NotFoundException
        tenant: Tenant = await TenantService.get_tenant_by_id(
            db=db, tenant_id=tenant_id
        )

        # 2. Extract only the fields explicitly passed in the request body
        # 💡 Using exclude_unset=True ensures we don't overwrite values with None
        update_data = tenant_in.model_dump(exclude_unset=True)

        # 3. Check for unique naming conflicts if a name change is requested
        if "name" in update_data and update_data["name"] != tenant.name:
            existing: Result[Tenant] = await db.execute(
                statement=select(Tenant).where(Tenant.name == update_data["name"])
            )
            if existing.scalars().first():
                raise ConflictException(message="Tenant with this name already exists")

        # 4. Safely apply attributes to the tracked database model instance
        for field, value in update_data.items():
            setattr(tenant, field, value)

        # 5. Commit the changes over the active connection pool wire
        db.add(instance=tenant)
        await db.commit()
        await db.refresh(instance=tenant)
        return tenant

    # ==============================================================================
    # 💡 New: Delete Tenant Service Logic
    # ==============================================================================
    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> None:
        """Removes a tenant record or raises a NotFoundException if it does not exist."""
        tenant: Tenant = await TenantService.get_tenant_by_id(
            db=db, tenant_id=tenant_id
        )

        await db.delete(instance=tenant)
        await db.commit()
