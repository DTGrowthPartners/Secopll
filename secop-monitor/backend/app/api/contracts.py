import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractListResponse, ContractOut, ContractUpdate

router = APIRouter()


@router.get("", response_model=ContractListResponse)
async def list_contracts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    min_score: int = Query(0, ge=0, le=100),
    service_category: str | None = None,
    status: str | None = None,
    department: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    internal_status: str | None = None,
    search: str | None = None,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Contract)
    count_query = select(func.count(Contract.id))

    filters = []

    # By default, exclude contracts that are already awarded/closed
    EXCLUDED_STATUSES = ["Cerrado", "Celebrado", "Liquidado", "Terminado", "Adjudicado"]

    if min_score > 0:
        filters.append(Contract.relevance_score >= min_score)
    if service_category:
        filters.append(Contract.dt_service_category == service_category)
    if status:
        filters.append(Contract.status == status)
    else:
        # When no status filter specified, exclude awarded/closed contracts
        filters.append(~Contract.status.in_(EXCLUDED_STATUSES))
    if department:
        filters.append(Contract.department == department)
    if date_from:
        filters.append(Contract.published_at >= date_from)
    if date_to:
        filters.append(Contract.published_at <= date_to)
    if internal_status:
        filters.append(Contract.internal_status == internal_status)
    if source:
        filters.append(Contract.source == source)
    if search:
        search_filter = f"%{search}%"
        filters.append(
            Contract.title.ilike(search_filter) | Contract.description.ilike(search_filter)
        )

    for f in filters:
        query = query.where(f)
        count_query = count_query.where(f)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * limit
    query = query.order_by(Contract.published_at.desc(), Contract.relevance_score.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    contracts = result.scalars().all()

    return ContractListResponse(
        items=[ContractOut.model_validate(c) for c in contracts],
        total=total,
        page=page,
        pages=math.ceil(total / limit) if total > 0 else 0,
    )


@router.get("/{contract_id}", response_model=ContractOut)
async def get_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return ContractOut.model_validate(contract)


@router.patch("/{contract_id}", response_model=ContractOut)
async def update_contract(
    contract_id: str,
    body: ContractUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)

    await db.commit()
    await db.refresh(contract)
    return ContractOut.model_validate(contract)
