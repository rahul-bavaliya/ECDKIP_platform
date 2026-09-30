import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TenantBase(BaseModel):
    name: str
    tier: str = "standard"


class TenantCreate(TenantBase):
    pass


class TenantResponse(TenantBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
