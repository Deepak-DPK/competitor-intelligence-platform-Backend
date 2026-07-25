"""
app/schemas/monitoring_settings.py
----------------------------------
Pydantic schemas for Monitoring Settings.
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import ScanFrequency


class MonitoringSettingsUpdate(BaseModel):
    """Payload for PATCH /competitors/{id}/monitoring-settings."""
    website_enabled: bool | None = Field(None, description="Enable website page monitoring.")
    keyword_enabled: bool | None = Field(None, description="Enable SEO keyword monitoring.")
    pricing_enabled: bool | None = Field(None, description="Enable pricing monitoring.")
    social_enabled: bool | None = Field(None, description="Enable social media monitoring.")
    advertising_enabled: bool | None = Field(None, description="Enable advertising monitoring.")
    scan_frequency: ScanFrequency | None = Field(None, description="Scan frequency.")


class MonitoringSettingsResponse(BaseModel):
    """Response model for Monitoring Settings."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    competitor_id: UUID
    website_enabled: bool
    keyword_enabled: bool
    pricing_enabled: bool
    social_enabled: bool
    advertising_enabled: bool
    scan_frequency: str
