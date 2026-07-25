"""
app/schemas/alert.py
--------------------
Pydantic schemas for Alerts.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    message: Optional[str] = None
    severity: str
    is_read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
