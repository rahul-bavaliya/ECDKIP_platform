import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantBase(BaseModel):
    name: str = Field(
        ...,
        description="The official legal or corporate name of the organization account.",
        examples=["Acme Corporation"],  # 💡 Clean, realistic string example
    )
    tier: str = Field(
        default="standard",
        description="The operational subscription tier determining system rate-limits and access.",
        examples=["premium"],  # 💡 Realistic production tier variant
    )


class TenantCreate(TenantBase):
    pass


class TenantResponse(TenantBase):
    id: uuid.UUID = Field(
        ...,
        description="The immutable, globally unique identifier assigned to the tenant.",
        examples=[
            "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
        ],  # 💡 MUST be a valid 36-character UUID string
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="The ISO 8601 UTC timestamp recording exactly when the workspace was initialized.",
        examples=["2026-09-30T14:00:00Z"],  # 💡 Formatted ISO standard representation
    )

    # Combines field examples into a beautiful, cohesive structural fallback schema
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "name": "Acme Corporation",
                "tier": "premium",
                "created_at": "2026-09-30T14:00:00Z",
            }
        },
    )
