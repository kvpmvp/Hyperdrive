from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "hyperdrive-backend")
    api_prefix: str = os.getenv("API_PREFIX", "/")
    db_url: str = os.getenv("DB_URL", "sqlite+aiosqlite:///./dev.db")
    cors_origins: List[str] = (os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","))

    algod_url: str = os.getenv("ALGOD_URL", "")
    algod_token: str = os.getenv("ALGOD_TOKEN", "")
    indexer_url: str = os.getenv("INDEXER_URL", "")
    indexer_token: str = os.getenv("INDEXER_TOKEN", "")
    network: str = os.getenv("NETWORK", "testnet")

settings = Settings()
