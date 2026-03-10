import asyncio
import json
import logging
from datetime import datetime, timezone
from functools import partial

from openai import OpenAI
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models.contract import Contract

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

SYSTEM_PROMPT = """
Eres un clasificador de contratos públicos colombianos del SECOP.
Tu tarea es evaluar si un contrato es una oportunidad de negocio para DT Growth Partners,
una agencia de marketing digital y tecnología que ofrece: Meta Ads, Desarrollo Web,
Automatizaciones con IA, Chatbots, Marketing Digital y Consultoría de Transformación Digital.

Dado el título y descripción de un contrato, responde SOLO con un JSON válido con esta estructura:
{
  "relevance_score": <número 0-100>,
  "primary_service": "<uno de: Meta Ads | Desarrollo Web | Automatizaciones & IA | Chatbot | Marketing Digital | Consultoría Digital | No relevante>",
  "service_tags": ["<servicio1>", "<servicio2>"],
  "reason": "<explicación breve en español de máximo 2 oraciones>"
}

Criterios de puntuación:
- 80-100: El contrato busca EXACTAMENTE lo que DT ofrece (ej: "contratar agencia de Meta Ads")
- 60-79: Hay alineación clara pero puede requerir adaptación (ej: "diseño publicitario y redes sociales")
- 40-59: Relación indirecta (ej: "comunicaciones institucionales con componente digital")
- 0-39: No es relevante para DT Growth Partners
"""


def _build_user_prompt(title: str, description: str | None) -> str:
    desc = description or "Sin descripción disponible"
    return f"Título: {title}\nDescripción: {desc}"


def _parse_ai_response(content: str) -> dict | None:
    try:
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse AI response: %s", content[:200])
        return None


def _classify_single_sync(client: OpenAI, title: str, description: str | None) -> dict | None:
    """Synchronous classification call — runs in a thread."""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(title, description)},
                ],
                temperature=0.1,
                max_tokens=300,
                timeout=30,
            )
            return _parse_ai_response(response.choices[0].message.content or "")
        except Exception as exc:
            if attempt < MAX_RETRIES - 1:
                import time
                wait = 2 ** (attempt + 1)
                logger.warning("OpenAI attempt %d failed: %s — retrying in %ds", attempt + 1, exc, wait)
                time.sleep(wait)
            else:
                logger.error("OpenAI classification failed after %d attempts: %s", MAX_RETRIES, exc)
                return None


async def classify_contracts(secop_ids: list[str]) -> int:
    """Classify contracts by their secop_ids. Returns count of classified contracts."""
    if not secop_ids:
        return 0

    client = OpenAI(api_key=settings.openai_api_key, max_retries=2, timeout=30)
    classified_count = 0

    async with async_session() as db:
        result = await db.execute(
            select(Contract).where(Contract.secop_id.in_(secop_ids))
        )
        contracts = list(result.scalars().all())

        for i, contract in enumerate(contracts):
            ai_result = await asyncio.to_thread(
                _classify_single_sync, client, contract.title, contract.description
            )

            if ai_result is None:
                logger.warning("Classification returned None for %s", contract.secop_id)
                continue

            score = ai_result.get("relevance_score", 0)
            is_relevant = score >= settings.relevance_threshold

            await db.execute(
                update(Contract)
                .where(Contract.id == contract.id)
                .values(
                    relevance_score=score,
                    dt_service_category=ai_result.get("primary_service"),
                    dt_service_tags=ai_result.get("service_tags", []),
                    classification_reason=ai_result.get("reason"),
                    is_relevant=is_relevant,
                    updated_at=datetime.utcnow(),
                )
            )
            classified_count += 1

            if (i + 1) % 10 == 0:
                await db.commit()
                logger.info("Classified %d/%d contracts", i + 1, len(contracts))

        await db.commit()

    logger.info("Classification complete: %d/%d contracts classified", classified_count, len(secop_ids))
    return classified_count


async def classify_unclassified(limit: int = 200) -> int:
    """Find and classify contracts that passed prefilter but haven't been classified yet."""
    async with async_session() as db:
        result = await db.execute(
            select(Contract.secop_id)
            .where(Contract.relevance_score == 0, Contract.classification_reason.is_(None))
            .order_by(Contract.created_at.desc())
            .limit(limit)
        )
        secop_ids = list(result.scalars().all())

    if not secop_ids:
        logger.info("No unclassified contracts found")
        return 0

    logger.info("Found %d unclassified contracts", len(secop_ids))
    return await classify_contracts(secop_ids)
