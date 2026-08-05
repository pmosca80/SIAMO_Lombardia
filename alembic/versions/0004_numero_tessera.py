"""numero tessera

Revision ID: 0004_numero_tessera
Revises: 0003_login_password
Create Date: 2026-08-05

Aggiunge `numero_tessera` a `utenti`: obbligatorio nel form di
autoregistrazione, ma nullable a livello di colonna perché gli utenti
creati da un amministratore possono non averlo ancora assegnato.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Identificatori della revisione, usati da Alembic.
revision: str = "0004_numero_tessera"
down_revision: Union[str, None] = "0003_login_password"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    colonne_utenti = {c["name"] for c in inspector.get_columns("utenti")}
    if "numero_tessera" not in colonne_utenti:
        op.add_column("utenti", sa.Column("numero_tessera", sa.String(length=50), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    colonne_utenti = {c["name"] for c in inspector.get_columns("utenti")}
    if "numero_tessera" in colonne_utenti:
        op.drop_column("utenti", "numero_tessera")
