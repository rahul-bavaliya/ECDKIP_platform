import uuid

from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import ConflictException, NotFoundException
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    @staticmethod
    async def create_tenant(db: AsyncSession, tenant_in: TenantCreate) -> Tenant:
        existing: Result[*tuple[Tenant, ...]] = await db.execute(
            statement=select(Tenant).where(Tenant.name == tenant_in.name)
        )
        if existing.scalars().first():
            raise ConflictException(message="Tenant with this name already exists")

        tenant: Tenant = Tenant(name=tenant_in.name, email=tenant_in.email)
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
        result: Result[*tuple[Tenant, ...]] = await db.execute(
            statement=select(Tenant).offset(offset=skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_tenant(
        db: AsyncSession, tenant_id: uuid.UUID, tenant_in: TenantUpdate
    ) -> Tenant:
        tenant: Tenant = await TenantService.get_tenant_by_id(
            db=db, tenant_id=tenant_id
        )

        update_data: dict[str, any] = tenant_in.model_dump(exclude_unset=True)

        if "name" in update_data:
            existing: Result[*tuple[Tenant, ...]] = await db.execute(
                statement=select(Tenant).where(Tenant.name == update_data["name"])
            )
            if existing.scalars().first():
                raise ConflictException(message="Tenant with this name already exists")

        for field, value in update_data.items():
            setattr(tenant, field, value)

        await db.commit()
        await db.refresh(instance=tenant)
        return tenant
