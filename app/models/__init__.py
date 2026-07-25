"""
app/models/__init__.py
----------------------
Central model registry.

Import EVERY model here so that:
1. SQLAlchemy metadata is fully populated when the engine connects.
2. Alembic autogenerate can detect all tables and produce accurate migrations.

Ordered from least-dependent to most-dependent (FK resolution order).
"""

# ── Tier 0: no FK dependencies ─────────────────────────────────────────
from app.models.user import User                              # noqa: F401

# ── Tier 1: depends on User ─────────────────────────────────────────────
from app.models.project import Project                        # noqa: F401
from app.models.activity_log import ActivityLog               # noqa: F401

# ── Tier 2: depends on Project / User ───────────────────────────────────
from app.models.project_member import ProjectMember           # noqa: F401
from app.models.competitor import Competitor                  # noqa: F401
from app.models.alert import Alert                            # noqa: F401
from app.models.report import Report                          # noqa: F401

# ── Tier 3: depends on Competitor ───────────────────────────────────────
from app.models.website_snapshot import WebsiteSnapshot       # noqa: F401
from app.models.keyword_snapshot import KeywordSnapshot       # noqa: F401
from app.models.pricing_snapshot import PricingSnapshot       # noqa: F401
from app.models.social_snapshot import SocialSnapshot         # noqa: F401
from app.models.advertising_snapshot import AdvertisingSnapshot  # noqa: F401
from app.models.monitoring_settings import MonitoringSettings # noqa: F401
from app.models.change_log import ChangeLog                   # noqa: F401

# ── Tier 4: depends on ChangeLog ────────────────────────────────────────
from app.models.ai_insight import AIInsight                   # noqa: F401

# ── Tier 5: depends on AIInsight ────────────────────────────────────────
from app.models.recommendation import Recommendation          # noqa: F401

# ── Public re-exports (convenience) ────────────────────────────────────
__all__ = [
    "User",
    "Project",
    "ProjectMember",
    "Competitor",
    "WebsiteSnapshot",
    "KeywordSnapshot",
    "PricingSnapshot",
    "SocialSnapshot",
    "AdvertisingSnapshot",
    "MonitoringSettings",
    "ChangeLog",
    "AIInsight",
    "Recommendation",
    "Alert",
    "Report",
    "ActivityLog",
]

