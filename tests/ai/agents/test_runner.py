from unittest.mock import Mock
import pytest

from app.ai.agents.runner import AgentRunner
from app.llm.types import LLMResponse, ToolCall


def test_runner_executes_calculator(
    active_agent,
):
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
    )

    assert result == "Error: Tool 'unknown' not found."

def test_execute_tool_handles_error():
    runner = AgentRunner()

    result = runner._execute_tool(
        tool_name="calculator",
        arguments={
            "expression": "hello",
        },
    )

    assert result.startswith(
        "Error executing tool:"
    )      

def test_runner_stops_after_max_iterations(
    active_agent,
):
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