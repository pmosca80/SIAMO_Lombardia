"""normative documenti

Revision ID: 0005_normative_documenti
Revises: 0004_numero_tessera
Create Date: 2026-08-08

Archivio dei documenti normativi importati da siamoesercito.org
(scripts/import_normative.py). Tabella globale, non multi-tenant: il
contenuto è pubblico/nazionale, non appartiene a un'organizzazione.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Identificatori della revisione, usati da Alembic.
revision: str = "0005_normative_documenti"
down_revision: Union[str, None] = "0004_numero_tessera"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "normative_documenti",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("categoria_macro_slug", sa.String(length=100), nullable=False),
        sa.Column("categoria_macro_nome", sa.String(length=150), nullable=False),
        sa.Column("categoria_sub_slug", sa.String(length=150), nullable=False),
        sa.Column("categoria_sub_nome", sa.String(length=150), nullable=False),
        sa.Column("titolo", sa.String(length=500), nullable=False),
        sa.Column("data_pubblicazione", sa.Date(), nullable=True),
        sa.Column("source_url", sa.String(length=1024), nullable=False),
        sa.Column("storage_key", sa.String(length=1024), nullable=True),
        sa.Column("file_size_kb", sa.Integer(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_url", name="uq_normativa_documento_source_url"),
    )
    op.create_index(
        "ix_normative_documenti_categoria_sub_slug",
        "normative_documenti",
        ["categoria_sub_slug"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_normative_documenti_categoria_sub_slug",
        table_name="normative_documenti",
    )
    op.drop_table("normative_documenti")
