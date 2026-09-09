from typing import Any
import httpx

from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.types import LLMResponse, ToolCall

class OllamaProvider(BaseLLMProvider):

    def generate_response(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:

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

        if tools:
            payload["tools"] = tools

        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=60.0,
        )

        response.raise_for_status()

        data = response.json()

        message = data["message"]

        tool_calls = []

        for tool_call in message.get("tool_calls", []):
            function = tool_call["function"]

            tool_calls.append(
                ToolCall(
                    name=function["name"],
                    arguments=function.get("arguments", {}),
                )
            )

        return LLMResponse(
            content=message.get("content") or None,
            tool_calls=tool_calls,
        )