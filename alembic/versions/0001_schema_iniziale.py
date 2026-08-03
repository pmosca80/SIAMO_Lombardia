"""schema iniziale

Revision ID: 0001_schema_iniziale
Revises:
Create Date: 2026-08-03

Crea le tabelle di base multi-tenant: organizzazioni (tenant radice),
membri e comunicazioni, con i relativi tipi ENUM Postgres.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_schema_iniziale"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizzazioni",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("attiva", sa.Boolean(), nullable=False),
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
    )
    op.create_index(
        "ix_organizzazioni_slug", "organizzazioni", ["slug"], unique=True
    )

    op.create_table(
        "membri",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("cognome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "ruolo",
            sa.Enum("AMMINISTRATORE", "OPERATORE", "SOCIO", name="ruolo_membro"),
            nullable=False,
        ),
        sa.Column("attivo", sa.Boolean(), nullable=False),
        sa.Column("organizzazione_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["organizzazione_id"], ["organizzazioni.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organizzazione_id", "email", name="uq_membro_org_email"
        ),
    )
    op.create_index(
        "ix_membri_organizzazione_id", "membri", ["organizzazione_id"], unique=False
    )

    op.create_table(
        "comunicazioni",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titolo", sa.String(length=255), nullable=False),
        sa.Column("corpo", sa.Text(), nullable=False),
        sa.Column(
            "canale",
            sa.Enum("EMAIL", "SMS", "AVVISO", name="canale_comunicazione"),
            nullable=False,
        ),
        sa.Column(
            "stato",
            sa.Enum("BOZZA", "INVIATA", name="stato_comunicazione"),
            nullable=False,
        ),
        sa.Column("autore_id", sa.Integer(), nullable=True),
        sa.Column("inviata_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("organizzazione_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["autore_id"], ["membri.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["organizzazione_id"], ["organizzazioni.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_comunicazioni_organizzazione_id",
        "comunicazioni",
        ["organizzazione_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_comunicazioni_organizzazione_id", table_name="comunicazioni"
    )
    op.drop_table("comunicazioni")
    op.drop_index("ix_membri_organizzazione_id", table_name="membri")
    op.drop_table("membri")
    op.drop_index("ix_organizzazioni_slug", table_name="organizzazioni")
    op.drop_table("organizzazioni")

    bind = op.get_bind()
    postgresql.ENUM(name="stato_comunicazione").drop(bind, checkfirst=True)
    postgresql.ENUM(name="canale_comunicazione").drop(bind, checkfirst=True)
    postgresql.ENUM(name="ruolo_membro").drop(bind, checkfirst=True)
