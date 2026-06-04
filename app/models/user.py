from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    first_name: Mapped[str] = mapped_column(
        String,
        index=True
    )

    last_name: Mapped[str] = mapped_column(
        String,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )