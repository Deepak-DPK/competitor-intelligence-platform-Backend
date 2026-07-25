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
    industry: Optional[str] = Field(None, max_length=100, description="Industry vertical.")
    description: Optional[str] = Field(None, description="Free-text project description.")


class ProjectUpdate(BaseModel):
    """Payload for PATCH /projects/{id}."""
    name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None)
    status: Optional[ProjectStatus] = Field(None, description="Project lifecycle status.")


class ProjectResponse(BaseModel):
    """Response model for a Project."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    industry: Optional[str]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
