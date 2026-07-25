"""
app/services/monitoring/scrapers/social.py
------------------------------------------
Mock scraper for social media.
In a real environment, this would use official APIs (Twitter API, Meta Graph API)
or specialized scraping tools, since Playwright is easily blocked by social platforms.
"""

from uuid import UUID

from app.models.social_snapshot import SocialSnapshot
from app.services.monitoring.scrapers.base import BaseScraper


class SocialScraper(BaseScraper):
    async def run(self, competitor_id: UUID, url: str) -> SocialSnapshot:
        self.logger.info("Running SocialScraper (MOCK)", extra={"competitor_id": str(competitor_id)})
        
        # MOCK IMPLEMENTATION
        snapshot = SocialSnapshot(
            competitor_id=competitor_id,
            platform="twitter",
            post_title="Exciting new hotel opening!",
            post_url="https://twitter.com/competitor/status/12345",
            engagement=142
        )
        
        self._db.add(snapshot)
        await self._db.flush()
        
        self.logger.info("Social snapshot created (MOCK)", extra={"snapshot_id": str(snapshot.id)})
        return snapshot
