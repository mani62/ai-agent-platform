from sqlalchemy import String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

class Agent(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=False
    )

    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="gpt-4.1-mini"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    owner= relationship(
        "User",
        back_populates="agents",
    )