import json
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models.contract import Contract
from app.models.sync_log import SyncLog
from app.utils.keywords import passes_prefilter

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
MAX_RETRIES = 3
BACKOFF_BASE = 2


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.replace(tzinfo=None)
    except (ValueError, AttributeError):
        return None


def _parse_int(value: str | int | float | None) -> int | None:
    if value is None:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _extract_url(urlproceso: str | dict | None) -> str | None:
    if not urlproceso:
        return None
    if isinstance(urlproceso, dict):
        return urlproceso.get("url")
    try:
        parsed = json.loads(urlproceso)
        if isinstance(parsed, dict):
            return parsed.get("url")
    except (json.JSONDecodeError, TypeError):
        pass
    return str(urlproceso) if urlproceso else None


def _normalize_duration(duration: str | None, unit: str | None) -> int | None:
    days = _parse_int(duration)
    if days is None:
        return None
    unit_upper = (unit or "").upper()
    if "MES" in unit_upper:
        return days * 30
    if "AÑO" in unit_upper or "ANO" in unit_upper or "YEAR" in unit_upper:
        return days * 365
    return days


def _should_skip(record: dict, source: str) -> bool:
    """Skip contracts with value 0 and closed status."""
    if source == "SECOP_II":
        value = _parse_int(record.get("precio_base"))
        status = (record.get("estado_de_apertura_del_proceso") or "").upper()
        if value == 0 and status == "CERRADO":
            return True
    elif source == "SECOP_I":
        value = _parse_int(record.get("valor_del_contrato"))
        status = (record.get("estado_contrato") or "").upper()
        if value == 0 and "CERRADO" in status:
            return True
    return False


def _map_secop_ii(record: dict) -> dict:
    return {
        "secop_id": record.get("id_del_proceso", record.get("referencia_del_proceso", "")),
        "source": "SECOP_II",
        "entity_name": record.get("entidad"),
        "entity_nit": record.get("nit_entidad"),
        "department": record.get("departamento_entidad"),
        "city": record.get("ciudad_entidad"),
        "title": record.get("nombre_del_procedimiento", ""),
        "description": record.get("descripci_n_del_procedimiento"),
        "contract_type": record.get("tipo_de_contrato"),
        "modality": record.get("modalidad_de_contratacion"),
        "estimated_value": _parse_int(record.get("precio_base")),
        "duration_days": _normalize_duration(record.get("duracion"), record.get("unidad_de_duracion")),
        "status": record.get("estado_de_apertura_del_proceso"),
        "phase": record.get("fase"),
        "published_at": _parse_datetime(record.get("fecha_de_publicacion_del")),
        "deadline_at": _parse_datetime(record.get("fecha_de_recepcion_de")),
        "last_updated_at": _parse_datetime(record.get("fecha_de_ultima_publicaci")),
        "secop_url": _extract_url(record.get("urlproceso")),
        "category_code": record.get("codigo_principal_de_categoria"),
    }


def _map_secop_i(record: dict) -> dict:
    return {
        "secop_id": record.get("id_del_proceso", record.get("proceso_de_compra", "")),
        "source": "SECOP_I",
        "entity_name": record.get("nombre_entidad"),
        "entity_nit": record.get("nit_entidad"),
        "department": record.get("departamento"),
        "city": record.get("ciudad"),
        "title": record.get("objeto_del_contrato", ""),
        "description": record.get("detalle_del_objeto_a_contratar"),
        "contract_type": record.get("tipo_de_contrato"),
        "modality": record.get("modalidad_de_contratacion"),
        "estimated_value": _parse_int(record.get("valor_del_contrato")),
        "duration_days": None,
        "status": record.get("estado_contrato"),
        "phase": None,
        "published_at": _parse_datetime(record.get("fecha_de_inicio_del_contrato")),
        "deadline_at": None,
        "last_updated_at": _parse_datetime(record.get("ultima_actualizacion")),
        "secop_url": _extract_url(record.get("urlproceso")),
        "category_code": None,
    }


async def _fetch_page(
    client: httpx.AsyncClient,
    url: str,
    params: dict,
) -> list[dict]:
    """Fetch a single page from the SECOP API with exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = await client.get(url, params=params, timeout=30.0)
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            wait = BACKOFF_BASE ** (attempt + 1)
            logger.warning("SECOP API attempt %d failed: %s — retrying in %ds", attempt + 1, exc, wait)
            if attempt == MAX_RETRIES - 1:
                raise
            import asyncio
            await asyncio.sleep(wait)
    return []


async def _get_last_sync_timestamp(db: AsyncSession, source: str) -> datetime | None:
    result = await db.execute(
        select(SyncLog.finished_at)
        .where(SyncLog.source == source, SyncLog.status == "success")
        .order_by(SyncLog.finished_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    return row


async def _upsert_contracts(db: AsyncSession, contracts_data: list[dict]) -> tuple[int, int]:
    """Upsert contracts into DB using bulk insert. Returns (new_count, updated_count)."""
    if not contracts_data:
        return 0, 0

    # Deduplicate by secop_id within the batch (keep last occurrence)
    seen: dict[str, int] = {}
    for i, c in enumerate(contracts_data):
        seen[c["secop_id"]] = i
    contracts_data = [contracts_data[i] for i in sorted(seen.values())]

    stmt = pg_insert(Contract).values(contracts_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["secop_id"],
        set_={
            "entity_name": stmt.excluded.entity_name,
            "department": stmt.excluded.department,
            "city": stmt.excluded.city,
            "title": stmt.excluded.title,
            "description": stmt.excluded.description,
            "contract_type": stmt.excluded.contract_type,
            "modality": stmt.excluded.modality,
            "estimated_value": stmt.excluded.estimated_value,
            "duration_days": stmt.excluded.duration_days,
            "status": stmt.excluded.status,
            "phase": stmt.excluded.phase,
            "published_at": stmt.excluded.published_at,
            "deadline_at": stmt.excluded.deadline_at,
            "last_updated_at": stmt.excluded.last_updated_at,
            "secop_url": stmt.excluded.secop_url,
            "category_code": stmt.excluded.category_code,
            "updated_at": datetime.utcnow(),
        },
    )
    result = await db.execute(stmt)
    await db.commit()

    total = result.rowcount or len(contracts_data)
    return total, 0


async def sync_secop(source: str = "SECOP_II") -> dict:
    """Main sync function for a given SECOP source."""
    is_secop_ii = source == "SECOP_II"
    base_url = settings.secop_ii_url if is_secop_ii else settings.secop_i_url
    mapper = _map_secop_ii if is_secop_ii else _map_secop_i
    date_field = "fecha_de_ultima_publicaci" if is_secop_ii else "ultima_actualizacion"

    async with async_session() as db:
        sync_log = SyncLog(source=source, status="running")
        db.add(sync_log)
        await db.commit()
        await db.refresh(sync_log)

        try:
            last_sync = await _get_last_sync_timestamp(db, source)
            if last_sync is None:
                last_sync = datetime.utcnow() - timedelta(days=settings.backfill_days)
                logger.info("No previous sync for %s — backfilling %d days", source, settings.backfill_days)

            last_sync_str = last_sync.strftime("%Y-%m-%dT%H:%M:%S")
            where_clause = f"{date_field} > '{last_sync_str}'"

            total_fetched = 0
            total_new = 0
            total_updated = 0
            offset = 0
            prefiltered: list[dict] = []

            async with httpx.AsyncClient() as client:
                while True:
                    params = {
                        "$where": where_clause,
                        "$order": f"{date_field} DESC",
                        "$limit": BATCH_SIZE,
                        "$offset": offset,
                    }

                    logger.info("Fetching %s offset=%d", source, offset)
                    records = await _fetch_page(client, base_url, params)

                    if not records:
                        break

                    total_fetched += len(records)
                    batch_to_upsert: list[dict] = []

                    for record in records:
                        if _should_skip(record, source):
                            continue

                        mapped = mapper(record)
                        if not mapped["secop_id"] or not mapped["title"]:
                            continue

                        passed, _matches = passes_prefilter(mapped["title"], mapped["description"])
                        if passed:
                            prefiltered.append(mapped)

                        batch_to_upsert.append(mapped)

                    new_count, updated_count = await _upsert_contracts(db, batch_to_upsert)
                    total_new += new_count
                    total_updated += updated_count

                    if len(records) < BATCH_SIZE:
                        break

                    offset += BATCH_SIZE

            sync_log.records_fetched = total_fetched
            sync_log.records_new = total_new
            sync_log.records_updated = total_updated
            sync_log.status = "success"
            sync_log.finished_at = datetime.utcnow()
            await db.commit()

            logger.info(
                "Sync %s completed: fetched=%d, new=%d, updated=%d, prefiltered=%d",
                source, total_fetched, total_new, total_updated, len(prefiltered),
            )

            return {
                "source": source,
                "fetched": total_fetched,
                "new": total_new,
                "updated": total_updated,
                "prefiltered_for_ai": len(prefiltered),
                "prefiltered_secop_ids": [c["secop_id"] for c in prefiltered],
            }

        except Exception as exc:
            logger.exception("Sync %s failed: %s", source, exc)
            sync_log.status = "error"
            sync_log.error_message = str(exc)[:2000]
            sync_log.finished_at = datetime.utcnow()
            await db.commit()
            raise


async def sync_secop_ii() -> dict:
    return await sync_secop("SECOP_II")


async def sync_secop_i() -> dict:
    return await sync_secop("SECOP_I")
