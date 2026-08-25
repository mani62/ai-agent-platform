from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):

    @abstractmethod
    def generate_response(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        pass