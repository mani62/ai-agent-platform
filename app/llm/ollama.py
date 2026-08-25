import httpx

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):

    def generate_response(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                *messages,
            ],
            "stream": False,
        }

        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=60.0,
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]