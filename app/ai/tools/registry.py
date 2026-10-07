from app.ai.tools.base import BaseTool

class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:
        self._tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> BaseTool | None:
        return self._tools.get(name)

    def get_all(
        self,
    ) -> list[BaseTool]:
        return list(self._tools.values())
    
    def get_schemas(
        self,
    ) -> list[dict]:
        return [
            tool.to_schema()
            for tool in self._tools.values()
        ]
    
tool_registry = ToolRegistry()    