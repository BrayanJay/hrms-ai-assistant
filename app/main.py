from app.core.config import settings
from app.core.logging import get_logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import documents, query, chat_sessions, analytics
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

logger = get_logger("app.errors")

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Log 4xx as warnings, 5xx as errors
    log_fn = logger.warning if exc.status_code < 500 else logger.error
    log_fn(
        "http exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "cause": exc.detail,
        },
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "request validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": 422,
            "cause": exc.errors(),
        },
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": 500,
            "cause": str(exc),
            "type": type(exc).__name__,
        },
        exc_info=exc,
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(query.router, prefix="/api/query", tags=["query"])
app.include_router(chat_sessions.router, prefix="/api/chat_session", tags=["chat_session"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/health")
async def health():
    return {"status": "ok"}
