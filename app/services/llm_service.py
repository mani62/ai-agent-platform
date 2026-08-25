from app.llm.factory import LLMProviderFactory

class LLMService:

    def generate_response(
        self,
        provider: str,
        model: str,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:

        llm_provider = LLMProviderFactory.get_provider(
            provider
        )

        return llm_provider.generate_response(
            model=model,
            system_prompt=system_prompt,
            messages=messages,
        )