from app.core.config import get_settings

settings = get_settings()

def get_embedder() -> EmbeddingPort:
    return OpenAIEmbedder(client) if settings.EMBEDDER == "openai" else SentenceTransformerEmbedder()

def get_vector_store() -> VectorStorePort:
    return QdrantVectorStore(client, "docs") if settings.VECTOR_DB == "qdrant" else PgVectorStore(session)