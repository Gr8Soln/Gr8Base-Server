from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    score: float = 0.0


@dataclass
class SearchResponse:
    query: str
    results: list[SearchResult] = field(default_factory=list)
    total_results: int = 0


class SearchProviderPort(ABC):
    """Abstract port for web search operations.

    Provider-independent — supports Tavily, SerpAPI, Brave, etc.
    """

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: list[str] | None = None,
    ) -> SearchResponse:
        """Execute a web search and return structured results."""
        ...

    @abstractmethod
    async def search_company(self, company_name: str) -> SearchResponse:
        """Search for company information (industry, size, products, tech focus)."""
        ...
