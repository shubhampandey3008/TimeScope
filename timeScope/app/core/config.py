from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost/employee_monitoring"
    SQLITE_DATABASE_URL: str = "sqlite:///./employee_monitoring.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: List[str] = ["png", "jpg", "jpeg", "gif"]
    
    # AWS S3 (optional)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    
    # App Info
    APP_NAME: str = "Employee Monitoring API"
    APP_VERSION: str = "1.0.0"
    
    # Add debug field to handle the DEBUG environment variable
    debug: bool = False
    
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # This will ignore extra environment variables
    )

settings = Settings()