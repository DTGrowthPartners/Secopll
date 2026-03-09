"""Initial tables: contracts and sync_logs

Revision ID: 001
Revises:
Create Date: 2026-03-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("secop_id", sa.String(100), unique=True, nullable=False),
        sa.Column("source", sa.String(10), nullable=False),
        sa.Column("entity_name", sa.String(500)),
        sa.Column("entity_nit", sa.String(50)),
        sa.Column("department", sa.String(100)),
        sa.Column("city", sa.String(100)),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("contract_type", sa.String(200)),
        sa.Column("modality", sa.String(200)),
        sa.Column("estimated_value", sa.BigInteger),
        sa.Column("duration_days", sa.Integer),
        sa.Column("status", sa.String(100)),
        sa.Column("phase", sa.String(100)),
        sa.Column("published_at", sa.DateTime),
        sa.Column("deadline_at", sa.DateTime),
        sa.Column("last_updated_at", sa.DateTime),
        sa.Column("secop_url", sa.Text),
        sa.Column("category_code", sa.String(50)),
        # AI classification
        sa.Column("relevance_score", sa.Integer, server_default="0"),
        sa.Column("dt_service_category", sa.String(100)),
        sa.Column("dt_service_tags", ARRAY(sa.String)),
        sa.Column("classification_reason", sa.Text),
        sa.Column("is_relevant", sa.Boolean, server_default="false"),
        # Internal management
        sa.Column("internal_status", sa.String(50), server_default="'new'"),
        sa.Column("assigned_to", sa.String(100)),
        sa.Column("notes", sa.Text),
        sa.Column("notified_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index("ix_contracts_source", "contracts", ["source"])
    op.create_index("ix_contracts_is_relevant", "contracts", ["is_relevant"])
    op.create_index("ix_contracts_relevance_score", "contracts", ["relevance_score"])
    op.create_index("ix_contracts_department", "contracts", ["department"])
    op.create_index("ix_contracts_internal_status", "contracts", ["internal_status"])
    op.create_index("ix_contracts_published_at", "contracts", ["published_at"])
    op.create_index("ix_contracts_dt_service_category", "contracts", ["dt_service_category"])

    op.create_table(
        "sync_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source", sa.String(10)),
        sa.Column("started_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime),
        sa.Column("records_fetched", sa.Integer, server_default="0"),
        sa.Column("records_new", sa.Integer, server_default="0"),
        sa.Column("records_updated", sa.Integer, server_default="0"),
        sa.Column("status", sa.String(20)),
        sa.Column("error_message", sa.Text),
    )

    op.create_index("ix_sync_logs_source_started", "sync_logs", ["source", "started_at"])


def downgrade() -> None:
    op.drop_table("sync_logs")
    op.drop_table("contracts")
