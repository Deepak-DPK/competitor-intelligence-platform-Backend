"""
app/services/monitoring/worker.py
---------------------------------
Background worker that processes ScrapeJob tasks from the MonitoringQueue.
Includes retry logic via tenacity.
"""

import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logging import get_logger
from app.database.session import _TestSessionLocal, engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.services.monitoring.queue import ScrapeJob, monitoring_queue
from app.services.monitoring.scrapers.website import WebsiteScraper
from app.services.monitoring.scrapers.pricing import PricingScraper
from app.services.monitoring.scrapers.keyword import KeywordScraper
from app.services.monitoring.scrapers.social import SocialScraper
from app.services.monitoring.scrapers.advertising import AdvertisingScraper


logger = get_logger(__name__)

# Use the app's async sessionmaker
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def execute_job(job: ScrapeJob, db: AsyncSession):
    """Executes a single job with retry logic."""
    if job.module_type == "website":
        scraper = WebsiteScraper(db)
    elif job.module_type == "pricing":
        scraper = PricingScraper(db)
    elif job.module_type == "keyword":
        scraper = KeywordScraper(db)
    elif job.module_type == "social":
        scraper = SocialScraper(db)
    elif job.module_type == "advertising":
        scraper = AdvertisingScraper(db)
    else:
        logger.error("Unknown module type", extra={"module_type": job.module_type})
        return

    await scraper.run(job.competitor_id, job.url or "")
    await db.commit()


async def monitoring_worker():
    """Background task that runs forever, processing jobs from the queue."""
    logger.info("Monitoring worker started.")
    try:
        while True:
            job = await monitoring_queue.dequeue()
            logger.info("Processing job", extra={"job": job})

            # Create a fresh DB session for each job
            async with AsyncSessionLocal() as db:
                try:
                    await execute_job(job, db)
                    logger.info("Job completed successfully", extra={"job": job})
                except Exception as e:
                    logger.exception("Job failed after all retries", extra={"job": job, "error": str(e)})
                    await db.rollback()
                finally:
                    monitoring_queue.task_done()
    except asyncio.CancelledError:
        logger.info("Monitoring worker cancelled.")
