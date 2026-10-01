import uuid
from datetime import datetime  # 💡 Added timezone import here

from pydantic import EmailStr
from sqlalchemy import TIMESTAMP, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# 💡 2. Change BaseModel to Base here
class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # ✅ Mandatory: Database enforces NOT NULL constraint
    name: Mapped[str] = mapped_column(String(length=255), unique=False, nullable=False)

    # ✅ Mandatory: Database enforces NOT NULL constraint, uniqueness, and indexes it
    email: Mapped[EmailStr] = mapped_column(
        String(length=255),
        unique=True,
        index=True,
        nullable=False,
    )

    # 💡 Force TIMESTAMPTZ datatype mapping
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # 💡 When this runs, it will now locate the timezone package perfectly
    updated_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        onupdate=func.now(),
    )
