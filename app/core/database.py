from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(engine)

logger.info("database engine initialised", extra={"pool_size": 10, "max_overflow": 20})

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session