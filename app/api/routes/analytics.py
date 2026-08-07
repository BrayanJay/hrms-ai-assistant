from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer
from datetime import datetime, timezone, timedelta

from app.models.query_event import QueryEvent
from app.api.dependencies import require_user
from app.core.database import get_db

router = APIRouter()

@router.get("/")
async def query_events(db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_user)):
    result = await db.execute(
        select(
            func.count(QueryEvent.id),
            func.avg(QueryEvent.cache_hit.cast(Integer)) * 100,
            func.avg(QueryEvent.response_time_ms)
        )
    )
    total, cache_hit_rate, avg_response_time = result.one()
    return {
        "total_queries": total or 0, 
        "cache_hit_rate": round(cache_hit_rate or 0, 1), 
        "avg_response_time_ms": avg_response_time
        }

@router.get("/daily")
async def daily_volume(db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_user)):
    since = datetime.now(timezone.utc) - timedelta(days=7)
    result = await db.execute(
        select(
            func.date(QueryEvent.created_at).label("date"),
            func.count(QueryEvent.id).label("count")
        )
        .where(QueryEvent.created_at >= since)
        .group_by(func.date(QueryEvent.created_at))
        .order_by(func.date(QueryEvent.created_at))
    )
    return [{"date": str(row.date), "count": row.count} for row in result.all()]

@router.get("/top-queries")
async def top_queries(db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_user)):
    result = await db.execute(
        select(
            QueryEvent.query,
            func.count(QueryEvent.id).label("count")
        )
        .group_by(QueryEvent.query)
        .order_by(func.count(QueryEvent.id).desc())
        .limit(10)
    )
    return [{"query": row.query, "count": row.count} for row in result.all()]