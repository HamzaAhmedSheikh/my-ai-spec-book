"""
FastEmbed Embedder Service
Generates embeddings using BAAI/bge-small-en-v1.5 via FastEmbed
"""

import logging
from typing import List, Optional

import numpy as np
from fastembed import TextEmbedding

from app.config import config

logger = logging.getLogger(__name__)


class EmbedderService:
    """
    FastEmbed embedding generator
    Uses BAAI/bge-small-en-v1.5 model (384 dimensions)
    """

    def __init__(self):
        """Initialize FastEmbed model"""
        self.model = None
        self.model_name = config.EMBEDDING_MODEL
        self.dimensions = config.EMBEDDING_DIMENSIONS

    def initialize(self) -> None:
        """
        Initialize FastEmbed model
        Downloads model on first use if not cached
        """
        try:
            # Initialize FastEmbed with the specified model
            self.model = TextEmbedding(model_name=self.model_name)
            logger.info(
                f"✅ FastEmbed initialized - model: {self.model_name} ({self.dimensions} dimensions)"
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize FastEmbed: {str(e)}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            384-dimensional embedding vector as list of floats
        """
        if not self.model:
            raise RuntimeError("Embedder not initialized. Call initialize() first.")

        try:
            # FastEmbed returns an iterator, convert to list
            embeddings = list(self.model.embed([text]))
            embedding = embeddings[0].tolist()  # Convert numpy array to list
            logger.debug(f"Generated embedding for text (length: {len(text)} chars)")
            return embedding

        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {str(e)}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (each 384 dimensions)
        """
        if not self.model:
            raise RuntimeError("Embedder not initialized. Call initialize() first.")

        try:
            # FastEmbed handles batching efficiently
            embeddings = list(self.model.embed(texts))
            # Convert numpy arrays to lists
            embeddings_list = [emb.tolist() for emb in embeddings]
            logger.info(f"✅ Generated {len(embeddings_list)} embeddings in batch")
            return embeddings_list

        except Exception as e:
            logger.error(f"❌ Batch embedding generation failed: {str(e)}")
            raise

    def get_model_info(self) -> dict:
        """Get information about the embedding model"""
        return {
            "model": self.model_name,
            "dimensions": self.dimensions,
            "provider": "FastEmbed",
            "library": "fastembed",
        }


# Singleton instance
embedder_service = EmbedderService()
