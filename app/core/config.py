from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #app
    model_config = SettingsConfigDict(env_file=".env")
    app_env: str

    #frontend
    frontend_url: str

    #postgres
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    #qdrant vector db
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "astrynox_chunks"

    #redis cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    #openai api
    openai_api_key: str
    openai_model: str = "gpt-4o"

    #embedding model
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    embedding_dimension: int = 1024

    #resend mail service
    resend_api_key: str
    resend_from_email: str

    #google OAuth service
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

settings = Settings()