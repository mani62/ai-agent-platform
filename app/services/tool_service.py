from app.ai.tools.registry import tool_registry
from app.models.tool import Tool
from app.repositories.tool_repository import ToolRepository


class ToolService:
    def __init__(self):
        self.tool_repository = ToolRepository()

    def sync_tools(self, db):
        tools = tool_registry.get_all()

        for tool in tools:
            existing_tool = self.tool_repository.get_by_name(
                db,
                tool.name,
            )

            if existing_tool is None:
                db_tool = Tool(
                    name=tool.name,
                    description=tool.description,
                    is_active=True,
                )

                self.tool_repository.create(
                    db,
                    db_tool,
                )

            else:
                existing_tool.description = tool.description

                self.tool_repository.save(
                    db,
                    existing_tool,
                )