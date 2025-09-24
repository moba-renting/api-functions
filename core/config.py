import logging
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings
from uvicorn.config import LOGGING_CONFIG

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_SERVICE_KEY: str = Field(..., env="SUPABASE_SERVICE_KEY")

    CLOUDINARY_CLOUD_NAME: str = Field(..., env="CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = Field(..., env="CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = Field(..., env="CLOUDINARY_API_SECRET")
    CLOUDINARY_SECURE: bool = Field(True, env="CLOUDINARY_SECURE")

    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"

try:
    settings = Settings()
except ValidationError as e:
    logger.error("Error loading settings: %s", e.json())
    raise

LOGGING_CONFIG["formatters"]["default"] = {
    "()": "uvicorn.logging.DefaultFormatter",
    "format": "%(levelprefix)s %(asctime)s - %(name)s - %(message)s",
}

LOGGING_CONFIG["formatters"]["access"] = LOGGING_CONFIG["formatters"]["default"]

LOGGING_CONFIG["loggers"][""] = {
    "level": "INFO",
    "handlers": ["default"],
    "propagate": True,
}
    

