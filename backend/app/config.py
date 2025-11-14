"""
Application configuration management.
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase
    supabase_url: str = os.getenv('SUPABASE_URL', '')
    supabase_key: str = os.getenv('SUPABASE_KEY', '')
    supabase_jwt_secret: str = os.getenv('SUPABASE_JWT_SECRET', '')
    
    # Google Gemini
    gemini_api_key: str = os.getenv('GEMINI_API_KEY', '')
    
    # Application
    environment: str = os.getenv('ENVIRONMENT', 'development')
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    api_host: str = os.getenv('API_HOST', '0.0.0.0')
    api_port: int = int(os.getenv('API_PORT', '8000'))
    
    # CORS
    cors_origins: str = os.getenv('CORS_ORIGINS', 'http://localhost:8501')
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',')]
        return self.cors_origins
    
    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '100'))
    
    class Config:
        env_file = '.env'
        case_sensitive = False
        extra = 'ignore'  # Ignore extra fields from .env
    
    def validate_required(self):
        """Validate required configuration."""
        required = {
            'supabase_url': self.supabase_url,
            'supabase_key': self.supabase_key,
            'gemini_api_key': self.gemini_api_key
        }
        
        missing = [k for k, v in required.items() if not v]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")


# Global settings instance
settings = Settings()
