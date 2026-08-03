"""schema iniziale

Revision ID: 0001_schema_iniziale
Revises:
Create Date: 2026-08-03

Schema completo multi-tenant: organizzazioni (tenant radice), campagne,
utenti, comunicazioni, documenti, letture, con i relativi tipi ENUM Postgres.
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
    # --- organizzazioni (tenant radice) ---
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

    # --- campagne ---
    op.create_table(
        "campagne",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("descrizione", sa.Text(), nullable=True),
        sa.Column(
            "stato",
            sa.Enum("PIANIFICATA", "ATTIVA", "CONCLUSA", name="stato_campagna"),
            nullable=False,
        ),
        sa.Column("data_inizio", sa.Date(), nullable=True),
        sa.Column("data_fine", sa.Date(), nullable=True),
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
            "organizzazione_id", "nome", name="uq_campagna_org_nome"
        ),
    )
    op.create_index(
        "ix_campagne_organizzazione_id", "campagne", ["organizzazione_id"], unique=False
    )

    # --- utenti ---
    op.create_table(
        "utenti",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("cognome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "ruolo",
            sa.Enum("AMMINISTRATORE", "OPERATORE", "SOCIO", name="ruolo_utente"),
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
            "organizzazione_id", "email", name="uq_utente_org_email"
        ),
    )
    op.create_index(
        "ix_utenti_organizzazione_id", "utenti", ["organizzazione_id"], unique=False
    )

    # --- comunicazioni ---
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
        sa.Column("campagna_id", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["campagna_id"], ["campagne.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["autore_id"], ["utenti.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["organizzazione_id"], ["organizzazioni.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_comunicazioni_campagna_id", "comunicazioni", ["campagna_id"], unique=False
    )
    op.create_index(
        "ix_comunicazioni_organizzazione_id",
        "comunicazioni",
        ["organizzazione_id"],
        unique=False,
    )

    # --- documenti ---
    op.create_table(
        "documenti",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome_file", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("dimensione_bytes", sa.BigInteger(), nullable=True),
        sa.Column("comunicazione_id", sa.Integer(), nullable=True),
        sa.Column("caricato_da_id", sa.Integer(), nullable=True),
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
            ["comunicazione_id"], ["comunicazioni.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["caricato_da_id"], ["utenti.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["organizzazione_id"], ["organizzazioni.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_documenti_comunicazione_id",
        "documenti",
        ["comunicazione_id"],
        unique=False,
    )
    op.create_index(
        "ix_documenti_organizzazione_id",
        "documenti",
        ["organizzazione_id"],
        unique=False,
    )

    # --- letture (ricevute di lettura) ---
    op.create_table(
        "letture",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("comunicazione_id", sa.Integer(), nullable=False),
        sa.Column("utente_id", sa.Integer(), nullable=False),
        sa.Column(
            "letto_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
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
            ["comunicazione_id"], ["comunicazioni.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["utente_id"], ["utenti.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["organizzazione_id"], ["organizzazioni.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "comunicazione_id", "utente_id", name="uq_lettura_comunicazione_utente"
        ),
    )
    op.create_index(
        "ix_letture_comunicazione_id", "letture", ["comunicazione_id"], unique=False
    )
    op.create_index(
        "ix_letture_organizzazione_id", "letture", ["organizzazione_id"], unique=False
    )
    op.create_index("ix_letture_utente_id", "letture", ["utente_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_letture_utente_id", table_name="letture")
    op.drop_index("ix_letture_organizzazione_id", table_name="letture")
    op.drop_index("ix_letture_comunicazione_id", table_name="letture")
    op.drop_table("letture")

    op.drop_index("ix_documenti_organizzazione_id", table_name="documenti")
    op.drop_index("ix_documenti_comunicazione_id", table_name="documenti")
    op.drop_table("documenti")

    op.drop_index(
        "ix_comunicazioni_organizzazione_id", table_name="comunicazioni"
    )
    op.drop_index("ix_comunicazioni_campagna_id", table_name="comunicazioni")
    op.drop_table("comunicazioni")

    op.drop_index("ix_utenti_organizzazione_id", table_name="utenti")
    op.drop_table("utenti")

    op.drop_index("ix_campagne_organizzazione_id", table_name="campagne")
    op.drop_table("campagne")

    op.drop_index("ix_organizzazioni_slug", table_name="organizzazioni")
    op.drop_table("organizzazioni")

    # Rimozione dei tipi ENUM (op.drop_table non li elimina automaticamente).
    bind = op.get_bind()
    postgresql.ENUM(name="stato_comunicazione").drop(bind, checkfirst=True)
    postgresql.ENUM(name="canale_comunicazione").drop(bind, checkfirst=True)
    postgresql.ENUM(name="ruolo_utente").drop(bind, checkfirst=True)
    postgresql.ENUM(name="stato_campagna").drop(bind, checkfirst=True)
