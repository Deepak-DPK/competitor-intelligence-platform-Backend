"""
app/services/monitoring/scrapers/advertising.py
-----------------------------------------------
Mock scraper for advertising campaigns.
In a real environment, this would use Facebook Ad Library API or Google Ads Transparency Center.
"""

from uuid import UUID

from app.models.advertising_snapshot import AdvertisingSnapshot
from app.services.monitoring.scrapers.base import BaseScraper


class AdvertisingScraper(BaseScraper):
    async def run(self, competitor_id: UUID, url: str) -> AdvertisingSnapshot:
        self.logger.info("Running AdvertisingScraper (MOCK)", extra={"competitor_id": str(competitor_id)})
        
        # MOCK IMPLEMENTATION
        snapshot = AdvertisingSnapshot(
            competitor_id=competitor_id,
            campaign="Summer 2026 Getaway",
            landing_page="https://competitor.com/summer-sale",
            cta="Book Now"
        )
        
        self._db.add(snapshot)
        await self._db.flush()
        
        self.logger.info("Advertising snapshot created (MOCK)", extra={"snapshot_id": str(snapshot.id)})
        return snapshot
