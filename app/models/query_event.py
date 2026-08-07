import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from app.models.base import Base

class QueryEvent(Base):
    __tablename__ = "query_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_session.id"), nullable=False)
    query: Mapped[str] = mapped_column(String, nullable=False)
    cache_hit: Mapped[bool] = mapped_column(Boolean, nullable=False)
    retrieved_chunks: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))