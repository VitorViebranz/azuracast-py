"""Add mount_points table

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mount_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("station_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("mount_path", sa.String(255), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("max_listeners", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("bitrate", sa.Integer(), nullable=False, server_default="128"),
        sa.Column("format", sa.String(20), nullable=False, server_default="mp3"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id", "mount_path", name="uq_mount_station_path"),
    )
    op.create_index("ix_mount_points_station_id", "mount_points", ["station_id"])


def downgrade() -> None:
    op.drop_index("ix_mount_points_station_id", table_name="mount_points")
    op.drop_table("mount_points")
