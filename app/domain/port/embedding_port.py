from abc import ABC, abstractmethod

class EmbeddingPort(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        pass