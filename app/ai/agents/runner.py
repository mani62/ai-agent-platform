from app.models.agent import Agent
from app.models.message import Message
from app.services.llm_service import LLMService

class AgentRunner:

    def __init__(self):
        self.llm_service = LLMService()

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

        return self.llm_service.generate_response(
            provider=agent.provider,
            model=agent.model,
            system_prompt=agent.system_prompt,
            messages=messages,
        )