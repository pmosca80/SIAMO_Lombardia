"""login con password

Revision ID: 0003_login_password
Revises: 0002_autenticazione
Create Date: 2026-08-04

Sostituisce il login via magic link con email+password: aggiunge
`password_hash` e `email_verificato` a `utenti`, e rimpiazza
`magic_link_tokens` con `token_azione` (usata sia per la verifica email che
per il reset password, distinte dal campo `tipo`).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_login_password"
down_revision: Union[str, None] = "0002_autenticazione"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("utenti", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.add_column(
        "utenti",
        sa.Column(
            "email_verificato",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.drop_index("ix_magic_link_tokens_token_hash", table_name="magic_link_tokens")
    op.drop_index(
        "ix_magic_link_tokens_organizzazione_id", table_name="magic_link_tokens"
    )
    op.drop_index("ix_magic_link_tokens_utente_id", table_name="magic_link_tokens")
    op.drop_table("magic_link_tokens")

    tipo_token_azione = sa.Enum("verifica_email", "reset_password", name="tipo_token_azione")
    tipo_token_azione.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "token_azione",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("utente_id", sa.Integer(), nullable=False),
        sa.Column("tipo", tipo_token_azione, nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("scade_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usato_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("organizzazione_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["utente_id"], ["utenti.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["organizzazione_id"], ["organizzazioni.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_token_azione_token_hash"),
    )
    op.create_index(
        "ix_token_azione_utente_id", "token_azione", ["utente_id"], unique=False
    )
    op.create_index(
        "ix_token_azione_organizzazione_id",
        "token_azione",
        ["organizzazione_id"],
        unique=False,
    )
    op.create_index(
        "ix_token_azione_token_hash", "token_azione", ["token_hash"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_token_azione_token_hash", table_name="token_azione")
    op.drop_index("ix_token_azione_organizzazione_id", table_name="token_azione")
    op.drop_index("ix_token_azione_utente_id", table_name="token_azione")
    op.drop_table("token_azione")

    tipo_token_azione = sa.Enum("verifica_email", "reset_password", name="tipo_token_azione")
    tipo_token_azione.drop(op.get_bind(), checkfirst=True)

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
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
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

    op.drop_column("utenti", "email_verificato")
    op.drop_column("utenti", "password_hash")
