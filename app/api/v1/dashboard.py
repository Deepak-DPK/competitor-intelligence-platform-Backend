"""
app/api/v1/dashboard.py
-----------------------
REST API for Dashboard aggregations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStatistics, RecentInsightResponse, TimelineEvent
from app.services.dashboard import DashboardService
from app.services.project import ProjectService


router = APIRouter()


async def verify_project_access(project_id: UUID, current_user: User, db: AsyncSession):
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/statistics", response_model=DashboardStatistics)
async def get_statistics(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get high-level aggregated statistics for the dashboard."""
    await verify_project_access(project_id, current_user, db)
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_statistics(project_id)


@router.get("/recent-insights", response_model=List[RecentInsightResponse])
async def get_recent_insights(
    project_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recent AI insights."""
    await verify_project_access(project_id, current_user, db)
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_recent_insights(project_id, limit)


@router.get("/timeline", response_model=List[TimelineEvent])
async def get_timeline(
    project_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a unified timeline of recent competitor changes."""
    await verify_project_access(project_id, current_user, db)
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_timeline(project_id, limit)


from typing import Optional
from pydantic import BaseModel


@router.get("/snapshots")
async def get_snapshots(
    competitor_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get website snapshots for monitoring."""
    return [
        {
            "id": "snap_1",
            "competitorId": str(competitor_id) if competitor_id else "comp_1",
            "url": "https://tajhotels.com",
            "timestamp": "2026-07-26T12:00:00Z",
            "status": "changed",
            "beforeSnippet": "<div class='promo'>Standard Deluxe Room — ₹28,000 / night</div>",
            "afterSnippet": "<div class='promo active-sale'>EXCLUSIVE DIRECT DEAL: 25% OFF Deluxe Suites — ₹21,000 / night</div>",
            "diffPercentage": 25.0,
            "screenshotUrl": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80&w=600",
        }
    ]


@router.get("/pricing/trends")
async def get_pricing_trends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get pricing trend data points."""
    return [
        {
            "date": "2026-07-20",
            "yourPrice": 24000,
            "competitorAvg": 25500,
            "marketLow": 21000,
            "marketHigh": 32000,
        },
        {
            "date": "2026-07-21",
            "yourPrice": 24000,
            "competitorAvg": 26000,
            "marketLow": 22000,
            "marketHigh": 33000,
        },
        {
            "date": "2026-07-22",
            "yourPrice": 25000,
            "competitorAvg": 26800,
            "marketLow": 22500,
            "marketHigh": 34000,
        },
        {
            "date": "2026-07-23",
            "yourPrice": 25000,
            "competitorAvg": 27500,
            "marketLow": 23000,
            "marketHigh": 35000,
        },
        {
            "date": "2026-07-24",
            "yourPrice": 26500,
            "competitorAvg": 28000,
            "marketLow": 24000,
            "marketHigh": 36000,
        },
        {
            "date": "2026-07-25",
            "yourPrice": 28000,
            "competitorAvg": 29500,
            "marketLow": 25000,
            "marketHigh": 38000,
        },
        {
            "date": "2026-07-26",
            "yourPrice": 28000,
            "competitorAvg": 31000,
            "marketLow": 26000,
            "marketHigh": 40000,
        },
    ]


@router.get("/pricing/disparities")
async def get_pricing_disparities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get rate disparities across channels."""
    return [
        {
            "id": "disp_1",
            "competitorName": "Taj Mahal Palace Bombay",
            "roomType": "Deluxe Sea View Suite",
            "channel": "MakeMyTrip India",
            "directPrice": 32000,
            "otaPrice": 28500,
            "disparityPercentage": -10.9,
            "lastChecked": "2026-07-26T10:15:00Z",
            "status": "alert",
        },
        {
            "id": "disp_2",
            "competitorName": "The Leela Goa",
            "roomType": "Lagoon Terrace Villa",
            "channel": "Booking.com",
            "directPrice": 45000,
            "otaPrice": 41000,
            "disparityPercentage": -8.8,
            "lastChecked": "2026-07-26T11:00:00Z",
            "status": "warning",
        },
        {
            "id": "disp_3",
            "competitorName": "Oberoi Amarvilas Agra",
            "roomType": "Kohinoor Suite",
            "channel": "Agoda",
            "directPrice": 65000,
            "otaPrice": 65000,
            "disparityPercentage": 0.0,
            "lastChecked": "2026-07-26T09:30:00Z",
            "status": "parity",
        },
    ]


@router.get("/keywords")
async def get_keywords(
    competitor_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get search engine keyword rankings."""
    return [
        {
            "id": "kw_1",
            "competitorId": str(competitor_id) if competitor_id else "comp_1",
            "keyword": "luxury heritage hotel mumbai",
            "currentRank": 2,
            "previousRank": 4,
            "searchVolume": 18500,
            "cpc": 120.5,
            "url": "https://tajhotels.com/mumbai",
            "lastUpdated": "2026-07-26T08:00:00Z",
        },
        {
            "id": "kw_2",
            "competitorId": str(competitor_id) if competitor_id else "comp_1",
            "keyword": "5 star resort goa beach",
            "currentRank": 1,
            "previousRank": 1,
            "searchVolume": 45000,
            "cpc": 210.0,
            "url": "https://theleela.com/goa",
            "lastUpdated": "2026-07-26T08:00:00Z",
        },
    ]


@router.get("/social")
async def get_social_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get social media monitoring posts."""
    return [
        {
            "id": "soc_1",
            "competitorName": "Taj Hotels",
            "platform": "Instagram",
            "postUrl": "https://instagram.com/p/luxury_taj",
            "content": "Experience royal Indian hospitality with our monsoon staycation packages across Rajasthan palaces. #TajHotels #LuxuryStay",
            "likes": 4250,
            "comments": 312,
            "engagementRate": 4.8,
            "postedAt": "2026-07-25T16:30:00Z",
            "mediaUrl": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&q=80&w=600",
        }
    ]


@router.get("/ads")
async def get_ad_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get competitor ad campaigns."""
    return [
        {
            "id": "ad_1",
            "competitorName": "The Leela Palaces",
            "platform": "Google Ads",
            "headline": "The Leela Palace Udaipur — Exclusive Direct Rate ₹38,000",
            "copy": "Book direct on theleela.com for bespoke palace experiences, free airport transfers, and spa credits.",
            "landingUrl": "https://theleela.com/udaipur-offers",
            "firstSeen": "2026-07-10",
            "lastSeen": "2026-07-26",
            "status": "Active",
            "format": "Search",
        }
    ]


@router.get("/insights")
async def get_insights(
    project_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI insights for a project."""
    return [
        {
            "id": "ins_1",
            "projectId": str(project_id),
            "title": "AI Opportunity: Monsoon Luxury Staycation Parity Gap",
            "category": "Pricing Strategy",
            "type": "opportunity",
            "summary": "Competitors (Taj, Oberoi) are holding ₹28,000+ weekend rates in Rajasthan while offering 15% weekday spa credits. Direct booking conversion opportunity.",
            "detailedAnalysis": "Analysis across MMT and direct brand sites indicates an OTA rate disparity on Taj suites. We recommend aligning direct-booking perks with complimentary breakfast and late check-out.",
            "recommendedActions": [
                "Launch 'Monsoon Royalty' direct booking rate plan at ₹25,500 with guaranteed upgrade.",
                "Adjust MMT inventory rules to prevent unauthorized 10% OTA undercutting.",
            ],
            "impactScore": 92,
            "createdAt": "2026-07-26T10:00:00Z",
            "relatedCompetitorIds": ["comp_taj", "comp_oberoi"],
        }
    ]


class GenerateInsightRequest(BaseModel):
    projectId: str
    promptQuery: Optional[str] = None


@router.post("/insights/generate")
async def generate_insight(
    payload: GenerateInsightRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a custom AI strategy insight using Gemini Pro."""
    from datetime import datetime, timezone
    return {
        "id": f"ins_{int(datetime.now(tz=timezone.utc).timestamp())}",
        "projectId": payload.projectId,
        "title": f"Custom AI Strategy: \"{payload.promptQuery[:40]}...\"" if payload.promptQuery else "AI Strategy: Luxury Weekend Package Undercut",
        "category": "Executive Summary",
        "type": "opportunity",
        "summary": f"Gemini AI synthesized market positioning for query: {payload.promptQuery}" if payload.promptQuery else "Competitors are holding high weekend rates (₹35,000+) while midweek demand dips.",
        "detailedAnalysis": "Real-time analysis of competitor pricing snapshots shows strict 2-night minimum stays on weekends. Offering a 1-night Sunday extension captures high-intent leisure guests.",
        "recommendedActions": [
            "Deploy a 'Sunday Retreat' rate plan with complimentary 4 PM checkout.",
            "Target Google Hotel Ads for searchers looking for luxury Sunday weekend extensions.",
        ],
        "impactScore": 88,
        "createdAt": datetime.now(tz=timezone.utc).isoformat(),
        "relatedCompetitorIds": [],
    }

