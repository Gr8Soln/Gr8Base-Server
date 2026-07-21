import httpx

from app.application.ports.ai.search_provider_port import (
    SearchProviderPort,
    SearchResponse,
    SearchResult,
)
from app.infrastructure.config.settings import get_settings
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)
settings = get_settings()

TAVILY_API_URL = "https://api.tavily.com/search"


class TavilySearchProvider(SearchProviderPort):
    """Tavily web search provider.

    Uses the Tavily Search API for web search operations.
    Configured via TAVILY_API_KEY environment variable.
    """

    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key or getattr(settings, "tavily_api_key", "")

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: list[str] | None = None,
    ) -> SearchResponse:
        if not self._api_key:
            logger.warning("tavily_no_api_key", query=query)
            return SearchResponse(query=query)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload: dict = {
                    "api_key": self._api_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic",
                }
                if include_domains:
                    payload["include_domains"] = include_domains

                response = await client.post(TAVILY_API_URL, json=payload)
                response.raise_for_status()
                data = response.json()

                results = [
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        snippet=r.get("content", ""),
                        score=r.get("score", 0.0),
                    )
                    for r in data.get("results", [])
                ]
                logger.info("tavily_search_done", query=query, results=len(results))
                return SearchResponse(
                    query=query,
                    results=results,
                    total_results=len(results),
                )
        except Exception as e:
            logger.error("tavily_search_failed", query=query, error=str(e))
            return SearchResponse(query=query)

    async def search_company(self, company_name: str) -> SearchResponse:
        """Search for company information."""
        query = f"{company_name} company industry size products technology focus"
        return await self.search(query, max_results=3)
