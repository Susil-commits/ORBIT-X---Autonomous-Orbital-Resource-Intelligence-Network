"""Configuration and Environment Settings for ORBIT-X."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

try:
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        PROJECT_NAME: str = "ORBIT-X"
        VERSION: str = "2.0.0"

        # Database URL: Switch between Postgres asyncpg and SQLite aiosqlite
        DATABASE_URL: str = (
            f"sqlite+aiosqlite:///{BASE_DIR / 'orbitx.db'}"
        )

        # Redis URL for pub/sub & caching
        REDIS_URL: str = "redis://localhost:6379/0"

        # Local LLM Ollama URL
        OLLAMA_URL: str = "http://localhost:11434"
        OLLAMA_MODEL: str = "llama3.2"

        # Embedding Model for RAG
        EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

        # Paths
        DATA_PATH: Path = DATA_DIR
        MODELS_PATH: Path = MODELS_DIR
        REAL_CONSTELLATION_PATH: Path = DATA_DIR / "real_constellation.json"
        BID_NETWORK_PATH: Path = MODELS_DIR / "bid_network.pt"
        SHAP_SURROGATE_PATH: Path = MODELS_DIR / "shap_surrogate.json"

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"

except ImportError:
    # Fallback to plain BaseModel with manual os.getenv for environments without pydantic-settings
    from pydantic import BaseModel

    class Settings(BaseModel):  # type: ignore[no-redef]
        PROJECT_NAME: str = "ORBIT-X"
        VERSION: str = "2.0.0"

        DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            f"sqlite+aiosqlite:///{BASE_DIR / 'orbitx.db'}",
        )

        REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
        EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

        DATA_PATH: Path = DATA_DIR
        MODELS_PATH: Path = MODELS_DIR
        REAL_CONSTELLATION_PATH: Path = DATA_DIR / "real_constellation.json"
        BID_NETWORK_PATH: Path = MODELS_DIR / "bid_network.pt"
        SHAP_SURROGATE_PATH: Path = MODELS_DIR / "shap_surrogate.json"


settings = Settings()
