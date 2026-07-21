import uuid

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class IngestionWorkflowModel(Base):
    __tablename__ = "ingestion_workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    source_file_key: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    source_file_name: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    source_file_url: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    error_message: Mapped[str] = mapped_column(Text, default="", nullable=False)
    events: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
