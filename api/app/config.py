"""
Configuration Management
Loads and validates environment variables
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file from the project root
load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".env"
    )
)


class Config:
    """Application configuration from environment variables"""

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Anthropic Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Qdrant Configuration
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")

    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Model Configuration
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"  # FastEmbed model
    EMBEDDING_DIMENSIONS: int = 384  # bge-small-en-v1.5 dimensions
    LLM_MODEL: str = "gpt-5-nano-2025-08-07" # This will be overridden by llm_service
    LLM_TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 1000

    # Vector Search Configuration
    COLLECTION_NAME: str = "book_chapters"
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

    # Chunking Configuration
    CHUNK_SIZE: int = 512  # tokens (smaller for bge-small)
    CHUNK_OVERLAP: int = 64  # tokens

    @classmethod
    def validate(cls) -> None:
        """
        Validate required environment variables are set
        Raises ValueError if any required config is missing
        """
        logger.debug(f"Loaded QDRANT_URL: {cls.QDRANT_URL}")
        logger.debug(f"Loaded QDRANT_API_KEY: {cls.QDRANT_API_KEY}")

        missing_qdrant_vars = []
        if not cls.QDRANT_URL:
            missing_qdrant_vars.append("QDRANT_URL")
        if not cls.QDRANT_API_KEY:
            missing_qdrant_vars.append("QDRANT_API_KEY")

        if missing_qdrant_vars:
            error_msg = f"Missing required Qdrant environment variables: {', '.join(missing_qdrant_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            error_msg = "Either OPENAI_API_KEY or ANTHROPIC_API_KEY must be set in environment."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("✅ All required environment variables are set")

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT == "production"


# Create config instance
config = Config()

