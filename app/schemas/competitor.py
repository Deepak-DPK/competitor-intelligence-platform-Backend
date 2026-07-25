"""
app/schemas/competitor.py
-------------------------
Pydantic schemas for the Competitor entity.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class CompetitorCreate(BaseModel):
    """Payload for POST /competitors."""
    project_id: UUID = Field(..., description="Project this competitor belongs to.")
    name: str = Field(..., max_length=255, description="Competitor's display name.")
    website_url: AnyHttpUrl = Field(..., description="Base URL of the competitor's website.")
    country: Optional[str] = Field(None, max_length=100, description="Operating country.")
    category: Optional[str] = Field(None, max_length=100, description="Business category.")
    monitoring_enabled: bool = Field(True, description="Master switch for monitoring.")


class CompetitorUpdate(BaseModel):
    """Payload for PATCH /competitors/{id}."""
    name: Optional[str] = Field(None, max_length=255)
    website_url: Optional[AnyHttpUrl] = Field(None)
    country: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    monitoring_enabled: Optional[bool] = Field(None)


class CompetitorResponse(BaseModel):
    """Response model for a Competitor."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    website_url: str
    country: Optional[str]
    category: Optional[str]
    monitoring_enabled: bool
    created_at: datetime
    updated_at: datetime
