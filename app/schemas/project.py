"""
app/schemas/project.py
----------------------
Pydantic schemas for the Project entity.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import ProjectStatus


class ProjectCreate(BaseModel):
    """Payload for POST /projects."""
    name: str = Field(..., max_length=255, description="Human-readable project name.")
    industry: Optional[str] = Field("Travel & Hospitality", max_length=100, description="Industry vertical.")
    description: Optional[str] = Field(None, description="Free-text project description.")
    business_type: Optional[str] = Field("Resort & Hospitality", max_length=100, description="Travel business type.")
    country: Optional[str] = Field("United States", max_length=100, description="Operating country.")
    currency: Optional[str] = Field("USD", max_length=10, description="Base currency.")
    primary_destinations: Optional[str] = Field(None, description="Comma-separated primary travel destinations.")
    monitoring_preferences: Optional[str] = Field(None, description="JSON string of monitoring preferences.")
    workspace_settings: Optional[str] = Field(None, description="JSON string of workspace settings.")


class ProjectUpdate(BaseModel):
    """Payload for PATCH /projects/{id}."""
    name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None)
    status: Optional[ProjectStatus] = Field(None, description="Project lifecycle status.")
    business_type: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=10)
    primary_destinations: Optional[str] = Field(None)
    monitoring_preferences: Optional[str] = Field(None)
    workspace_settings: Optional[str] = Field(None)


class ProjectResponse(BaseModel):
    """Response model for a Project."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    industry: Optional[str] = None
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    business_type: Optional[str] = "Resort & Hospitality"
    country: Optional[str] = "United States"
    currency: Optional[str] = "USD"
    primary_destinations: Optional[str] = None
    monitoring_preferences: Optional[str] = None
    workspace_settings: Optional[str] = None
