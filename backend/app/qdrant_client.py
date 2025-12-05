"""Qdrant client singleton for managing vector database connections."""

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from .config import settings

logger = logging.getLogger(__name__)


class QdrantClientSingleton:
    """Singleton class to ensure only one Qdrant client instance exists."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantClientSingleton, cls).__new__(cls)
            cls._instance.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
            cls._instance._create_collection_if_not_exists()
        return cls._instance

    # print(settings.QDRANT_URL, "hi")

    def _create_collection_if_not_exists(self):
        """Create the collection if it doesn't exist."""
        collection_name = "ai-spec-book"

        try:
            # Check if collection exists
            if self.client.collection_exists(collection_name=collection_name):
                logger.info(f"Collection '{collection_name}' already exists.")
            else:
                logger.info(
                    f"Collection '{collection_name}' does not exist. Creating it."
                )
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI text-embedding-3-small size
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Collection '{collection_name}' created successfully.")
        except Exception as create_error:
            logger.error(
                f"Failed to create collection '{collection_name}': {create_error}"
            )
            raise

    def get_client(self) -> QdrantClient:
        """Get the Qdrant client instance."""
        return self.client


# Initialize the singleton instance
qdrant_client_instance = QdrantClientSingleton()

# Export the actual QdrantClient for direct use
qdrant_client = qdrant_client_instance.get_client()
