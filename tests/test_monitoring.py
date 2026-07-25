"""
tests/test_monitoring.py
------------------------
Unit tests for the monitoring engine.
Uses mocked Playwright to avoid requiring browser installation in test environments.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_snapshot import SocialSnapshot
from app.models.advertising_snapshot import AdvertisingSnapshot
from app.services.monitoring.scrapers.social import SocialScraper
from app.services.monitoring.scrapers.advertising import AdvertisingScraper
from app.services.monitoring.queue import ScrapeJob, monitoring_queue
from app.services.monitoring.worker import execute_job

pytestmark = pytest.mark.asyncio


async def test_queue_operations():
    """Test the in-memory queue works."""
    job = ScrapeJob(competitor_id=uuid4(), module_type="social", url="https://x.com")
    await monitoring_queue.enqueue(job)
    
    dequeued = await monitoring_queue.dequeue()
    assert dequeued.competitor_id == job.competitor_id
    assert dequeued.module_type == "social"
    
    monitoring_queue.task_done()


async def test_social_scraper(db_session: AsyncSession):
    """Test the mock social scraper inserts a snapshot."""
    comp_id = uuid4()
    scraper = SocialScraper(db_session)
    snapshot = await scraper.run(comp_id, "https://twitter.com/test")
    
    assert isinstance(snapshot, SocialSnapshot)
    assert snapshot.competitor_id == comp_id
    assert snapshot.platform == "twitter"


async def test_advertising_scraper(db_session: AsyncSession):
    """Test the mock advertising scraper inserts a snapshot."""
    comp_id = uuid4()
    scraper = AdvertisingScraper(db_session)
    snapshot = await scraper.run(comp_id, "https://google.com/ads")
    
    assert isinstance(snapshot, AdvertisingSnapshot)
    assert snapshot.competitor_id == comp_id
    assert snapshot.campaign == "Summer 2026 Getaway"


@patch("app.services.monitoring.scrapers.social.SocialScraper.run", new_callable=AsyncMock)
async def test_execute_job_routes_correctly(mock_run, db_session: AsyncSession):
    """Test that execute_job instantiates the correct scraper and runs it."""
    comp_id = uuid4()
    job = ScrapeJob(competitor_id=comp_id, module_type="social", url="https://x.com")
    
    await execute_job(job, db_session)
    
    mock_run.assert_called_once_with(comp_id, "https://x.com")
