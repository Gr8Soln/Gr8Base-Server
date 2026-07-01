from app.domain.port import VectorStorePort


class PgVectorStore(VectorStorePort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def search(self, query_vector, top_k=5):
        stmt = select(DocumentModel).order_by(
            DocumentModel.embedding.cosine_distance(query_vector)
        ).limit(top_k)
        rows = (await self._session.execute(stmt)).scalars().all()
        return [RetrievalResult(content=r.text, score=r.score) for r in rows]