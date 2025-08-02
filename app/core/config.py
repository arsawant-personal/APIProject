from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SaaS API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Super Admin
    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_PASSWORD: str
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_DETAILED_LOGGING: bool = False
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings() 