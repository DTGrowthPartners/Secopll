import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    secop_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(10), nullable=False)

    entity_name: Mapped[str | None] = mapped_column(String(500))
    entity_nit: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    contract_type: Mapped[str | None] = mapped_column(String(200))
    modality: Mapped[str | None] = mapped_column(String(200))
    estimated_value: Mapped[int | None] = mapped_column(BigInteger)
    duration_days: Mapped[int | None] = mapped_column(Integer)

    status: Mapped[str | None] = mapped_column(String(100))
    phase: Mapped[str | None] = mapped_column(String(100))

    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    secop_url: Mapped[str | None] = mapped_column(Text)
    category_code: Mapped[str | None] = mapped_column(String(50))

    # AI classification fields
    relevance_score: Mapped[int] = mapped_column(Integer, default=0)
    dt_service_category: Mapped[str | None] = mapped_column(String(100))
    dt_service_tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    classification_reason: Mapped[str | None] = mapped_column(Text)
    is_relevant: Mapped[bool] = mapped_column(Boolean, default=False)

    # Internal management fields
    internal_status: Mapped[str] = mapped_column(String(50), default="new")
    assigned_to: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
