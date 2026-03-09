from fastapi import APIRouter, Depends
from sqlalchemy import select, func, case, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contract import Contract
from app.models.sync_log import SyncLog
from app.schemas.dashboard import DashboardStats, PipelineStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(Contract.id)))
    total_contracts = total_result.scalar_one()

    relevant_result = await db.execute(
        select(func.count(Contract.id)).where(Contract.is_relevant.is_(True))
    )
    relevant_contracts = relevant_result.scalar_one()

    new_week_result = await db.execute(
        select(func.count(Contract.id)).where(
            Contract.is_relevant.is_(True),
            Contract.created_at >= func.now() - text("interval '7 days'"),
        )
    )
    new_this_week = new_week_result.scalar_one()

    value_result = await db.execute(
        select(func.coalesce(func.sum(Contract.estimated_value), 0)).where(
            Contract.is_relevant.is_(True)
        )
    )
    total_value_cop = value_result.scalar_one()

    service_result = await db.execute(
        select(Contract.dt_service_category, func.count(Contract.id))
        .where(Contract.is_relevant.is_(True), Contract.dt_service_category.isnot(None))
        .group_by(Contract.dt_service_category)
    )
    by_service = {row[0]: row[1] for row in service_result.all()}

    dept_result = await db.execute(
        select(Contract.department, func.count(Contract.id))
        .where(Contract.is_relevant.is_(True), Contract.department.isnot(None))
        .group_by(Contract.department)
        .order_by(func.count(Contract.id).desc())
        .limit(15)
    )
    by_department = {row[0]: row[1] for row in dept_result.all()}

    pipeline_result = await db.execute(
        select(
            func.count(case((Contract.internal_status == "new", 1))),
            func.count(case((Contract.internal_status == "reviewing", 1))),
            func.count(case((Contract.internal_status == "applied", 1))),
            func.count(case((Contract.internal_status == "discarded", 1))),
        ).where(Contract.is_relevant.is_(True))
    )
    p = pipeline_result.one()

    sync_result = await db.execute(
        select(SyncLog.finished_at)
        .where(SyncLog.status == "success")
        .order_by(SyncLog.finished_at.desc())
        .limit(1)
    )
    last_sync = sync_result.scalar_one_or_none()

    return DashboardStats(
        total_contracts=total_contracts,
        relevant_contracts=relevant_contracts,
        new_this_week=new_this_week,
        total_value_cop=total_value_cop,
        by_service=by_service,
        by_department=by_department,
        last_sync=last_sync,
        pipeline=PipelineStats(new=p[0], reviewing=p[1], applied=p[2], discarded=p[3]),
    )
