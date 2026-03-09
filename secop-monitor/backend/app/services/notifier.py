import logging
from datetime import datetime, timezone

import resend
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models.contract import Contract

logger = logging.getLogger(__name__)


def _format_cop(value: int | None) -> str:
    if value is None:
        return "No definido"
    return f"${value:,.0f} COP".replace(",", ".")


def _build_email_html(contract: Contract) -> str:
    secop_link = ""
    if contract.secop_url and "Login/Index" not in contract.secop_url:
        secop_link = f'<a href="{contract.secop_url}" style="color:#3b82f6;">Ver en SECOP</a>'

    return f"""
    <div style="font-family:system-ui,sans-serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#ededed;padding:24px;border-radius:8px;">
        <div style="border-bottom:2px solid #3b82f6;padding-bottom:16px;margin-bottom:16px;">
            <h2 style="margin:0;color:#3b82f6;">SECOP Monitor</h2>
            <p style="margin:4px 0 0;color:#a3a3a3;font-size:13px;">Nueva oportunidad detectada por DT Growth Partners</p>
        </div>

        <div style="background:#141414;border:1px solid #262626;border-radius:8px;padding:16px;margin-bottom:16px;">
            <div style="margin-bottom:12px;">
                <span style="background:#3b82f6;color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">
                    {contract.dt_service_category or "Sin categoria"}
                </span>
                <span style="background:#22c55e;color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;margin-left:8px;">
                    Score: {contract.relevance_score}/100
                </span>
            </div>

            <h3 style="margin:0 0 8px;color:#ededed;font-size:16px;">{contract.title}</h3>

            <table style="width:100%;font-size:14px;color:#a3a3a3;">
                <tr><td style="padding:4px 0;width:120px;"><strong>Entidad:</strong></td><td>{contract.entity_name or "N/A"}</td></tr>
                <tr><td style="padding:4px 0;"><strong>Ubicacion:</strong></td><td>{contract.city or ""}, {contract.department or ""}</td></tr>
                <tr><td style="padding:4px 0;"><strong>Valor:</strong></td><td style="color:#22c55e;font-weight:600;">{_format_cop(contract.estimated_value)}</td></tr>
                <tr><td style="padding:4px 0;"><strong>Modalidad:</strong></td><td>{contract.modality or "N/A"}</td></tr>
                <tr><td style="padding:4px 0;"><strong>Estado:</strong></td><td>{contract.status or "N/A"}</td></tr>
            </table>
        </div>

        <div style="background:#141414;border:1px solid #262626;border-radius:8px;padding:16px;margin-bottom:16px;">
            <p style="margin:0;font-size:14px;color:#a3a3a3;">
                <strong style="color:#ededed;">Por que es relevante:</strong><br>
                {contract.classification_reason or "Sin analisis disponible"}
            </p>
        </div>

        <div style="text-align:center;margin-top:16px;">
            {secop_link}
        </div>

        <p style="text-align:center;color:#525252;font-size:11px;margin-top:24px;">
            Alerta automatica de SECOP Monitor — DT Growth Partners
        </p>
    </div>
    """


async def notify_contract(contract: Contract) -> bool:
    """Send email alert for a relevant contract. Returns True on success."""
    if not settings.resend_api_key:
        logger.warning("Resend API key not configured — skipping notification")
        return False

    resend.api_key = settings.resend_api_key

    subject = f"Nueva oportunidad SECOP: {contract.title[:80]} — Score: {contract.relevance_score}/100"

    try:
        resend.Emails.send({
            "from": settings.alert_email_from,
            "to": [settings.alert_email_to],
            "subject": subject,
            "html": _build_email_html(contract),
        })
        logger.info("Notification sent for contract %s (score=%d)", contract.secop_id, contract.relevance_score)
        return True
    except Exception as exc:
        logger.error("Failed to send notification for %s: %s", contract.secop_id, exc)
        return False


async def notify_new_relevant_contracts() -> int:
    """Find relevant contracts that haven't been notified and send alerts.
    Returns count of notifications sent."""
    notified = 0

    async with async_session() as db:
        result = await db.execute(
            select(Contract)
            .where(
                Contract.is_relevant.is_(True),
                Contract.relevance_score >= settings.alert_threshold,
                Contract.notified_at.is_(None),
            )
            .order_by(Contract.relevance_score.desc())
            .limit(20)
        )
        contracts = list(result.scalars().all())

        if not contracts:
            return 0

        logger.info("Found %d contracts pending notification", len(contracts))

        for contract in contracts:
            success = await notify_contract(contract)
            if success:
                await db.execute(
                    update(Contract)
                    .where(Contract.id == contract.id)
                    .values(notified_at=datetime.utcnow())
                )
                notified += 1

        await db.commit()

    logger.info("Sent %d notifications", notified)
    return notified
