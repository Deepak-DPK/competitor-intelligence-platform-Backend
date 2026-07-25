"""
app/services/monitoring/scrapers/website.py
-------------------------------------------
Scrapes raw HTML using Playwright, computes a SHA-256 hash, and extracts basic text using BeautifulSoup.
"""

import hashlib
from uuid import UUID

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.models.website_snapshot import WebsiteSnapshot
from app.services.monitoring.scrapers.base import BaseScraper


class WebsiteScraper(BaseScraper):
    async def run(self, competitor_id: UUID, url: str) -> WebsiteSnapshot:
        self.logger.info("Running WebsiteScraper", extra={"competitor_id": str(competitor_id), "url": url})
        
        # 1. Fetch raw HTML using Playwright
        html_content = ""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Wait until network is mostly idle to ensure dynamic content loads
            await page.goto(url, wait_until="networkidle", timeout=30000)
            html_content = await page.content()
            await browser.close()

        if not html_content:
            raise ValueError(f"Failed to retrieve HTML for {url}")

        # 2. Compute SHA-256 hash of the HTML
        html_hash = hashlib.sha256(html_content.encode("utf-8")).hexdigest()

        # 3. Clean the text using BeautifulSoup (simulate Jina AI Reader for now)
        soup = BeautifulSoup(html_content, "lxml")
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
        text = soup.get_text(separator="\n", strip=True)

        # 4. Save the snapshot to the database
        snapshot = WebsiteSnapshot(
            competitor_id=competitor_id,
            page_url=url,
            html_hash=html_hash,
            markdown_content=text,  # basic cleaned text
        )
        
        self._db.add(snapshot)
        await self._db.flush()
        
        self.logger.info("Website snapshot created", extra={"snapshot_id": str(snapshot.id)})
        return snapshot
