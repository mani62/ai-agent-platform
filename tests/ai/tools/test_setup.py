from unittest.mock import patch

from app.ai.tools.setup import register_tools
from app.ai.tools.registry import tool_registry
from app.ai.tools.tavily import TavilyTool
from app.ai.tools.calculator import CalculatorTool


def test_register_tools_with_tavily(monkeypatch):
    monkeypatch.setattr(
        "app.ai.tools.setup.settings.TAVILY_API_KEY",
        "fake-api-key",
    )

    with patch("app.ai.tools.setup.TavilyClient") as mock_client:
        register_tools()

    calculator = tool_registry.get("calculator")
    tavily = tool_registry.get("tavily_search")

    assert isinstance(calculator, CalculatorTool)
    assert isinstance(tavily, TavilyTool)

    assert tavily.client is mock_client.return_value