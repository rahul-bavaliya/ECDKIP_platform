import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantBase(BaseModel):
    name: str = Field(
        default=...,
        description="The official legal or corporate name of the organization account.",
        examples=["Acme Corporation"],
    )
    tier: str = Field(
        default="standard",
        description="The operational subscription tier determining system rate-limits and access.",
        examples=["premium"],
    )


class TenantCreate(TenantBase):
    pass


# ==============================================================================
# 💡 New: Tenant Update Schema
# ==============================================================================
class TenantUpdate(BaseModel):
    """Schema used to apply partial updates to a tenant. All fields are optional."""

    name: str | None = Field(
        default=None,
        description="Update the official corporate name of the organization.",
        examples=["Acme Globally Inc."],
    )
    tier: str | None = Field(
        default=None,
        description="Upgrade or downgrade the operational subscription tier.",
        examples=["enterprise"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tier": "enterprise"  # Clean view showing a partial patch request body
            }
        }
    )


class TenantResponse(TenantBase):
    id: uuid.UUID = Field(
        default=...,
        description="The immutable, globally unique identifier assigned to the tenant.",
        examples=["9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"],
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="The ISO 8601 UTC timestamp recording exactly when the workspace was initialized.",
        examples=["2026-09-30T14:00:00Z"],
    )
    # 💡 Added explicit optional updated_at field to match your perfect DB model layout
    updated_at: datetime | None = Field(
        default=None,
        description="The ISO 8601 UTC timestamp showing when a record was updated. Remains null until modified.",
        examples=["2026-09-30T16:45:00Z"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "name": "Acme Corporation",
                "tier": "premium",
                "created_at": "2026-09-30T14:00:00Z",
                "updated_at": None,
            }
        },
    )
