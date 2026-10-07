from app.ai.tools.calculator import CalculatorTool
from app.ai.tools.registry import tool_registry


def register_tools() -> None:
    tool_registry.register(CalculatorTool())