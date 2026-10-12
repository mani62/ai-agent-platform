from typing import Any

from app.ai.tools.base import BaseTool
from app.ai.clients.tavily import TavilyClient


class TavilyTool(BaseTool):

    def __init__(self, client: TavilyClient):
        self.client = client

    @property
    def name(self) -> str:
        return "tavily_search"

    @property
    def description(self) -> str:
        return (
            "Searches the web for current information, "
            "news, and recent events."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                }
            },
            "required": ["query"],
        }

    def execute(self, **kwargs: Any) -> str:
        query = kwargs.get("query")

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query is required")

        response = self.client.search(query=query)

        results = response.get("results", [])

        if not results:
            return "No search results found."

        formatted_results = []

        for result in results:
            formatted_results.append(
                f"Title: {result.get('title', '')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Content: {result.get('content', '')}"
            )

        return "\n\n".join(formatted_results)