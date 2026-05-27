from abc import ABC, abstractmethod


class FileStoragePort(ABC):
    @abstractmethod
    async def upload(self, file_bytes: bytes, key: str, content_type: str) -> str:
        """Upload a file and return its storage URL."""
        ...

    @abstractmethod
    async def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a time-limited signed URL for private access."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a file from storage."""
        ...
