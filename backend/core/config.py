"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Enterprise AI Integration Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/enterprise_ai"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_URL: str = "redis://localhost:6379/1"
    REDIS_CACHE_URL: str = "redis://localhost:6379/2"
    
    # Security
    SECRET_KEY: str = "change-me-in-production-use-env-variable"
    JWT_SECRET_KEY: str = "change-me-in-production-use-env-variable"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    
    # AI Providers
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LOCAL_AI_ENABLED: bool = False
    LOCAL_AI_URL: str = "http://localhost:11434"
    
    # Feature Flags
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    
    # Monitoring
    PROMETHEUS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None
    
    # ERP Integrations (optional)
    SAP_BASE_URL: Optional[str] = None
    SAP_API_KEY: Optional[str] = None
    SAP_USERNAME: Optional[str] = None
    SAP_PASSWORD: Optional[str] = None
    
    ORACLE_BASE_URL: Optional[str] = None
    ORACLE_API_KEY: Optional[str] = None
    ORACLE_USERNAME: Optional[str] = None
    ORACLE_PASSWORD: Optional[str] = None
    
    DYNAMICS_CLIENT_ID: Optional[str] = None
    DYNAMICS_CLIENT_SECRET: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # Vector Database
    VECTOR_DIMENSION: int = 1536  # OpenAI ada-002 / sentence-transformers default
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # AWS S3 (for document storage, optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()

