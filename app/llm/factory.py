from app.llm.base import BaseLLMProvider
from app.llm.ollama import OllamaProvider

class LLMProviderFactory:

    @staticmethod
    def get_provider(
        provider: str,
    ) -> BaseLLMProvider:

        if provider == "ollama":
            return OllamaProvider()

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )