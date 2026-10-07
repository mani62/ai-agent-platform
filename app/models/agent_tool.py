from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base


agent_tools = Table(
    "agent_tools",
    Base.metadata,

    Column(
        "agent_id",
        Integer,
        ForeignKey("agents.id", ondelete="CASCADE"),
        primary_key=True,
    ),

    Column(
        "tool_id",
        Integer,
        ForeignKey("tools.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)