from abc import ABC, abstractmethod
from typing import Any
from app.llm.types import LLMResponse

class BaseLLMProvider(ABC):

    @abstractmethod
    def generate_response(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        pass