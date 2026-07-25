"""
app/services/ai/gemini.py
-------------------------
Integrates with Google Gemini API to analyze ChangeLogs.
"""

import json
from typing import Optional

import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.change_log import ChangeLog
from app.models.ai_insight import AIInsight
from app.services.ai.prompt_manager import PromptManager


logger = get_logger(__name__)


class AIService:
    def __init__(self, db: AsyncSession):
        self._db = db
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use flash for fast structured extraction
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def generate_insight(self, change_log: ChangeLog) -> Optional[AIInsight]:
        """Calls Gemini to generate an AIInsight from a ChangeLog."""
        if not self.model:
            logger.warning("GEMINI_API_KEY not configured. Skipping AI Insight generation.")
            return None

        prompt = PromptManager.build_prompt(change_log)
        
        try:
            # We use async generate_content_async if available, else standard
            response = await self.model.generate_content_async(prompt)
            
            # Clean response text if it contains markdown formatting
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            data = json.loads(raw_text.strip())
            
            insight = AIInsight(
                change_log_id=change_log.id,
                summary=data.get("summary", "No summary provided."),
                business_impact=data.get("business_impact", "No impact provided."),
                confidence=float(data.get("confidence", 0.5)),
            )
            
            self._db.add(insight)
            await self._db.flush()
            
            # Create Recommendations if provided
            recs_data = data.get("recommendations", [])
            if recs_data:
                from app.services.ai.recommendation import RecommendationEngine
                rec_engine = RecommendationEngine(self._db)
                await rec_engine.process_recommendations(insight.id, recs_data)
                
            logger.info("AI Insight generated successfully", extra={"insight_id": str(insight.id)})
            return insight
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Gemini JSON output", extra={"error": str(e), "raw": response.text})
            return None
        except Exception as e:
            logger.error("Gemini API call failed", extra={"error": str(e)})
            return None
