from tavily import TavilyClient as TavilySDKClient

from app.core.config import settings

class TavilyClient:
    def __init__(self):
        if not settings.TAVILY_API_KEY:
            raise ValueError("Tavily API key is not configured")

        self.client = TavilySDKClient(
            api_key=settings.TAVILY_API_KEY
        )

    def search(self, query: str) -> dict:
        return self.client.search(
            query=query,
            search_depth="basic",
            max_results=5,
        )