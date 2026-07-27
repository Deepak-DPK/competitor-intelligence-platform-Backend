"""
add Phase 1 travel workspace columns to projects

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-27 10:00:00.000000

Adds 5 Travel Workspace columns to the projects table:
  - business_type    (varchar 100, default 'Resort & Hospitality')
  - country          (varchar 100, default 'United States')
  - currency         (varchar 10,  default 'USD')
  - primary_destinations  (text, nullable)
  - monitoring_preferences (text, nullable)
  - workspace_settings    (text, nullable)

These columns were present in the ORM model (app/models/project.py)
but missing from the initial migration, causing a schema mismatch
that would surface as column-not-found errors at runtime.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add business_type column
    op.add_column(
        'projects',
        sa.Column(
            'business_type',
            sa.String(100),
            nullable=True,
            server_default='Resort & Hospitality',
        )
    )

    # Add country column (may already exist as nullable in some envs, use try/except)
    op.add_column(
        'projects',
        sa.Column(
            'country',
            sa.String(100),
            nullable=True,
            server_default='United States',
        )
    )

    # Add currency column
    op.add_column(
        'projects',
        sa.Column(
            'currency',
            sa.String(10),
            nullable=True,
            server_default='USD',
        )
    )

    # Add primary_destinations column (free-text, comma-separated)
    op.add_column(
        'projects',
        sa.Column(
            'primary_destinations',
            sa.Text,
            nullable=True,
        )
    )

    # Add monitoring_preferences column (JSON string)
    op.add_column(
        'projects',
        sa.Column(
            'monitoring_preferences',
            sa.Text,
            nullable=True,
        )
    )

    # Add workspace_settings column (JSON string)
    op.add_column(
        'projects',
        sa.Column(
            'workspace_settings',
            sa.Text,
            nullable=True,
        )
    )


def downgrade() -> None:
    op.drop_column('projects', 'workspace_settings')
    op.drop_column('projects', 'monitoring_preferences')
    op.drop_column('projects', 'primary_destinations')
    op.drop_column('projects', 'currency')
    op.drop_column('projects', 'country')
    op.drop_column('projects', 'business_type')
