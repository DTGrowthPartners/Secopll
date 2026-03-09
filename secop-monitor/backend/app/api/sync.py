import asyncio
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sync_log import SyncLog
from app.schemas.dashboard import SyncLogOut, SyncTriggerResponse
from app.services.secop_fetcher import sync_secop
from app.services.classifier import classify_contracts
from app.services.notifier import notify_new_relevant_contracts

router = APIRouter()


async def _run_full_sync(source: str):
    result = await sync_secop(source)
    prefiltered_ids = result.get("prefiltered_secop_ids", [])
    if prefiltered_ids:
        await classify_contracts(prefiltered_ids)
        await notify_new_relevant_contracts()


@router.post("/trigger", response_model=SyncTriggerResponse)
async def trigger_sync(source: str = "SECOP_II"):
    job_id = str(uuid.uuid4())
    asyncio.create_task(_run_full_sync(source))
    return SyncTriggerResponse(job_id=job_id)


@router.get("/status", response_model=SyncLogOut | None)
async def sync_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SyncLog).order_by(SyncLog.started_at.desc()).limit(1)
    )
    log = result.scalar_one_or_none()
    if not log:
        return None
    return SyncLogOut.model_validate(log)
