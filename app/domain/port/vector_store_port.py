from abc import ABC, abstractmethod


class VectorStorePort(ABC):
    @abstractmethod
    async def upsert(self, docs: list[Document]) -> None:
        pass
   
    @abstractmethod
    async def search(self, query_vector: list[float], top_k: int) -> list[RetrievalResult]:
        pass


