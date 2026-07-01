from app.domain.port import EmbeddingPort


class OpenAIEmbedder(EmbeddingPort):
    def __init__(self, client: AsyncOpenAI, model: str = "text-embedding-3-small"):
        self._client = client
        self._model = model
        self._embedding_dimention = 1234

    async def embed(self, texts: list[str]) -> list[list[float]]:
        res = await self._client.embeddings.create(model=self._model, input=texts)
        return [d.embedding for d in res.data]