from unittest.mock import Mock
import pytest

from app.ai.agents.runner import AgentRunner
from app.llm.types import LLMResponse, ToolCall

def test_runner_executes_calculator(
    active_agent,
    registered_tools,
    calculator_tool,
    db,
):
    active_agent.tools = [calculator_tool]
    db.commit()
    
    runner = AgentRunner()

    runner.llm_service.generate_response = Mock(
        side_effect=[
            LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        name="calculator",
                        arguments={
                            "expression": "25 * 2",
                        },
                    )
                ],
            ),
            LLMResponse(
                content="The result is 50.",
                tool_calls=[],
            ),
        ]
    )

    result = runner.run(
        agent=active_agent,
        history=[],
    )

    assert result == "The result is 50."

    assert (
        runner.llm_service.generate_response.call_count
        == 2
    )


def test_execute_unknown_tool():
    runner = AgentRunner()

    result = runner._execute_tool(
        tool_name="unknown",
        arguments={},
        allowed_tool_names={"unknown"},
    )

    assert result == "Error: Tool 'unknown' not found."


def test_execute_tool_handles_error(
    registered_tools,
):
    runner = AgentRunner()

    result = runner._execute_tool(
        tool_name="calculator",
        arguments={
            "expression": "hello",
        },
        allowed_tool_names={"calculator"},
    )

    assert result.startswith(
        "Error executing tool:"
    )


def test_runner_stops_after_max_iterations(
    active_agent,
    registered_tools,
    calculator_tool,
    db,
):
    active_agent.tools = [calculator_tool]
    db.commit()
    
    runner = AgentRunner()

    runner.llm_service.generate_response = Mock(
        return_value=LLMResponse(
            content=None,
            tool_calls=[
                ToolCall(
                    name="calculator",
                    arguments={
                        "expression": "2 + 2",
                    },
                )
            ],
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Agent exceeded maximum tool iterations",
    ):
        runner.run(
            agent=active_agent,
            history=[],
        )

    assert (
        runner.llm_service.generate_response.call_count
        == runner.MAX_ITERATIONS
    )

def test_execute_tool_not_allowed(
    registered_tools,
):
    runner = AgentRunner()

    result = runner._execute_tool(
        tool_name="calculator",
        arguments={
            "expression": "2 + 2",
        },
        allowed_tool_names=set(),
    )

    assert result == (
        "Error: Tool 'calculator' is not allowed for this agent."
    )    

def test_runner_sends_only_agent_tools_to_llm(
    active_agent,
    registered_tools,
):
    active_agent.tools = []

    runner = AgentRunner()

    runner.llm_service.generate_response = Mock(
        return_value=LLMResponse(
            content="Hello",
            tool_calls=[],
        )
    )

    result = runner.run(
        agent=active_agent,
        history=[],
    )

    assert result == "Hello"

    call_kwargs = (
        runner.llm_service.generate_response.call_args.kwargs
    )

    assert call_kwargs["tools"] == []    

def test_runner_sends_assigned_tool_to_llm(
    active_agent,
    calculator_tool,
    registered_tools,
    db,
):
    active_agent.tools = [calculator_tool]
    db.commit()

    runner = AgentRunner()

    runner.llm_service.generate_response = Mock(
        return_value=LLMResponse(
            content="Hello",
            tool_calls=[],
        )
    )

    runner.run(
        agent=active_agent,
        history=[],
    )

    call_kwargs = (
        runner.llm_service.generate_response.call_args.kwargs
    )

    tools = call_kwargs["tools"]

    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "calculator"    