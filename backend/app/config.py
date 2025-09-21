from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator
import json

class Settings(BaseSettings):
    app_name: str = "hyperdrive-backend"
    api_prefix: str = "/api"
    db_url: str = "sqlite+aiosqlite:///./dev.db"

    # Keep raw env value as str
    cors_origins: str = ""  

    algod_url: str = ""
    algod_token: str = ""
    indexer_url: str = ""
    indexer_token: str = ""
    network: str = "testnet"

    # Expose a computed property that returns a clean list
    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            return []
        v = self.cors_origins.strip()
        if v.startswith("[") and v.endswith("]"):
            try:
                return json.loads(v)
            except Exception:
                pass
        return [i.strip() for i in v.split(",") if i.strip()]

    class Config:
        env_file = "backend/.env"
        env_file_encoding = "utf-8"

settings = Settings()
