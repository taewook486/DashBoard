"""
Configuration management using Pydantic Settings.
@SPEC:IMPROVE-001 REQ-SEC-001
@MX:ANCHOR: Central configuration - all environment variables loaded here
@MX:REASON: Single source of truth for application configuration
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic for validation and type conversion.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore',  # Allow extra fields from .env file
    )

    # Flask Configuration
    FLASK_ENV: str = Field(default='development', description='Flask environment')
    FLASK_DEBUG: bool = Field(default=False, description='Flask debug mode')
    SECRET_KEY: str = Field(default='dev-secret-key-change-in-production',
                           description='Flask secret key')

    # Server Configuration
    HOST: str = Field(default='0.0.0.0', description='Server host')
    PORT: int = Field(default=5001, description='Server port')

    # Logging Configuration
    LOG_LEVEL: str = Field(default='INFO', description='Logging level')
    LOG_FORMAT: str = Field(default='json', description='Log format (json or console)')

    # CORS Configuration
    CORS_ENABLED: bool = Field(default=True, description='Enable CORS')
    ALLOWED_ORIGINS: str = Field(
        default='*',
        description='Allowed CORS origins (comma-separated)'
    )

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = Field(default=True, description='Enable rate limiting')
    RATE_LIMIT_DEFAULT: str = Field(default='100 per minute',
                                    description='Default rate limit')
    RATE_LIMIT_STORAGE: str = Field(default='memory://',
                                    description='Rate limit storage URI')

    # Cache Configuration
    CACHE_TTL_SECONDS: int = Field(default=300, description='Cache TTL in seconds')
    CACHE_ENABLED: bool = Field(default=True, description='Enable caching')

    # External API Keys (optional - loaded from .env if present)
    OPENAI_API_KEY: Optional[str] = Field(default=None, description='OpenAI API key')
    GEMINI_API_KEY: Optional[str] = Field(default=None, description='Gemini API key')
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description='Google API key')
    FRED_API_KEY: Optional[str] = Field(default=None, description='FRED API key')

    # Application Metadata
    VERSION: str = Field(default='1.0.0', description='Application version')
    APP_NAME: str = Field(default='DashBoard', description='Application name')

    @field_validator('FLASK_ENV')
    @classmethod
    def validate_env(cls, v: str) -> str:
        """Validate FLASK_ENV is one of allowed values."""
        allowed = ['development', 'production', 'testing']
        if v not in allowed:
            raise ValueError(f'FLASK_ENV must be one of {allowed}')
        return v

    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate LOG_LEVEL is one of allowed values."""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f'LOG_LEVEL must be one of {allowed}')
        return v_upper


class Config:
    """
    Flask configuration class that wraps Pydantic Settings.
    Provides Flask-compatible configuration interface.
    """

    def __init__(self):
        self._settings = Settings()

    def __getitem__(self, key: str):
        """Allow dict-like access for Flask compatibility."""
        return getattr(self._settings, key, None)

    def get(self, key: str, default=None):
        """Get configuration value with default."""
        return getattr(self._settings, key, default)

    def __getattr__(self, name: str):
        """Delegate attribute access to settings."""
        return getattr(self._settings, name)

    # Flask-required properties
    @property
    def DEBUG(self) -> bool:
        return self._settings.FLASK_DEBUG

    @property
    def SECRET_KEY(self) -> str:
        return self._settings.SECRET_KEY

    @property
    def ENV(self) -> str:
        return self._settings.FLASK_ENV

    @property
    def TESTING(self) -> bool:
        return self._settings.FLASK_ENV == 'testing'


# Development configuration
class DevelopmentConfig(Config):
    """Development environment configuration."""
    pass


# Production configuration
class ProductionConfig(Config):
    """Production environment configuration."""

    def __init__(self):
        super().__init__()
        if self._settings.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError(
                "SECRET_KEY must be set in production environment! "
                "Set the SECRET_KEY environment variable."
            )


# Testing configuration
class TestingConfig(Config):
    """Testing environment configuration."""

    def __init__(self):
        super().__init__()
        self._settings.FLASK_ENV = 'testing'
        self._settings.FLASK_DEBUG = True


def get_config() -> Config:
    """
    Get the appropriate configuration based on FLASK_ENV.
    """
    env = os.environ.get('FLASK_ENV', 'development').lower()

    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }

    return config_map.get(env, Config)()
