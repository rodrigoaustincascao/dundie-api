"""ensure_admin_user

Revision ID: 491f4464b587
Revises: 1ddf91223aba
Create Date: 2025-11-10 16:23:13.815145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from dundie.models.user import User
from sqlmodel import Session


# revision identifiers, used by Alembic.
revision: str = '491f4464b587'
down_revision: Union[str, None] = '1ddf91223aba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    admin = User(
        name="Admin",
        username="admin",
        email="admin@dm.com",
        dept="management",
        currency="USD",
        password="admin",  # pyright: ignore
    )
    # if admin user already exists it will raise IntegrityError
    try:
        session.add(admin)
        session.commit()
    except sa.exc.IntegrityError:
        session.rollback()



def downgrade() -> None:
    pass
