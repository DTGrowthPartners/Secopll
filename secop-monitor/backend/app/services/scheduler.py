import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _run_sync_and_classify(source: str):
    from app.services.secop_fetcher import sync_secop
    from app.services.classifier import classify_contracts
    from app.services.notifier import notify_new_relevant_contracts

    try:
        logger.info("Scheduled sync started for %s", source)
        result = await sync_secop(source)

        prefiltered_ids = result.get("prefiltered_secop_ids", [])
        if prefiltered_ids:
            logger.info("Classifying %d prefiltered contracts", len(prefiltered_ids))
            await classify_contracts(prefiltered_ids)

            logger.info("Sending notifications for new relevant contracts")
            await notify_new_relevant_contracts()

        logger.info("Scheduled sync completed for %s", source)
    except Exception as exc:
        logger.exception("Scheduled sync failed for %s: %s", source, exc)


async def job_sync_secop_ii():
    await _run_sync_and_classify("SECOP_II")


async def job_sync_secop_i():
    await _run_sync_and_classify("SECOP_I")


def start_scheduler():
    scheduler.add_job(
        job_sync_secop_ii,
        "interval",
        hours=settings.sync_interval_hours,
        id="sync_secop_ii",
        replace_existing=True,
    )
    scheduler.add_job(
        job_sync_secop_i,
        "interval",
        hours=24,
        id="sync_secop_i",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "APScheduler started — SECOP II every %dh, SECOP I every 24h",
        settings.sync_interval_hours,
    )


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("APScheduler stopped")
