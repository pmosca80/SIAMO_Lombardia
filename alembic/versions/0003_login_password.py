"""login con password

Revision ID: 0003_login_password
Revises: 0002_autenticazione
Create Date: 2026-08-04

Sostituisce il login via magic link con email+password: aggiunge
`password_hash` e `email_verificato` a `utenti`, e rimpiazza
`magic_link_tokens` con `token_azione` (usata sia per la verifica email che
per il reset password, distinte dal campo `tipo`).

Ogni passo verifica lo stato attuale prima di agire: un primo deploy si è
interrotto a metà (tipo enum creato, tabella no) lasciando il DB in uno
stato intermedio, quindi la migrazione deve poter ripartire da lì senza
fallire su "already exists" / "does not exist".
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_login_password"
down_revision: Union[str, None] = "0002_autenticazione"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    colonne_utenti = {c["name"] for c in inspector.get_columns("utenti")}
    if "password_hash" not in colonne_utenti:
        op.add_column("utenti", sa.Column("password_hash", sa.String(length=255), nullable=True))
    if "email_verificato" not in colonne_utenti:
        op.add_column(
            "utenti",
            sa.Column(
                "email_verificato", sa.Boolean(), nullable=False, server_default=sa.true()
            ),
        )

    if inspector.has_table("magic_link_tokens"):
        indici_esistenti = {ix["name"] for ix in inspector.get_indexes("magic_link_tokens")}
        for nome_indice in (
            "ix_magic_link_tokens_token_hash",
            "ix_magic_link_tokens_organizzazione_id",
            "ix_magic_link_tokens_utente_id",
        ):
            if nome_indice in indici_esistenti:
                op.drop_index(nome_indice, table_name="magic_link_tokens")
        op.drop_table("magic_link_tokens")

    # Creazione del tipo idempotente. Su Postgres un blocco DO con except
    # esplicito è l'unico modo davvero affidabile: `Enum.create(checkfirst=True)`
    # e `create_type=False` sulla colonna non bastano a impedire che
    # `create_table` provi comunque a ricrearlo (fallendo su "already exists").
    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                "DO $$ BEGIN "
                "CREATE TYPE tipo_token_azione AS ENUM ('verifica_email', 'reset_password'); "
                "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
            )
        )
    else:
        sa.Enum(
            "verifica_email", "reset_password", name="tipo_token_azione"
        ).create(bind, checkfirst=True)

    if not inspector.has_table("token_azione"):
        # `create_type=False` è rispettato in modo affidabile solo sulla
        # classe dialect-specific `postgresql.ENUM`: su `sa.Enum` generico
        # `create_table` lo ignora e prova comunque a ricreare il tipo.
        if bind.dialect.name == "postgresql":
            tipo_colonna = postgresql.ENUM(
                "verifica_email",
                "reset_password",
                name="tipo_token_azione",
                create_type=False,
            )
        else:
            tipo_colonna = sa.Enum(
                "verifica_email", "reset_password", name="tipo_token_azione"
            )

        op.create_table(
            "token_azione",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("utente_id", sa.Integer(), nullable=False),
            sa.Column("tipo", tipo_colonna, nullable=False),
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
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("token_azione"):
        indici_esistenti = {ix["name"] for ix in inspector.get_indexes("token_azione")}
        for nome_indice in (
            "ix_token_azione_token_hash",
            "ix_token_azione_organizzazione_id",
            "ix_token_azione_utente_id",
        ):
            if nome_indice in indici_esistenti:
                op.drop_index(nome_indice, table_name="token_azione")
        op.drop_table("token_azione")

    tipo_token_azione = sa.Enum("verifica_email", "reset_password", name="tipo_token_azione")
    tipo_token_azione.drop(bind, checkfirst=True)

    if not inspector.has_table("magic_link_tokens"):
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

    colonne_utenti = {c["name"] for c in inspector.get_columns("utenti")}
    if "email_verificato" in colonne_utenti:
        op.drop_column("utenti", "email_verificato")
    if "password_hash" in colonne_utenti:
        op.drop_column("utenti", "password_hash")
