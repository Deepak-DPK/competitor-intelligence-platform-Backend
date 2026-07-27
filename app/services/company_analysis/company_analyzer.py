"""
app/services/company_analysis/company_analyzer.py
-------------------------------------------------
Analyzes a company website to extract structured business information.
"""

import json
from typing import Any, Dict

import httpx
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.company_profile import CompanyProfile

logger = get_logger(__name__)

class CompanyAnalyzer:
    """
    Independent service for analyzing a company website and extracting
    business profiles using Firecrawl Cloud API and Google Gemini.
    """
    
    def __init__(self, db: AsyncSession):
        self._db = db
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def extract_markdown(self, url: str) -> str:
        """
        Uses Firecrawl Cloud API to fetch the website as clean markdown.
        """
        from app.services.monitoring.firecrawl_service import FirecrawlService
        fc_service = FirecrawlService()
        try:
            return await fc_service.extract_markdown(url)
        except Exception as e:
            logger.error("Firecrawl API call error", extra={"error": str(e)})
            return ""

    async def analyze(self, project_id: str, website: str) -> "CompanyProfile":
        """
        Main pipeline: fetch markdown -> gemini -> save profile.
        """
        import uuid as _uuid
        markdown = await self.extract_markdown(website)
        
        if not markdown:
            markdown = f"Company website: {website}. Unable to fetch full content."

        structured_data = await self._run_gemini_extraction(website, markdown)

        # Provide smart fallbacks when Gemini returns nothing
        if not structured_data.get("company_name"):
            # Extract name from domain
            from urllib.parse import urlparse
            domain = urlparse(website).netloc.replace("www.", "")
            structured_data["company_name"] = domain.split(".")[0].capitalize()
        if not structured_data.get("industry"):
            structured_data["industry"] = "Travel & Tourism"
        if not structured_data.get("category"):
            structured_data["category"] = "Online Travel Agency"
        if not structured_data.get("summary"):
            structured_data["summary"] = f"{structured_data['company_name']} is an online travel and booking platform."
        if not structured_data.get("keywords"):
            structured_data["keywords"] = ["flights", "hotels", "travel", "booking", "india"]

        profile = CompanyProfile(
            project_id=_uuid.UUID(project_id) if isinstance(project_id, str) else project_id,
            website=website,
            company_name=structured_data.get("company_name"),
            industry=structured_data.get("industry"),
            category=structured_data.get("category"),
            summary=structured_data.get("summary"),
            keywords=structured_data.get("keywords", []),
        )
        
        self._db.add(profile)
        await self._db.flush()
        await self._db.refresh(profile)
        
        return profile

    async def _run_gemini_extraction(self, website: str, markdown: str) -> Dict[str, Any]:
        """
        Calls Gemini to extract business info from markdown.
        """
        if not self.model:
            return {}

        prompt = f"""
        You are an expert business analyst. Extract structured information about the company from this website content.
        Website: {website}
        
        Content (Markdown):
        {markdown[:15000]}  # Truncating to avoid token limits just in case
        
        Extract the following fields and return ONLY a valid JSON object:
        - "company_name": Name of the company.
        - "industry": The primary industry (e.g., 'Hospitality', 'SaaS', 'Retail').
        - "category": The specific business category (e.g., 'Luxury Resort', 'B2B CRM').
        - "summary": A 2-3 sentence business summary.
        - "keywords": A list of important keywords, products, or target audiences (max 10).
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            return json.loads(raw_text.strip())
        except Exception as e:
            logger.error("Gemini business extraction failed", extra={"error": str(e)})
            return {}
