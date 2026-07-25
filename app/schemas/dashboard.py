"""
app/schemas/dashboard.py
------------------------
Pydantic schemas for the Dashboard API.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DashboardStatistics(BaseModel):
    total_competitors: int
    active_alerts: int
    pending_recommendations: int


class RecentInsightResponse(BaseModel):
    id: UUID
    change_log_id: UUID
    summary: Optional[str]
    business_impact: Optional[str]
    confidence: Optional[float]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TimelineEvent(BaseModel):
    id: UUID
    snapshot_type: str
    change_type: str
    severity: str
    summary: Optional[str]
    detected_at: datetime
    competitor_id: UUID
    competitor_name: str
    
    model_config = ConfigDict(from_attributes=True)
