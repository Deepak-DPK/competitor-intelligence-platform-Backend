"""
app/services/company_analysis/search_service.py
-----------------------------------------------
Search service for discovering competitors based on a company profile.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import google.generativeai as genai

from app.core.config import settings
from app.core.logging import get_logger
from app.models.company_profile import CompanyProfile

logger = get_logger(__name__)

class SearchProvider(ABC):
    @abstractmethod
    async def discover_competitors(self, profile: CompanyProfile) -> List[Dict[str, Any]]:
        """
        Takes a CompanyProfile and returns a list of dictionaries with:
        name, website, confidence_score, reason
        """
        pass

class GeminiSearchProvider(SearchProvider):
    """
    A placeholder search provider that uses Gemini to "guess" competitors
    based on the industry, category, and keywords.
    """
    
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def discover_competitors(self, profile: CompanyProfile) -> List[Dict[str, Any]]:
        if not self.model:
            logger.warning("No Gemini API key, cannot discover competitors via AI.")
            return []
            
        prompt = f"""
        You are an expert market researcher. Based on the following company profile, 
        identify 3 to 5 primary competitors in the same industry and category.

        Company Name: {profile.company_name}
        Website: {profile.website}
        Industry: {profile.industry}
        Category: {profile.category}
        Keywords: {profile.keywords}
        Summary: {profile.summary}

        Return ONLY a JSON array of objects with the following keys:
        - "name": The competitor's name
        - "website": The competitor's official website URL
        - "confidence_score": A float between 0.0 and 1.0 indicating how certain you are they compete.
        - "reason": A 1-sentence reason why they are a competitor.
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
                
            competitors = json.loads(raw_text.strip())
            if isinstance(competitors, list):
                return competitors
            return []
        except Exception as e:
            logger.error("Gemini competitor discovery failed", extra={"error": str(e)})
            return []
