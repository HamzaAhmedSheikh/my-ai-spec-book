"""
Text Chunking Utilities
Simple recursive text splitter for markdown content

Configuration:
- Chunk size: 512 tokens (for bge-small-en-v1.5)
- Overlap: 64 tokens (preserves context at boundaries)
- Splitters: Hierarchical (paragraphs > sentences > words)
"""

import logging
import re
from typing import List

import tiktoken

logger = logging.getLogger(__name__)


class BookChunker:
    """
    Text chunker optimized for technical book content
    Uses simple recursive splitting without external dependencies
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        encoding_name: str = "cl100k_base",
    ):
        """
        Initialize chunker with tiktoken encoding

        Args:
            chunk_size: Target chunk size in tokens (default: 512)
            chunk_overlap: Overlap between chunks in tokens (default: 64)
            encoding_name: Tiktoken encoding (default: cl100k_base)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens using tiktoken

        Args:
            text: Input text

        Returns:
            Token count
        """
        return len(self.encoding.encode(text))

    def _split_text(self, text: str) -> List[str]:
        """
        Recursively split text into chunks

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if not text.strip():
            return []

        # Try splitting by paragraphs first
        paragraphs = re.split(r"\n\n+", text)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if adding this paragraph would exceed chunk size
            test_chunk = current_chunk + "\n\n" + para if current_chunk else para
            token_count = self._count_tokens(test_chunk)

            if token_count <= self.chunk_size:
                # Add to current chunk
                current_chunk = test_chunk
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk)

                # If paragraph itself is too large, split by sentences
                if token_count > self.chunk_size:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue

                        test_chunk = (
                            current_chunk + " " + sentence
                            if current_chunk
                            else sentence
                        )
                        token_count = self._count_tokens(test_chunk)

                        if token_count <= self.chunk_size:
                            current_chunk = test_chunk
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = sentence
                else:
                    current_chunk = para

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk)

        # Add overlap between chunks
        if len(chunks) > 1 and self.chunk_overlap > 0:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i == 0:
                    overlapped_chunks.append(chunk)
                else:
                    # Get overlap from previous chunk
                    prev_tokens = self.encoding.encode(chunks[i - 1])
                    overlap_tokens = prev_tokens[-self.chunk_overlap :]
                    overlap_text = self.encoding.decode(overlap_tokens)

                    # Prepend overlap to current chunk
                    overlapped_chunk = overlap_text + " " + chunk
                    overlapped_chunks.append(overlapped_chunk)

            chunks = overlapped_chunks

        return chunks

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        chunks = self._split_text(text)
        logger.info(
            f"Chunked text ({len(text)} chars, {self._count_tokens(text)} tokens) into {len(chunks)} chunks"
        )
        return chunks

    def chunk_with_metadata(
        self, text: str, chapter_id: str, chapter_title: str, part: str
    ) -> List[dict]:
        """
        Split text into chunks with metadata

        Args:
            text: Input text to chunk
            chapter_id: Chapter slug (e.g., "module-1-ros2/chapter-1-introduction")
            chapter_title: Human-readable chapter name
            part: Sidebar part (e.g., "Core Technologies")

        Returns:
            List of dicts with chunk text and metadata
        """
        chunks = self.chunk_text(text)

        result = []
        for idx, chunk_text in enumerate(chunks):
            result.append(
                {
                    "text": chunk_text,
                    "chapter_id": chapter_id,
                    "chapter_title": chapter_title,
                    "part": part,
                    "chunk_index": idx,
                    "token_count": self._count_tokens(chunk_text),
                }
            )

        return result

    def validate_chunk_size(self, chunks: List[str]) -> bool:
        """
        Validate that all chunks are within size limits

        Args:
            chunks: List of text chunks

        Returns:
            True if all chunks are valid, False otherwise
        """
        for i, chunk in enumerate(chunks):
            token_count = self._count_tokens(chunk)
            if token_count > self.chunk_size * 1.2:  # Allow 20% overflow
                logger.warning(
                    f"Chunk {i} exceeds size limit: {token_count} tokens (max: {self.chunk_size})"
                )
                return False

        return True


# ============================================================================
# Singleton Instance (Default Configuration)
# ============================================================================

from app.config import config

book_chunker = BookChunker(
    chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP
)
