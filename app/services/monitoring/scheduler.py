"""
app/services/monitoring/scheduler.py
------------------------------------
Periodically scans MonitoringSettings and enqueues jobs based on frequency.
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.logging import get_logger
from app.database.session import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.competitor import Competitor
from app.models.monitoring_settings import MonitoringSettings
from app.services.monitoring.queue import ScrapeJob, monitoring_queue

logger = get_logger(__name__)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def monitoring_scheduler():
    """
    Background task that wakes up periodically (e.g. every 60s)
    to check if competitors need to be scanned.
    """
    logger.info("Monitoring scheduler started.")
    try:
        while True:
            # Wake up every 60 seconds (for testing, we'd use hours/days in production)
            await asyncio.sleep(60)
            
            async with AsyncSessionLocal() as db:
                # Find all competitors that have active monitoring settings
                stmt = (
                    select(Competitor, MonitoringSettings)
                    .join(MonitoringSettings, Competitor.id == MonitoringSettings.competitor_id)
                    .where(Competitor.deleted_at.is_(None))
                )
                result = await db.execute(stmt)
                rows = result.all()

                for competitor, settings in rows:
                    url = competitor.website_url

                    # Check Website
                    if settings.website_enabled:
                        await monitoring_queue.enqueue(ScrapeJob(competitor.id, "website", url))
                    
                    # Check Pricing
                    if settings.pricing_enabled:
                        await monitoring_queue.enqueue(ScrapeJob(competitor.id, "pricing", url))
                        
                    # Check Keyword
                    if settings.keyword_enabled:
                        await monitoring_queue.enqueue(ScrapeJob(competitor.id, "keyword", url))
                        
                    # Check Social
                    if settings.social_enabled:
                        await monitoring_queue.enqueue(ScrapeJob(competitor.id, "social", url))
                        
                    # Check Advertising
                    if settings.advertising_enabled:
                        await monitoring_queue.enqueue(ScrapeJob(competitor.id, "advertising", url))
                        
            logger.info("Scheduler completed a pass.")
    except asyncio.CancelledError:
        logger.info("Monitoring scheduler cancelled.")
