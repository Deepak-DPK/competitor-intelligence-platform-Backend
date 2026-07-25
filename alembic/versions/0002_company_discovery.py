"""
add company discovery tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-25 17:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('company_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('competitor_suggestions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('competitor_name', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('confidence_score', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('competitor_suggestions')
    op.drop_table('company_profiles')
