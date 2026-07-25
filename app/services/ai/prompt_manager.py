"""
app/services/ai/prompt_manager.py
---------------------------------
Manages prompt templates for different types of competitor changes.
"""

from app.core.constants import SnapshotType
from app.models.change_log import ChangeLog


class PromptManager:
    @staticmethod
    def build_prompt(change_log: ChangeLog) -> str:
        """
        Builds a context-aware prompt for Google Gemini based on the change log.
        """
        base_instruction = (
            "You are an expert AI hotel revenue manager and business analyst. "
            "A competitor tracking system has detected a change in a competitor's strategy. "
            "Analyze the change and provide exactly three outputs in strict JSON format:\n"
            "1. 'summary': A 1-2 sentence executive summary of the change.\n"
            "2. 'business_impact': A paragraph explaining the potential impact on our hotel's revenue or market positioning.\n"
            "3. 'confidence': A float between 0.0 and 1.0 indicating your confidence in this analysis.\n"
            "4. 'recommendations': A list of objects, each containing 'recommendation' (text) and 'priority' (low, medium, high).\n\n"
            "Return ONLY valid JSON. Do not include markdown blocks like ```json.\n\n"
        )

        specific_context = f"Detected Change Type: {change_log.snapshot_type}\n"
        specific_context += f"Severity: {change_log.severity}\n"
        specific_context += f"Change Details: {change_log.summary}\n\n"
        
        if change_log.snapshot_type == SnapshotType.PRICING:
            specific_context += (
                "Focus your analysis on rate parity, potential price wars, and whether we should adjust our own ADR (Average Daily Rate).\n"
            )
        elif change_log.snapshot_type == SnapshotType.WEBSITE:
            specific_context += (
                "Focus your analysis on how their website changes affect user experience, conversion rates, or new amenities highlighted.\n"
            )
        elif change_log.snapshot_type == SnapshotType.KEYWORD:
            specific_context += (
                "Focus your analysis on their SEO strategy shift. Are they targeting new demographics or search intents?\n"
            )
        elif change_log.snapshot_type == SnapshotType.SOCIAL:
            specific_context += (
                "Focus your analysis on their social media engagement spike and whether their viral content poses a threat to our brand awareness.\n"
            )
        elif change_log.snapshot_type == SnapshotType.ADVERTISING:
            specific_context += (
                "Focus your analysis on their ad spend, new promotions, and what customer segments their CTA is targeting.\n"
            )

        return base_instruction + specific_context
