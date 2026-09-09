from app.ai.prompts.chat_title import CHAT_TITLE_SYSTEM_PROMPT
from app.llm.factory import LLMProviderFactory

class LLMService:

    def generate_response(
        self,
        provider: str,
        model: str,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[dict[str, any]] | None = None,
    ) -> str:

        llm_provider = LLMProviderFactory.get_provider(
            provider
        )

        return llm_provider.generate_response(
            model=model,
            system_prompt=system_prompt,
            messages=messages,
            tools=tools,
        )
    
    def generate_chat_title(
        self,
        provider: str,
        model: str,
        first_message: str,
    ) -> str:

        llm_provider = LLMProviderFactory.get_provider(
            provider
        )

        response  = llm_provider.generate_response(
            model=model,
            system_prompt=CHAT_TITLE_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": first_message,
                }
            ],
        )

        return response.content.strip()