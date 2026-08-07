import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional

from app.models.base import Base

class ChatSession(Base):
    __tablename__ = "chat_session"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    topic: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    llm_call_count: Mapped[int] = mapped_column(Integer, default=0)
    answer_accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    chat_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    chat_ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)