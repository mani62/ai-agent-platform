from app.ai.clients.tavily import TavilyClient
from app.ai.tools.calculator import CalculatorTool
from app.ai.tools.tavily import TavilyTool
from app.ai.tools.registry import tool_registry
from app.core.config import settings


def register_tools() -> None:
    tool_registry.register(CalculatorTool())

    if settings.TAVILY_API_KEY:
        client = TavilyClient()
        tool_registry.register(TavilyTool(client=client))