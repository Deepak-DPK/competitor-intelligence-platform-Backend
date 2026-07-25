"""
app/schemas/report.py
---------------------
Pydantic schemas for Reports.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ReportResponse(BaseModel):
    id: UUID
    project_id: UUID
    report_type: str
    report_url: Optional[str]
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ReportCreate(BaseModel):
    project_id: UUID
    report_type: str
