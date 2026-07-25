"""
tests/test_ai_pipeline.py
-------------------------
Tests for the AI integration pipeline (Phase 6).
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app.services.ai.change_detection import ChangeDetectionEngine
from app.services.ai.prompt_manager import PromptManager
from app.services.ai.gemini import AIService
from app.services.ai.recommendation import RecommendationEngine
from app.models.change_log import ChangeLog
from app.core.constants import SnapshotType, ChangeSeverity, ChangeType

pytestmark = pytest.mark.asyncio

async def test_prompt_manager():
    change = ChangeLog(
        id=uuid4(),
        competitor_id=uuid4(),
        snapshot_type=SnapshotType.PRICING,
        change_type=ChangeType.MODIFIED,
        severity=ChangeSeverity.HIGH,
        summary="Price changed from 150 to 130"
    )
    prompt = PromptManager.build_prompt(change)
    assert "rate parity" in prompt
    assert "150 to 130" in prompt
    assert "PRICING" in prompt
