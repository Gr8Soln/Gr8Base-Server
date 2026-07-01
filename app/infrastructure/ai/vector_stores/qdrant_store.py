from app.domain.port import VectorStorePort


class QdrantVectorStore(VectorStorePort):
    def __init__(self, client: QdrantClient, collection: str):
        self._client, self._collection = client, collection

    async def search(self, query_vector, top_k=5):
        hits = self._client.search(self._collection, query_vector, limit=top_k)
        return [RetrievalResult(content=h.payload["text"], score=h.score) for h in hits]