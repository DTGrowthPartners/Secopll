from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PipelineStats(BaseModel):
    new: int = 0
    reviewing: int = 0
    applied: int = 0
    discarded: int = 0


class DashboardStats(BaseModel):
    total_contracts: int = 0
    relevant_contracts: int = 0
    new_this_week: int = 0
    total_value_cop: int = 0
    by_service: dict[str, int] = {}
    by_department: dict[str, int] = {}
    last_sync: datetime | None = None
    pipeline: PipelineStats = PipelineStats()


class SyncLogOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    source: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    records_fetched: int = 0
    records_new: int = 0
    records_updated: int = 0
    status: str | None = None
    error_message: str | None = None


class SyncTriggerResponse(BaseModel):
    job_id: str
    message: str = "Sincronizacion iniciada"
