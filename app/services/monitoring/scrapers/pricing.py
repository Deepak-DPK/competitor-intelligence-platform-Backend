"""
app/services/monitoring/scrapers/pricing.py
-------------------------------------------
Scrapes pricing and offers from a page.
"""

import re
from decimal import Decimal
from uuid import UUID

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.models.pricing_snapshot import PricingSnapshot
from app.services.monitoring.scrapers.base import BaseScraper


class PricingScraper(BaseScraper):
    async def run(self, competitor_id: UUID, url: str) -> PricingSnapshot:
        self.logger.info("Running PricingScraper", extra={"competitor_id": str(competitor_id), "url": url})
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            html_content = await page.content()
            await browser.close()

        soup = BeautifulSoup(html_content, "lxml")
        text = soup.get_text(separator=" ")

        # -----------------------------------------------------------
        # Very basic heuristic to find a price (e.g., $199.99 or £150)
        # In a real system, this requires precise CSS selectors per competitor
        # or an AI-based extraction model.
        # -----------------------------------------------------------
        price_val = Decimal("0.00")
        currency = "USD"
        
        price_match = re.search(r'\$(\d{1,5}(?:\.\d{2})?)', text)
        if price_match:
            price_val = Decimal(price_match.group(1))
            currency = "USD"
        else:
            price_match_eur = re.search(r'€(\d{1,5}(?:\.\d{2})?)', text)
            if price_match_eur:
                price_val = Decimal(price_match_eur.group(1))
                currency = "EUR"

        # Offer heuristic
        offer = None
        if "off" in text.lower() or "discount" in text.lower():
            offer = "Potential discount detected on page"

        snapshot = PricingSnapshot(
            competitor_id=competitor_id,
            product_name="Main Product / Room",  # Generic for now
            currency=currency,
            price=price_val,
            offer=offer
        )
        
        self._db.add(snapshot)
        await self._db.flush()
        
        self.logger.info("Pricing snapshot created", extra={"snapshot_id": str(snapshot.id)})
        return snapshot
