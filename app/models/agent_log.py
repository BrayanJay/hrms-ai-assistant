import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional

from app.models.base import Base

class AgentLog(Base):
    __tablename__ = "agent_log"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_session.id"), nullable=False)
    query: Mapped[str] = mapped_column(String, nullable=False)
    intent: Mapped[str] = mapped_column(String, nullable=False)
    router_decision: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tool_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tool_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tool_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    maker_checker_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))