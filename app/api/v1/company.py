"""
app/api/v1/endpoints/company.py
-------------------------------
API routes for Company Analysis & Competitor Discovery.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.company_profile import CompanyProfile
from app.models.competitor import Competitor
from app.schemas.company import (
    CompanyAnalyzeRequest,
    CompanyProfileResponse,
    CompetitorDiscoverRequest,
    CompetitorDiscoverResponse,
    CompetitorSuggestionResponse,
    CompetitorApproveRequest,
    CompetitorRejectRequest
)
from app.services.company_analysis import (
    CompanyAnalyzer,
    CompetitorDiscoveryService,
    GeminiSearchProvider
)

router = APIRouter()


@router.post("/analyze", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
async def analyze_company(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request_data: CompanyAnalyzeRequest,
) -> Any:
    """
    Analyze a company website to extract structured business information.
    """
    analyzer = CompanyAnalyzer(db)
    profile = await analyzer.analyze(str(request_data.project_id), str(request_data.website))
    return profile


@router.post("/discover", response_model=CompetitorDiscoverResponse)
async def discover_competitors(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request_data: CompetitorDiscoverRequest,
) -> Any:
    """
    Discover competitors for a project based on its analyzed company profile.
    """
    # Fetch latest profile for the project
    stmt = select(CompanyProfile).where(
        CompanyProfile.project_id == request_data.project_id
    ).order_by(CompanyProfile.created_at.desc()).limit(1)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Please analyze the company first.")
        
    search_provider = GeminiSearchProvider()
    discovery_service = CompetitorDiscoveryService(db, search_provider)
    
    suggestions = await discovery_service.run_discovery(profile)
    return {"suggestions": suggestions}


@router.get("/suggestions", response_model=list[CompetitorSuggestionResponse])
async def get_suggestions(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get pending competitor suggestions for a project.
    """
    search_provider = GeminiSearchProvider()
    discovery_service = CompetitorDiscoveryService(db, search_provider)
    suggestions = await discovery_service.get_pending_suggestions(project_id)
    return suggestions


@router.post("/approve/{suggestion_id}", response_model=CompetitorSuggestionResponse)
async def approve_suggestion(
    *,
    suggestion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request_data: CompetitorApproveRequest,
) -> Any:
    """
    Approve a competitor suggestion and add it to the monitoring engine.
    """
    search_provider = GeminiSearchProvider()
    discovery_service = CompetitorDiscoveryService(db, search_provider)
    
    suggestion = await discovery_service.approve_suggestion(suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found.")
        
    # Insert into the actual competitors table for monitoring
    competitor_name = request_data.competitor_name or suggestion.competitor_name
    website = str(request_data.website) if request_data.website else suggestion.website
    
    new_competitor = Competitor(
        project_id=suggestion.project_id,
        name=competitor_name,
        website=website,
        # Default tracking configuration
        track_pricing=True,
        track_keywords=True,
        track_social=True,
        track_advertising=True,
    )
    db.add(new_competitor)
    await db.flush()
    
    return suggestion


@router.post("/reject/{suggestion_id}", response_model=CompetitorSuggestionResponse)
async def reject_suggestion(
    *,
    suggestion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request_data: CompetitorRejectRequest,
) -> Any:
    """
    Reject a competitor suggestion.
    """
    search_provider = GeminiSearchProvider()
    discovery_service = CompetitorDiscoveryService(db, search_provider)
    
    suggestion = await discovery_service.reject_suggestion(suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found.")
        
    return suggestion
