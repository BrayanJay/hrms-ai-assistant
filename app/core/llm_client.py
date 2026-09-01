from urllib.parse import urlparse, urlunparse

from openai import AsyncOpenAI

from app.core.config import settings


def _normalize_openai_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    path = parsed.path.rstrip("/")

    if not path:
        path = "/v1"
    elif not path.endswith("/v1"):
        path = f"{path}/v1"

    return urlunparse(parsed._replace(path=path))

llm_client = AsyncOpenAI(
    base_url=_normalize_openai_base_url(settings.llm_base_url),
    api_key=settings.llm_api_key,
)