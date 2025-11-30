"""
Vector Retriever Service
Performs semantic search over book chapters using Qdrant
"""

import logging
from typing import Dict, List

from app.config import config
from app.services.embedder import embedder_service
from app.services.qdrant_client import qdrant_service

logger = logging.getLogger(__name__)


class RetrieverService:
    """
    Vector retrieval service for semantic search
    """

    def __init__(self):
        """Initialize retriever with config"""
        self.top_k = config.TOP_K_RESULTS
        self.score_threshold = config.SIMILARITY_THRESHOLD

    def retrieve_top_k_chunks(
        self, query: str, k: int | None = None, score_threshold: float | None = None
    ) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks for a query

        Args:
            query: User's question
            k: Number of results to return (default: from config)
            score_threshold: Minimum similarity score (default: from config)

        Returns:
            List of dicts with text, chapter_id, chapter_title, relevance_score
        """
        # Use provided values or fallback to config
        k = k or self.top_k
        score_threshold = score_threshold or self.score_threshold

        try:
            logger.info(f"Retrieving top-{k} chunks for query: '{query[:50]}...'")

            # Check if Qdrant is connected
            if not qdrant_service.client:
                raise RuntimeError(
                    "Qdrant client not connected. Please ensure QDRANT_URL and QDRANT_API_KEY are set."
                )

            # Generate query embedding
            query_embedding = embedder_service.embed_text(query)
            logger.debug(f"Generated query embedding ({len(query_embedding)} dims)")

            # Search Qdrant
            results = qdrant_service.search(
                query_vector=query_embedding, limit=k, score_threshold=score_threshold
            )

            # Format results
            chunks = []
            for result in results:
                chunk = {
                    "text": result.payload["text"],
                    "chapter_id": result.payload["chapter_id"],
                    "chapter_title": result.payload["chapter_title"],
                    "part": result.payload.get("part", "Unknown"),
                    "chunk_index": result.payload.get("chunk_index", 0),
                    "relevance_score": result.score,
                }
                chunks.append(chunk)

            logger.info(
                f"✅ Retrieved {len(chunks)} chunks above threshold {score_threshold}"
            )

            return chunks

        except Exception as e:
            logger.error(f"❌ Retrieval failed: {str(e)}")
            raise

    def retrieve_with_reranking(
        self,
        query: str,
        k: int | None = None,
        score_threshold: float | None = None,
        rerank_top_n: int = 10,
    ) -> List[Dict]:
        """
        Retrieve chunks with two-stage retrieval (retrieve more, then rerank)

        This is useful for improving precision by first retrieving a larger set
        and then reranking them (future enhancement: use cross-encoder)

        Args:
            query: User's question
            k: Final number of results to return
            score_threshold: Minimum similarity score
            rerank_top_n: Initial retrieval size (before reranking)

        Returns:
            Top-k reranked chunks
        """
        # For MVP, just retrieve top-k directly
        # Future: Add cross-encoder reranking for better precision
        logger.info(f"Reranking not implemented yet - using top-k retrieval")
        return self.retrieve_top_k_chunks(query, k, score_threshold)

    def get_retrieval_stats(self) -> Dict:
        """
        Get retrieval configuration and statistics

        Returns:
            Dict with config and collection info
        """
        try:
            collection_info = qdrant_service.get_collection_info()

            return {
                "config": {
                    "top_k": self.top_k,
                    "score_threshold": self.score_threshold,
                    "embedding_model": config.EMBEDDING_MODEL,
                    "collection_name": config.COLLECTION_NAME,
                },
                "collection": collection_info,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get retrieval stats: {str(e)}")
            raise


# Singleton instance
retriever_service = RetrieverService()
