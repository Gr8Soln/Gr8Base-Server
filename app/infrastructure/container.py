from functools import lru_cache

from lagom import Container


@lru_cache(maxsize=1)
def get_container() -> Container:
    container = Container()

    # ── Infrastructure ────────────────────────────────────────────────────────
    # Registered lazily — filled in as phases are implemented

    # ── AI Provider Ports ─────────────────────────────────────────────────────
    from app.adapters.ai.providers.llm_provider import LiteLLMProvider
    from app.application.ports.ai.llm_provider_port import LLMProviderPort

    container.define(LLMProviderPort, lambda: LiteLLMProvider())

    from app.adapters.ai.providers.openai_embedding_provider import OpenAIEmbeddingProvider
    from app.application.ports.ai.embedding_provider_port import EmbeddingProviderPort

    container.define(EmbeddingProviderPort, lambda: OpenAIEmbeddingProvider())

    from app.adapters.ai.providers.tavily_search_provider import TavilySearchProvider
    from app.application.ports.ai.search_provider_port import SearchProviderPort

    container.define(SearchProviderPort, lambda: TavilySearchProvider())

    from app.adapters.ai.providers.pgvector_store import PgVectorStore
    from app.application.ports.ai.vector_store_port import VectorStorePort

    container.define(VectorStorePort, lambda: PgVectorStore())

    # ── AI Agent Ports ────────────────────────────────────────────────────────
    from app.adapters.ai.agents.career_extractor_agent import CareerExtractorAgent
    from app.application.ports.ai.career_extractor_port import CareerExtractorPort

    container.define(CareerExtractorPort, lambda: CareerExtractorAgent())

    from app.adapters.ai.agents.enrichment_agent import EnrichmentAgent
    from app.application.ports.ai.enrichment_port import EnrichmentPort

    container.define(EnrichmentPort, lambda c: EnrichmentAgent(c.resolve(SearchProviderPort)))

    # ── Storage ───────────────────────────────────────────────────────────────
    from app.adapters.storage.r2_file_storage import R2FileStorage
    from app.application.ports.storage.file_storage_port import FileStoragePort

    container.define(FileStoragePort, lambda: R2FileStorage())

    # ── Event Bus ─────────────────────────────────────────────────────────────
    from app.adapters.events.in_memory_event_bus import get_event_bus
    from app.application.ports.events.event_bus_port import EventBusPort

    container.define(EventBusPort, lambda: get_event_bus())

    # ── Repositories ──────────────────────────────────────────────────────────
    # Repositories require a DB session — they are instantiated per-request
    # via the route layer rather than through the container.
    # The container definitions below are for non-session-dependent singletons.

    return container
