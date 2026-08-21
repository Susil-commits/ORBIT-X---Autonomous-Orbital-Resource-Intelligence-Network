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

        # Redis URL for state caching, distributed locks & pub/sub
        REDIS_URL: str = "redis://localhost:6379/0"

        # Kafka Configuration
        KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
        KAFKA_GROUP_ID: str = "orbitx-cluster"
        KAFKA_CLIENT_ID: str = "orbitx-backend"

        # Security & JWT RBAC
        JWT_SECRET_KEY: str = "orbitx-dev-secret-key-32-chars-long-min!"
        JWT_ALGORITHM: str = "HS256"
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

        # Local LLM Ollama URL
        OLLAMA_URL: str = "http://localhost:11434"
        OLLAMA_MODEL: str = "llama3.2"

        # Embedding Model for RAG
        EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

        # Observability & Monitoring
        PROMETHEUS_METRICS_ENABLED: bool = True
        OPENTELEMETRY_ENABLED: bool = True
        OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

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
    from pydantic import BaseModel

    class Settings(BaseModel):  # type: ignore[no-redef]
        PROJECT_NAME: str = "ORBIT-X"
        VERSION: str = "2.0.0"

        DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            f"sqlite+aiosqlite:///{BASE_DIR / 'orbitx.db'}",
        )

        REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "orbitx-cluster")
        KAFKA_CLIENT_ID: str = os.getenv("KAFKA_CLIENT_ID", "orbitx-backend")

        JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "orbitx-dev-secret-key-32-chars-long-min!")
        JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

        OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
        EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

        PROMETHEUS_METRICS_ENABLED: bool = True
        OPENTELEMETRY_ENABLED: bool = True
        OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

        DATA_PATH: Path = DATA_DIR
        MODELS_PATH: Path = MODELS_DIR
        REAL_CONSTELLATION_PATH: Path = DATA_DIR / "real_constellation.json"
        BID_NETWORK_PATH: Path = MODELS_DIR / "bid_network.pt"
        SHAP_SURROGATE_PATH: Path = MODELS_DIR / "shap_surrogate.json"


settings = Settings()
