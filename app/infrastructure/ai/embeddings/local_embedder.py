from app.domain.port import EmbeddingPort


class SentenceTransformerEmbedder(EmbeddingPort):
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self._model = SentenceTransformer(model_name)
        self._embedding_dimention = 1234

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, convert_to_numpy=False).tolist()