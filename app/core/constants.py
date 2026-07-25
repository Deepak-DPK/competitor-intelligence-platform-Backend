"""
app/core/constants.py
---------------------
Project-wide constants.  All magic strings / numbers live here.
Import from this module instead of scattering literals across the codebase.
"""

from enum import Enum


# ------------------------------------------------------------------ #
# API
# ------------------------------------------------------------------ #
API_V1_PREFIX = "/api/v1"
HEALTH_CHECK_TAG = "Health"
AUTH_TAG = "Auth"
PROJECTS_TAG = "Projects"
COMPETITORS_TAG = "Competitors"
MONITORING_TAG = "Monitoring"
DASHBOARD_TAG = "Dashboard"
REPORTS_TAG = "Reports"
ALERTS_TAG = "Alerts"
SETTINGS_TAG = "Settings"


# ------------------------------------------------------------------ #
# Pagination defaults
# ------------------------------------------------------------------ #
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_PAGE = 1


# ------------------------------------------------------------------ #
# Database conventions
# ------------------------------------------------------------------ #
DB_SCHEMA = "public"
UUID_GEN = "gen_random_uuid()"  # Postgres function for UUID generation


# ------------------------------------------------------------------ #
# User roles
# ------------------------------------------------------------------ #
class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


# ------------------------------------------------------------------ #
# Project status
# ------------------------------------------------------------------ #
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


# ------------------------------------------------------------------ #
# Monitoring / snapshot types
# ------------------------------------------------------------------ #
class SnapshotType(str, Enum):
    WEBSITE = "website"
    KEYWORD = "keyword"
    PRICING = "pricing"
    SOCIAL = "social"
    ADVERTISING = "advertising"


# ------------------------------------------------------------------ #
# Change detection
# ------------------------------------------------------------------ #
class ChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class ChangeSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ------------------------------------------------------------------ #
# Alert severity
# ------------------------------------------------------------------ #
class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# ------------------------------------------------------------------ #
# Report types
# ------------------------------------------------------------------ #
class ReportType(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"
    ON_DEMAND = "on_demand"


# ------------------------------------------------------------------ #
# Monitoring scan frequencies (in minutes)
# ------------------------------------------------------------------ #
class ScanFrequency(str, Enum):
    HOURLY = "hourly"         # 60 min
    DAILY = "daily"           # 1440 min
    WEEKLY = "weekly"         # 10080 min

SCAN_FREQUENCY_MINUTES: dict[str, int] = {
    ScanFrequency.HOURLY: 60,
    ScanFrequency.DAILY: 1440,
    ScanFrequency.WEEKLY: 10080,
}


# ------------------------------------------------------------------ #
# Social platforms
# ------------------------------------------------------------------ #
class SocialPlatform(str, Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


# ------------------------------------------------------------------ #
# AI insight confidence thresholds
# ------------------------------------------------------------------ #
AI_HIGH_CONFIDENCE = 0.85
AI_MEDIUM_CONFIDENCE = 0.60
AI_LOW_CONFIDENCE = 0.40


# ------------------------------------------------------------------ #
# HTTP headers
# ------------------------------------------------------------------ #
CORRELATION_ID_HEADER = "X-Correlation-ID"
REQUEST_ID_HEADER = "X-Request-ID"


# ------------------------------------------------------------------ #
# Recommendation priority
# ------------------------------------------------------------------ #
class RecommendationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    DISMISSED = "dismissed"


# ------------------------------------------------------------------ #
# Misc
# ------------------------------------------------------------------ #
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_COMPETITORS_PER_PROJECT = 50
MAX_KEYWORDS_PER_COMPETITOR = 100
