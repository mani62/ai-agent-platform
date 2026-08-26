from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "51e5edede088"
down_revision: Union[str, Sequence[str], None] = "28824b813ed4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


message_role_enum = postgresql.ENUM(
    "user",
    "assistant",
    name="message_role",
    create_type=False,
)


def upgrade() -> None:
    # Create PostgreSQL enum type
    message_role_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    # Convert VARCHAR column to enum
    op.alter_column(
        "messages",
        "role",
        existing_type=sa.String(length=20),
        type_=message_role_enum,
        existing_nullable=False,
        postgresql_using="role::text::message_role",
    )


def downgrade() -> None:
    # Convert enum back to VARCHAR
    op.alter_column(
        "messages",
        "role",
        existing_type=message_role_enum,
        type_=sa.String(length=20),
        existing_nullable=False,
        postgresql_using="role::text",
    )

    # Remove PostgreSQL enum type
    message_role_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )