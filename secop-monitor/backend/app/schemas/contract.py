from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    secop_id: str
    source: str

    entity_name: str | None = None
    entity_nit: str | None = None
    department: str | None = None
    city: str | None = None

    title: str
    description: str | None = None
    contract_type: str | None = None
    modality: str | None = None
    estimated_value: int | None = None
    duration_days: int | None = None

    status: str | None = None
    phase: str | None = None

    published_at: datetime | None = None
    deadline_at: datetime | None = None
    last_updated_at: datetime | None = None

    secop_url: str | None = None
    category_code: str | None = None

    relevance_score: int = 0
    dt_service_category: str | None = None
    dt_service_tags: list[str] | None = None
    classification_reason: str | None = None
    is_relevant: bool = False

    internal_status: str = "new"
    assigned_to: str | None = None
    notes: str | None = None
    notified_at: datetime | None = None

    created_at: datetime
    updated_at: datetime


class ContractUpdate(BaseModel):
    internal_status: str | None = None
    assigned_to: str | None = None
    notes: str | None = None


class ContractListResponse(BaseModel):
    items: list[ContractOut]
    total: int
    page: int
    pages: int
