"""autenticazione

Revision ID: 0002_autenticazione
Revises: 0001_schema_iniziale
Create Date: 2026-08-03

Tabelle per il login via magic link e i refresh token JWT: entrambe
conservano solo l'hash del token, mai il valore in chiaro.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Identificatori della revisione, usati da Alembic.
revision: str = "0002_autenticazione"
down_revision: Union[str, None] = "0001_schema_iniziale"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- magic_link_tokens ---
    op.create_table(
        "magic_link_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("utente_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("scade_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usato_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("organizzazione_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["utente_id"], ["utenti.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["organizzazione_id"], ["organizzazioni.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_magic_link_token_hash"),
    )
    op.create_index(
        "ix_magic_link_tokens_utente_id", "magic_link_tokens", ["utente_id"], unique=False
    )
    op.create_index(
        "ix_magic_link_tokens_organizzazione_id",
        "magic_link_tokens",
        ["organizzazione_id"],
        unique=False,
    )
    op.create_index(
        "ix_magic_link_tokens_token_hash",
        "magic_link_tokens",
        ["token_hash"],
        unique=True,
    )

    # --- refresh_tokens ---
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("utente_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("scade_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revocato_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("organizzazione_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["utente_id"], ["utenti.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["organizzazione_id"], ["organizzazioni.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_refresh_token_hash"),
    )
    op.create_index(
        "ix_refresh_tokens_utente_id", "refresh_tokens", ["utente_id"], unique=False
    )
    op.create_index(
        "ix_refresh_tokens_organizzazione_id",
        "refresh_tokens",
        ["organizzazione_id"],
        unique=False,
    )
    op.create_index(
        "ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_organizzazione_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_utente_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ix_magic_link_tokens_token_hash", table_name="magic_link_tokens")
    op.drop_index(
        "ix_magic_link_tokens_organizzazione_id", table_name="magic_link_tokens"
    )
    op.drop_index("ix_magic_link_tokens_utente_id", table_name="magic_link_tokens")
    op.drop_table("magic_link_tokens")
