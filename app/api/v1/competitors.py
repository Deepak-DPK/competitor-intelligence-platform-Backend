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


from app.api.deps import Pagination, Search, Sort
from app.schemas.common import PaginatedResponse

@router.get("", response_model=PaginatedResponse[CompetitorResponse])
async def list_competitors(
    project_id: UUID = Query(..., description="ID of the project to fetch competitors for."),
    user_id: CurrentUserId = Depends(),
    pagination: Pagination = Depends(),
    search: Search = Depends(),
    sort: Sort = Depends(),
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
