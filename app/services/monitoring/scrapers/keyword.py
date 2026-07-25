"""
app/services/monitoring/scrapers/keyword.py
-------------------------------------------
Scrapes SEO metadata (title, meta desc, H1, H2) using BeautifulSoup.
"""

from uuid import UUID

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.models.keyword_snapshot import KeywordSnapshot
from app.services.monitoring.scrapers.base import BaseScraper


class KeywordScraper(BaseScraper):
    async def run(self, competitor_id: UUID, url: str) -> KeywordSnapshot:
        self.logger.info("Running KeywordScraper", extra={"competitor_id": str(competitor_id), "url": url})
        
        # We still use Playwright in case the metadata is injected via JS (e.g. React/Vue SPAs)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html_content = await page.content()
            await browser.close()

        soup = BeautifulSoup(html_content, "lxml")
        
        # Title
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        
        # Meta description
        meta_desc = None
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()
            
        # H1
        h1_tag = soup.find("h1")
        h1 = h1_tag.get_text(strip=True) if h1_tag else None
        
        # H2 (concatenate top 3 H2s)
        h2_tags = soup.find_all("h2", limit=3)
        h2 = " | ".join([tag.get_text(strip=True) for tag in h2_tags]) if h2_tags else None

        snapshot = KeywordSnapshot(
            competitor_id=competitor_id,
            keyword="brand_auto_extract", # Generic placeholder
            title=title,
            meta_description=meta_desc,
            h1=h1,
            h2=h2
        )
        
        self._db.add(snapshot)
        await self._db.flush()
        
        self.logger.info("Keyword snapshot created", extra={"snapshot_id": str(snapshot.id)})
        return snapshot
