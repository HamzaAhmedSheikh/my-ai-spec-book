import glob
import os
from pathlib import Path  # New import
from typing import ClassVar, List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from the .env file
load_dotenv()

# Get the absolute path of the current file (config.py)
CURRENT_FILE_PATH = Path(__file__).resolve()
# Go up from config.py -> app -> backend -> project_root
PROJECT_ROOT = CURRENT_FILE_PATH.parents[2]

print(PROJECT_ROOT / "my-website/docs/physical-ai")


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OPENAI_API_KEY: str
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None

    BOOK_CONTENT_PATH: ClassVar[str] = str(
        PROJECT_ROOT / "my-website" / "docs" / "physical-ai"
    )

    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    QDRANT_COLLECTION_NAME: str = "ai-spec-book"

    @property
    def computed_cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",")]


settings = Settings()
