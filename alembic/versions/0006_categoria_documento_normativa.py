"""categoria/documento normativa

Revision ID: 0006_categoria_documento_normativa
Revises: 0005_normative_documenti
Create Date: 2026-08-08

Sostituisce la tabella piatta `normative_documenti` (0005) con uno schema
normalizzato: `categoria_normativa` (self-referencing, macro e
sotto-categorie nella stessa tabella) e `documento_normativa` (FK alla
sotto-categoria). La tabella precedente non ha mai contenuto dati reali
(solo run di prova in --dry-run), quindi viene rimossa senza migrazione
dati.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Identificatori della revisione, usati da Alembic.
revision: str = "0006_categoria_documento_normativa"
down_revision: Union[str, None] = "0005_normative_documenti"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("normative_documenti")

    op.create_table(
        "categoria_normativa",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["categoria_normativa.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_categoria_normativa_slug"),
    )
    op.create_index(
        "ix_categoria_normativa_parent_id",
        "categoria_normativa",
        ["parent_id"],
        unique=False,
    )

    op.create_table(
        "documento_normativa",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("titolo", sa.String(length=500), nullable=False),
        sa.Column("data_pubblicazione", sa.Date(), nullable=True),
        sa.Column("file_path", sa.String(length=1024), nullable=True),
        sa.Column("file_size_kb", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.String(length=1024), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"], ["categoria_normativa.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_url", name="uq_documento_normativa_source_url"),
    )
    op.create_index(
        "ix_documento_normativa_categoria_id",
        "documento_normativa",
        ["categoria_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_documento_normativa_categoria_id", table_name="documento_normativa"
    )
    op.drop_table("documento_normativa")

    op.drop_index(
        "ix_categoria_normativa_parent_id", table_name="categoria_normativa"
    )
    op.drop_table("categoria_normativa")

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
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
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
