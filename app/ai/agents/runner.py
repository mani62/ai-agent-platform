from app.ai.tools.calculator import CalculatorTool
from app.ai.tools.registry import ToolRegistry
from app.models.agent import Agent
from app.models.message import Message
from app.services.llm_service import LLMService

class AgentRunner:

    MAX_ITERATIONS = 5

    def __init__(self):
        self.llm_service = LLMService()

        self.tool_registry = ToolRegistry()
        self.tool_registry.register(
            CalculatorTool()
        )

    def run(
        self,
        agent: Agent,
        history: list[Message],
    ) -> str:

        messages = [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in history
        ]

        tools = self.tool_registry.get_schemas()

        for _ in range(self.MAX_ITERATIONS):

            response = self.llm_service.generate_response(
                provider=agent.provider,
                model=agent.model,
                system_prompt=agent.system_prompt,
                messages=messages,
                tools=tools,
            )

            if not response.tool_calls:
                return response.content or ""

            for tool_call in response.tool_calls:

                result = self._execute_tool(
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                )

                messages.append(
                    {
                        "role": "assistant",
                        "content": (
                            f"Tool call: {tool_call.name} "
                            f"with arguments {tool_call.arguments}"
                        ),
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "content": result,
                    }
                )

        raise RuntimeError(
            "Agent exceeded maximum tool iterations"
        )        
    
    def _execute_tool(
        self,
        tool_name: str,
        arguments: dict,
    ) -> str:

        tool = self.tool_registry.get(
            tool_name
        )

        if tool is None:
            return f"Error: Tool '{tool_name}' not found."

        try:
            return tool.execute(
                **arguments
            )

        except Exception as exc:
            return f"Error executing tool: {exc}"