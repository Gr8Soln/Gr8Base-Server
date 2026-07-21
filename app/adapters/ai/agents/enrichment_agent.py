from app.application.ports.ai.enrichment_port import (
    CompanyEnrichment,
    EnrichmentPort,
)
from app.application.ports.ai.search_provider_port import SearchProviderPort
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


class EnrichmentAgent(EnrichmentPort):
    """Enriches extracted career data using web search.

    Uses a SearchProviderPort for web queries. Enrichment data is stored
    separately from canonical profile data — never overwrites user-provided info.
    """

    def __init__(self, search_provider: SearchProviderPort) -> None:
        self._search = search_provider

    async def enrich_companies(self, company_names: list[str]) -> dict[str, CompanyEnrichment]:
        result: dict[str, CompanyEnrichment] = {}
        for company in company_names:
            if not company.strip():
                continue
            try:
                search_result = await self._search.search_company(company)
                enrichment = CompanyEnrichment()
                if search_result.results:
                    snippet = search_result.results[0].snippet.lower()
                    # Simple heuristic extraction from search snippets
                    enrichment.description = search_result.results[0].snippet
                    if "industry" in snippet or "sector" in snippet:
                        enrichment.industry = _extract_field(snippet, "industry")
                    if "employees" in snippet or "size" in snippet:
                        enrichment.company_size = _extract_field(snippet, "size")
                    if "headquarters" in snippet or "based in" in snippet:
                        enrichment.headquarters = _extract_field(snippet, "headquarters")
                result[company] = enrichment
                logger.info("enrichment_company_done", company=company)
            except Exception as e:
                logger.warning("enrichment_company_failed", company=company, error=str(e))
                result[company] = CompanyEnrichment()
        return result

    async def enrich_technologies(self, technology_names: list[str]) -> dict[str, str]:
        result: dict[str, str] = {}
        for tech in technology_names:
            if not tech.strip():
                continue
            try:
                search_result = await self._search.search(
                    f"{tech} technology description", max_results=1
                )
                result[tech] = search_result.results[0].snippet if search_result.results else ""
            except Exception as e:
                logger.warning("enrichment_tech_failed", tech=tech, error=str(e))
                result[tech] = ""
        return result


def _extract_field(snippet: str, field: str) -> str:
    """Simple heuristic field extraction from search snippet."""
    lines = snippet.split(".")
    for line in lines:
        if field in line.lower():
            return line.strip()[:255]
    return ""
