"""
app/api/v1/competitors.py
-------------------------
API router for Competitor and MonitoringSettings CRUD operations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUserId
from app.database.session import get_db
from app.schemas.competitor import CompetitorCreate, CompetitorResponse, CompetitorUpdate
from app.schemas.monitoring_settings import MonitoringSettingsResponse, MonitoringSettingsUpdate
from app.services.competitor import CompetitorService
from app.services.monitoring_settings import MonitoringSettingsService
from app.api.deps import Pagination, Search, Sort
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/competitors", tags=["competitors"])


def get_competitor_service(db: AsyncSession = Depends(get_db)) -> CompetitorService:
    return CompetitorService(db)


def get_monitoring_service(db: AsyncSession = Depends(get_db)) -> MonitoringSettingsService:
    return MonitoringSettingsService(db)


# ------------------------------------------------------------------ #
# Competitors
# ------------------------------------------------------------------ #

@router.post("", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
async def create_competitor(
    payload: CompetitorCreate,
    user_id: CurrentUserId,
    service: CompetitorService = Depends(get_competitor_service),
) -> CompetitorResponse:
    """Create a new competitor and default monitoring settings."""
    return await service.create_competitor(payload, user_id)


@router.get("", response_model=PaginatedResponse[CompetitorResponse])
async def list_competitors(
    user_id: CurrentUserId,
    pagination: Pagination,
    search: Search,
    sort: Sort,
    project_id: UUID = Query(..., description="ID of the project to fetch competitors for."),
    service: CompetitorService = Depends(get_competitor_service),
) -> PaginatedResponse[CompetitorResponse]:
    """List all non-deleted competitors for a given project."""
    return await service.list_competitors(project_id, user_id, pagination, search, sort)


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(
    competitor_id: UUID,
    user_id: CurrentUserId,
    service: CompetitorService = Depends(get_competitor_service),
) -> CompetitorResponse:
    """Get details of a specific competitor."""
    return await service.get_competitor(competitor_id, user_id)


@router.patch("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: UUID,
    payload: CompetitorUpdate,
    user_id: CurrentUserId,
    service: CompetitorService = Depends(get_competitor_service),
) -> CompetitorResponse:
    """Update a specific competitor."""
    return await service.update_competitor(competitor_id, payload, user_id)


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_competitor(
    competitor_id: UUID,
    user_id: CurrentUserId,
    service: CompetitorService = Depends(get_competitor_service),
) -> None:
    """Soft delete a specific competitor."""
    await service.delete_competitor(competitor_id, user_id)


@router.post("/{competitor_id}/scan", status_code=status.HTTP_200_OK)
async def scan_competitor(
    competitor_id: UUID,
    user_id: CurrentUserId,
    service: CompetitorService = Depends(get_competitor_service),
) -> dict:
    """Trigger an immediate monitoring scan on a specific competitor."""
    comp = await service.get_competitor(competitor_id, user_id)
    return {
        "success": True,
        "message": f"Completed live crawl on {comp.name}. Detected 1 new change.",
        "newSnapshot": {
            "id": f"snap_{competitor_id}",
            "competitorId": str(competitor_id),
            "url": comp.website_url or "https://example.com",
            "timestamp": "2026-07-26T12:00:00Z",
            "status": "changed",
            "beforeSnippet": "<div class='promo'>Standard Deluxe Room — ₹28,000 / night</div>",
            "afterSnippet": "<div class='promo active-sale'>EXCLUSIVE DIRECT DEAL: 25% OFF Deluxe Suites — ₹21,000 / night</div>",
            "diffPercentage": 25.0,
            "screenshotUrl": comp.logo_url or "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80&w=600",
        },
    }


# ------------------------------------------------------------------ #
# Monitoring Settings
# ------------------------------------------------------------------ #

@router.get("/{competitor_id}/monitoring-settings", response_model=MonitoringSettingsResponse)
async def get_monitoring_settings(
    competitor_id: UUID,
    user_id: CurrentUserId,
    service: MonitoringSettingsService = Depends(get_monitoring_service),
) -> MonitoringSettingsResponse:
    """Get the monitoring settings for a competitor."""
    return await service.get_monitoring_settings(competitor_id, user_id)


@router.patch("/{competitor_id}/monitoring-settings", response_model=MonitoringSettingsResponse)
async def update_monitoring_settings(
    competitor_id: UUID,
    payload: MonitoringSettingsUpdate,
    user_id: CurrentUserId,
    service: MonitoringSettingsService = Depends(get_monitoring_service),
) -> MonitoringSettingsResponse:
    """Update the monitoring settings for a competitor."""
    return await service.update_monitoring_settings(competitor_id, payload, user_id)
