"""
Qdrant Vector Store Client
Wrapper for Qdrant operations with connection validation
"""

import logging
import os
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import config

logger = logging.getLogger(__name__)

# QDRANT_API_KEY and QDRANT_URL are now sourced from app.config.config
# QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
# QDRANT_URL: str = os.getenv("QDRANT_URL", "")


class QdrantService:
    """
    Qdrant client wrapper for vector store operations
    """

    def __init__(self):
        """Initialize Qdrant client with configuration"""
        self.client: Optional[QdrantClient] = None
        self.collection_name = config.COLLECTION_NAME

    def connect(self) -> None:
        """
        Establish connection to Qdrant Cloud
        Validates API key and URL according to Qdrant Cloud documentation

        Note: Qdrant Cloud URLs should be in format:
        https://your-cluster-id.cloud-region.cloud-provider.cloud.qdrant.io

        API keys can be passed via 'api_key' parameter or 'Authorization: Bearer' header
        """

        try:
            # Initialize Qdrant client with Cloud credentials
            # According to Qdrant docs: api_key parameter is supported by all official clients
            self.client = QdrantClient(
                url=config.QDRANT_URL,
                api_key=config.QDRANT_API_KEY,
                timeout=30.0,  # Increased timeout for Cloud connections
            )

            # Test connection by getting cluster info (more reliable than collections)
            # This validates both URL and API key
            cluster_info = self.client.get_collections()
            logger.info(
                f"✅ Connected to Qdrant Cloud - "
                f"{len(cluster_info.collections)} existing collections found"
            )
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                logger.error(
                    "❌ Authentication failed. Please check your QDRANT_API_KEY. "
                    "Get your API key from: https://cloud.qdrant.io"
                )
            elif "url" in error_msg.lower() or "connection" in error_msg.lower():
                logger.error(
                    "❌ Connection failed. Please check your QDRANT_URL. "
                    "Format should be: https://your-cluster-id.cloud-region.cloud-provider.cloud.qdrant.io"
                )
            else:
                logger.error(f"❌ Failed to connect to Qdrant Cloud: {error_msg}")
            raise

    def create_collection_if_not_exists(self) -> None:
        """
        Create book_chapters collection if it doesn't exist
        Uses BAAI/bge-small-en-v1.5 dimensions (384) and cosine distance
        """
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call connect() first.")

        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return

            # Create collection with correct dimensions for bge-small-en-v1.5
            from app.config import config

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=config.EMBEDDING_DIMENSIONS,  # 384 for bge-small-en-v1.5
                    distance=Distance.COSINE,  # Cosine similarity
                ),
            )
            logger.info(
                f"✅ Created collection '{self.collection_name}' with {config.EMBEDDING_DIMENSIONS} dimensions"
            )

        except Exception as e:
            logger.error(f"❌ Failed to create collection: {str(e)}")
            raise

    def search(
        self, query_vector: list[float], limit: int = 5, score_threshold: float = 0.7
    ):
        """
        Search for similar chunks in vector store

        Args:
            query_vector: Embedding vector (384 dimensions for bge-small-en-v1.5)
            limit: Maximum number of results (default: 5)
            score_threshold: Minimum similarity score (default: 0.7, range: 0.0-1.0)

        Returns:
            List of search results with payloads and similarity scores
        """
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call connect() first.")

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )
            logger.info(
                f"Found {len(results)} results above threshold {score_threshold}"
            )
            return results

        except Exception as e:
            logger.error(f"❌ Search failed: {str(e)}")
            raise

    def upsert_points(self, points: list[PointStruct]) -> None:
        """
        Insert or update points in collection

        Args:
            points: List of PointStruct with id, vector, and payload
        """
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call connect() first.")

        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"✅ Upserted {len(points)} points to collection")

        except Exception as e:
            logger.error(f"❌ Upsert failed: {str(e)}")
            raise

    def get_collection_info(self) -> dict:
        """Get collection statistics"""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized. Call connect() first.")

        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get collection info: {str(e)}")
            raise


# Singleton instance
qdrant_service = QdrantService()
