from sqlalchemy.orm import Session

from app.ai.tools.setup import register_tools
from app.models.tool import Tool
from app.services.tool_service import ToolService


def test_sync_tools_creates_missing_tool(
    db: Session,
) -> None:
    register_tools()

    service = ToolService()

    service.sync_tools(db)

    tool = (
        db.query(Tool)
        .filter(Tool.name == "calculator")
        .first()
    )

    assert tool is not None
    assert tool.name == "calculator"
    assert tool.is_active is True

def test_sync_tools_updates_existing_tool(
    db: Session,
) -> None:
    register_tools()

    existing_tool = Tool(
        name="calculator",
        description="Old description",
        is_active=True,
    )

    db.add(existing_tool)
    db.commit()

    service = ToolService()

    service.sync_tools(db)

    tools = (
        db.query(Tool)
        .filter(Tool.name == "calculator")
        .all()
    )

    assert len(tools) == 1

    tool = tools[0]

    assert tool.description != "Old description"    