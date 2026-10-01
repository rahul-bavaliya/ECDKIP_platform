import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TenantBase(BaseModel):
    name: str = Field(
        default=...,
        description="The official legal or corporate name of the organization account.",
        examples=["Acme Corporation"],
    )
    email: EmailStr = Field(
        default=...,
        description="Email Address.",
        examples=["example@test.com"],
    )


class TenantCreate(TenantBase):
    pass


# ==============================================================================
# 💡 Fixed: Tenant Update Schema (Fields now default to None for optional patching)
# ==============================================================================
class TenantUpdate(BaseModel):
    """Schema used to apply partial updates to a tenant. All fields are optional."""

    name: str | None = Field(
        default=None,
        description="The official legal or corporate name of the organization account.",
        examples=["Acme Corporation"],
    )
    email: EmailStr | None = Field(
        default=None,
        description="Email Address.",
        examples=["example@test.com"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "updated-test@test.com"  # Clean view showing a partial patch request body
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
                "email": "example@test.com",
                "created_at": "2026-09-30T14:00:00Z",
                "updated_at": None,
            }
        },
    )
