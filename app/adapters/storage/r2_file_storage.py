import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.application.ports.storage.file_storage_port import FileStoragePort
from app.domain.exceptions.domain_exceptions import StorageError
from app.infrastructure.config.settings import get_settings
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)
settings = get_settings()


class R2FileStorage(FileStoragePort):
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
        self._bucket = settings.r2_bucket_name

    async def upload(self, file_bytes: bytes, key: str, content_type: str) -> str:
        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
            )
            url = f"{settings.r2_public_url}/{key}"
            logger.info("file_uploaded", key=key, size=len(file_bytes))
            return url
        except ClientError as e:
            raise StorageError(f"Upload failed for key '{key}': {e}") from e

    async def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            raise StorageError(f"Signed URL generation failed for key '{key}': {e}") from e

    async def delete(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
            logger.info("file_deleted", key=key)
        except ClientError as e:
            raise StorageError(f"Delete failed for key '{key}': {e}") from e
