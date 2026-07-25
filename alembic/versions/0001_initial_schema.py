"""
Initial schema migration — Phase 2
===================================
Creates all 16 tables for the AI Hotel Booking Competitor Intelligence Platform.

Tables created (in FK dependency order):
    1.  users
    2.  projects
    3.  project_members
    4.  activity_logs
    5.  competitors
    6.  alerts
    7.  reports
    8.  website_snapshots
    9.  keyword_snapshots
    10. pricing_snapshots
    11. social_snapshots
    12. advertising_snapshots
    13. monitoring_settings
    14. change_logs
    15. ai_insights
    16. recommendations

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-25 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")
UUID_GEN = sa.text("gen_random_uuid()")


def upgrade() -> None:
    # ---------------------------------------------------------------- #
    # 1. users
    # ---------------------------------------------------------------- #
    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ---------------------------------------------------------------- #
    # 2. projects
    # ---------------------------------------------------------------- #
    op.create_table(
        "projects",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("owner_id", UUID, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"],
            name="fk_projects_owner_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    op.create_index("ix_projects_status", "projects", ["status"])

    # ---------------------------------------------------------------- #
    # 3. project_members
    # ---------------------------------------------------------------- #
    op.create_table(
        "project_members",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("invited_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"],
            name="fk_project_members_project_id_projects",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name="fk_project_members_user_id_users",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "project_id", "user_id",
            name="uq_project_members_project_id_user_id",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_project_members"),
    )
    op.create_index("ix_project_members_project_id", "project_members", ["project_id"])
    op.create_index("ix_project_members_user_id", "project_members", ["user_id"])

    # ---------------------------------------------------------------- #
    # 4. activity_logs
    # ---------------------------------------------------------------- #
    op.create_table(
        "activity_logs",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("entity", sa.Text, nullable=True),
        sa.Column("entity_id", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name="fk_activity_logs_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_activity_logs"),
    )
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"])
    op.create_index("ix_activity_logs_entity", "activity_logs", ["entity"])
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"])

    # ---------------------------------------------------------------- #
    # 5. competitors
    # ---------------------------------------------------------------- #
    op.create_table(
        "competitors",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("website_url", sa.Text, nullable=False),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("monitoring_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"],
            name="fk_competitors_project_id_projects",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_competitors"),
    )
    op.create_index("ix_competitors_project_id", "competitors", ["project_id"])
    op.create_index("ix_competitors_monitoring_enabled", "competitors", ["monitoring_enabled"])

    # ---------------------------------------------------------------- #
    # 6. alerts
    # ---------------------------------------------------------------- #
    op.create_table(
        "alerts",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"],
            name="fk_alerts_project_id_projects",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_alerts"),
    )
    op.create_index("ix_alerts_project_id", "alerts", ["project_id"])
    op.create_index("ix_alerts_is_read", "alerts", ["is_read"])
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_project_id_is_read", "alerts", ["project_id", "is_read"])

    # ---------------------------------------------------------------- #
    # 7. reports
    # ---------------------------------------------------------------- #
    op.create_table(
        "reports",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("report_type", sa.String(30), nullable=False),
        sa.Column("report_url", sa.Text, nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"],
            name="fk_reports_project_id_projects",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reports"),
    )
    op.create_index("ix_reports_project_id", "reports", ["project_id"])
    op.create_index("ix_reports_report_type", "reports", ["report_type"])
    op.create_index("ix_reports_generated_at", "reports", ["generated_at"])

    # ---------------------------------------------------------------- #
    # 8. website_snapshots
    # ---------------------------------------------------------------- #
    op.create_table(
        "website_snapshots",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("competitor_id", UUID, nullable=False),
        sa.Column("page_url", sa.Text, nullable=False),
        sa.Column("html_hash", sa.Text, nullable=True),
        sa.Column("markdown_content", sa.Text, nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["competitor_id"], ["competitors.id"],
            name="fk_website_snapshots_competitor_id_competitors",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_website_snapshots"),
    )
    op.create_index(
        "ix_website_snapshots_competitor_id_captured_at",
        "website_snapshots",
        ["competitor_id", "captured_at"],
    )

    # ---------------------------------------------------------------- #
    # 9. keyword_snapshots
    # ---------------------------------------------------------------- #
    op.create_table(
        "keyword_snapshots",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("competitor_id", UUID, nullable=False),
        sa.Column("keyword", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("meta_description", sa.Text, nullable=True),
        sa.Column("h1", sa.Text, nullable=True),
        sa.Column("h2", sa.Text, nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["competitor_id"], ["competitors.id"],
            name="fk_keyword_snapshots_competitor_id_competitors",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_keyword_snapshots"),
    )
    op.create_index(
        "ix_keyword_snapshots_competitor_id_captured_at",
        "keyword_snapshots",
        ["competitor_id", "captured_at"],
    )
    op.create_index("ix_keyword_snapshots_keyword", "keyword_snapshots", ["keyword"])

    # ---------------------------------------------------------------- #
    # 10. pricing_snapshots
    # ---------------------------------------------------------------- #
    op.create_table(
        "pricing_snapshots",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("competitor_id", UUID, nullable=False),
        sa.Column("product_name", sa.Text, nullable=True),
        sa.Column("currency", sa.String(10), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("offer", sa.Text, nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["competitor_id"], ["competitors.id"],
            name="fk_pricing_snapshots_competitor_id_competitors",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_pricing_snapshots"),
    )
    op.create_index(
        "ix_pricing_snapshots_competitor_id_captured_at",
        "pricing_snapshots",
        ["competitor_id", "captured_at"],
    )

    # ---------------------------------------------------------------- #
    # 11. social_snapshots
    # ---------------------------------------------------------------- #
    op.create_table(
        "social_snapshots",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("competitor_id", UUID, nullable=False),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("post_title", sa.Text, nullable=True),
        sa.Column("post_url", sa.Text, nullable=True),
        sa.Column("engagement", sa.Integer, nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["competitor_id"], ["competitors.id"],
            name="fk_social_snapshots_competitor_id_competitors",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_social_snapshots"),
    )
    op.create_index(
        "ix_social_snapshots_competitor_id_captured_at",
        "social_snapshots",
        ["competitor_id", "captured_at"],
    )
    op.create_index("ix_social_snapshots_platform", "social_snapshots", ["platform"])

    # ---------------------------------------------------------------- #
    # 12. advertising_snapshots
    # ---------------------------------------------------------------- #
    op.create_table(
        "advertising_snapshots",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("competitor_id", UUID, nullable=False),
        sa.Column("campaign", sa.Text, nullable=True),
        sa.Column("landing_page", sa.Text, nullable=True),
        sa.Column("cta", sa.Text, nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["competitor_id"], ["competitors.id"],
            name="fk_advertising_snapshots_competitor_id_competitors",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_advertising_snapshots"),
    )
    op.create_index(
        "ix_advertising_snapshots_competitor_id_captured_at",
        "advertising_snapshots",
        ["competitor_id", "captured_at"],
    )

    # ---------------------------------------------------------------- #
    # 13. monitoring_settings
    # ---------------------------------------------------------------- #
    op.create_table(
        "monitoring_settings",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("competitor_id", UUID, nullable=False),
        sa.Column("website_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("keyword_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("pricing_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("social_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("advertising_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("scan_frequency", sa.String(20), nullable=False, server_default="daily"),
        sa.ForeignKeyConstraint(
            ["competitor_id"], ["competitors.id"],
            name="fk_monitoring_settings_competitor_id_competitors",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("competitor_id", name="uq_monitoring_settings_competitor_id"),
        sa.PrimaryKeyConstraint("id", name="pk_monitoring_settings"),
    )

    # ---------------------------------------------------------------- #
    # 14. change_logs
    # ---------------------------------------------------------------- #
    op.create_table(
        "change_logs",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("competitor_id", UUID, nullable=False),
        sa.Column("snapshot_type", sa.String(50), nullable=False),
        sa.Column("change_type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="low"),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["competitor_id"], ["competitors.id"],
            name="fk_change_logs_competitor_id_competitors",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_change_logs"),
    )
    op.create_index(
        "ix_change_logs_competitor_id_detected_at",
        "change_logs",
        ["competitor_id", "detected_at"],
    )
    op.create_index("ix_change_logs_severity", "change_logs", ["severity"])
    op.create_index("ix_change_logs_snapshot_type", "change_logs", ["snapshot_type"])

    # ---------------------------------------------------------------- #
    # 15. ai_insights
    # ---------------------------------------------------------------- #
    op.create_table(
        "ai_insights",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("change_log_id", UUID, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("business_impact", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.ForeignKeyConstraint(
            ["change_log_id"], ["change_logs.id"],
            name="fk_ai_insights_change_log_id_change_logs",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)",
            name="ck_ai_insights_confidence_range",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ai_insights"),
    )
    op.create_index("ix_ai_insights_change_log_id", "ai_insights", ["change_log_id"])

    # ---------------------------------------------------------------- #
    # 16. recommendations
    # ---------------------------------------------------------------- #
    op.create_table(
        "recommendations",
        sa.Column("id", UUID, primary_key=True, server_default=UUID_GEN),
        sa.Column("insight_id", UUID, nullable=False),
        sa.Column("recommendation", sa.Text, nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.ForeignKeyConstraint(
            ["insight_id"], ["ai_insights.id"],
            name="fk_recommendations_insight_id_ai_insights",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_recommendations"),
    )
    op.create_index("ix_recommendations_insight_id", "recommendations", ["insight_id"])
    op.create_index("ix_recommendations_status", "recommendations", ["status"])
    op.create_index("ix_recommendations_priority", "recommendations", ["priority"])


def downgrade() -> None:
    # Drop in reverse FK dependency order
    op.drop_table("recommendations")
    op.drop_table("ai_insights")
    op.drop_table("change_logs")
    op.drop_table("monitoring_settings")
    op.drop_table("advertising_snapshots")
    op.drop_table("social_snapshots")
    op.drop_table("pricing_snapshots")
    op.drop_table("keyword_snapshots")
    op.drop_table("website_snapshots")
    op.drop_table("reports")
    op.drop_table("alerts")
    op.drop_table("competitors")
    op.drop_table("activity_logs")
    op.drop_table("project_members")
    op.drop_table("projects")
    op.drop_table("users")
