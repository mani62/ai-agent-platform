from app.ai.tools.calculator import CalculatorTool
from app.ai.tools.registry import ToolRegistry


def test_register_tool():
    registry = ToolRegistry()
    calculator = CalculatorTool()

    registry.register(calculator)

    tool = registry.get("calculator")

    assert tool is calculator


def test_get_unknown_tool():
    registry = ToolRegistry()

    tool = registry.get("unknown")

    assert tool is None


def test_get_all_tools():
    registry = ToolRegistry()
    calculator = CalculatorTool()

    registry.register(calculator)

    tools = registry.get_all()

    assert len(tools) == 1
    assert tools[0] is calculator

def test_get_schemas():
    registry = ToolRegistry()
    calculator = CalculatorTool()

    registry.register(calculator)

    schemas = registry.get_schemas()

    assert len(schemas) == 1
    assert schemas[0]["type"] == "function"
    assert schemas[0]["function"]["name"] == "calculator"
