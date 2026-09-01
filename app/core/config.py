from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    #app
    model_config = SettingsConfigDict(env_file=".env")
    app_env: str
    allowed_origins: str

    #postgres
    database_url: str
    db_user: str
    db_password: str
    db_name: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    #qdrant vector db
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "hris_chatbot_chunks"

    #chunking
    threshold: int
    child_threshold: int

    #retrieval
    top_k_chunks: int
    retrieval_threshold: float

    #image optimisation
    max_image_size: int

    #redis cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # LLM
    llm_base_url: str
    llm_api_key: str = Field(
        validation_alias=AliasChoices("LLM_API_KEY", "OPENAI_API_KEY")
    )
    llm_model: str = Field(
        validation_alias=AliasChoices("LLM_MODEL", "OPENAI_MODEL")
    )

    # HR System API
    hr_api_base_url: str

    # History compaction
    history_compact_threshold: int = 8000
    history_keep_recent: int = 6

    # Google Translate
    google_translate_api_key: str
    translation_model_name: str

    #embedding model
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    embedding_dimension: int = 1024

    #frontend url
    next_public_api_url: str

    @property
    def openai_api_key(self) -> str:
        return self.llm_api_key

    @property
    def openai_model(self) -> str:
        return self.llm_model

    def get_allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


settings = Settings()