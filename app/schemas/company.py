"""
app/schemas/company.py
----------------------
Pydantic schemas for the Company Discovery module.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# ------------------------------------------------------------------ #
# Company Profile
# ------------------------------------------------------------------ #
class CompanyProfileBase(BaseModel):
    website: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[Dict[str, Any]] = None

class CompanyProfileResponse(CompanyProfileBase):
    id: UUID
    project_id: UUID

    model_config = ConfigDict(from_attributes=True)

class CompanyAnalyzeRequest(BaseModel):
    project_id: UUID
    website: HttpUrl

# ------------------------------------------------------------------ #
# Competitor Suggestions
# ------------------------------------------------------------------ #
class CompetitorSuggestionBase(BaseModel):
    competitor_name: str
    website: Optional[str] = None
    confidence_score: float = 0.0
    reason: Optional[str] = None
    approved: Optional[bool] = None

class CompetitorSuggestionResponse(CompetitorSuggestionBase):
    id: UUID
    project_id: UUID

    model_config = ConfigDict(from_attributes=True)

class CompetitorDiscoverRequest(BaseModel):
    project_id: UUID

class CompetitorDiscoverResponse(BaseModel):
    suggestions: List[CompetitorSuggestionResponse]

class CompetitorApproveRequest(BaseModel):
    # Additional fields if the user overrides name/website upon approval
    competitor_name: Optional[str] = None
    website: Optional[HttpUrl] = None

class CompetitorRejectRequest(BaseModel):
    pass
