from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import require_user
from app.core.logging import get_logger
from app.models.chat_session import ChatSession
from app.schemas.chat_session import ChatSessionResponse

router = APIRouter()
logger = get_logger(__name__)

@router.post("/", response_model=ChatSessionResponse)
async def chat_session(db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_user)):
    new_session = ChatSession(user_id=current_user["sub"])
    db.add(new_session)
    await db.flush()
    session_id = str(new_session.id)
    await db.commit()

    logger.info("chat session created", extra={"user_id": current_user["sub"], "session_id": session_id})
    return ChatSessionResponse(session_id=session_id)
    
