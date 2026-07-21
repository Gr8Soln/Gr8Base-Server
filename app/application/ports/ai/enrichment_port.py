from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CompanyEnrichment:
    industry: str = ""
    company_size: str = ""
    products: list[str] = field(default_factory=list)
    technology_focus: list[str] = field(default_factory=list)
    description: str = ""
    headquarters: str = ""
    founded: str = ""


@dataclass
class EnrichmentResult:
    company_enrichments: dict[str, CompanyEnrichment] = field(default_factory=dict)
    technology_details: dict[str, str] = field(default_factory=dict)


class EnrichmentPort(ABC):
    """Abstract port for AI-powered data enrichment via web search.

    Enriches extracted career data with external information.
    Never overwrites user-provided data — enrichment is stored separately.
    """

    @abstractmethod
    async def enrich_companies(
        self, company_names: list[str]
    ) -> dict[str, CompanyEnrichment]:
        """Search and enrich company information (industry, size, products, tech focus)."""
        ...

    @abstractmethod
    async def enrich_technologies(
        self, technology_names: list[str]
    ) -> dict[str, str]:
        """Search and enrich technology descriptions."""
        ...
