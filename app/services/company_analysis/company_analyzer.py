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
    business profiles using Jina AI Reader and Google Gemini.
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
        Uses Jina AI Reader to fetch the website as clean markdown.
        """
        jina_url = f"https://r.jina.ai/{url}"
        headers = {"Authorization": f"Bearer {settings.JINA_API_KEY}"} if settings.JINA_API_KEY else {}

        async with httpx.AsyncClient(verify=False) as client:
            try:
                resp = await client.get(jina_url, headers=headers, timeout=30.0)
                if resp.status_code == 200:
                    return resp.text
                else:
                    logger.warning(f"Jina AI extraction failed with status {resp.status_code}")
                    return ""
            except Exception as e:
                logger.error("Jina API call error", extra={"error": str(e)})
                return ""

    async def analyze(self, project_id: str, website: str) -> CompanyProfile:
        """
        Main pipeline: fetch markdown -> gemini -> save profile.
        """
        markdown = await self.extract_markdown(website)
        
        if not markdown:
            # Fallback could be implemented here using Playwright/BS4 if desired, 
            # but for now we rely on Jina for clean markdown.
            markdown = f"Failed to fetch content for {website}."

        structured_data = await self._run_gemini_extraction(website, markdown)
        
        profile = CompanyProfile(
            project_id=project_id,
            website=website,
            company_name=structured_data.get("company_name"),
            industry=structured_data.get("industry"),
            category=structured_data.get("category"),
            summary=structured_data.get("summary"),
            keywords=structured_data.get("keywords", []),
        )
        
        self._db.add(profile)
        await self._db.flush()
        
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
