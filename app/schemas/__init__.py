"""app/schemas/__init__.py
-------------------------
Pydantic schema package.

Phase 1: empty — schemas will be added alongside models in Phase 2.
"""

from app.schemas.company import (
    CompanyAnalyzeRequest,
    CompanyProfileResponse,
    CompetitorDiscoverRequest,
    CompetitorDiscoverResponse,
    CompetitorSuggestionResponse,
    CompetitorApproveRequest,
    CompetitorRejectRequest,
)

__all__ = [
    "CompanyAnalyzeRequest",
    "CompanyProfileResponse",
    "CompetitorDiscoverRequest",
    "CompetitorDiscoverResponse",
    "CompetitorSuggestionResponse",
    "CompetitorApproveRequest",
    "CompetitorRejectRequest",
]
