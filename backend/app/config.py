from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Text2SQL API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # LLM Configuration (Anthropic)
    # LLM key optional for non-LLM flows; set in .env when needed
    ANTHROPIC_API_KEY: str = ""
    MODEL_NAME: str = "claude-3-haiku-20240307"
    LLM_TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 2000
    
    # HuggingFace Configuration (Optional)
    HUGGINGFACE_API_KEY: str = ""
    
    # Vector Database
    VECTOR_DB_TYPE: str = "chromadb"
    VECTOR_DB_PATH: str = "./data/vector_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Database
    DATABASE_URL: str = ""
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600
    
    # API Configuration
    MAX_QUERY_LENGTH: int = 500
    API_RATE_LIMIT: int = 100
    # Allow local dev hosts by default; override via .env if needed
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
