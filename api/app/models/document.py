"""
Document and Chunk Models
Data structures for vector store indexing
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """
    Indexed book content for vector search
    Stored as Qdrant payload
    """

    chunk_id: str = Field(..., description="Unique identifier (UUID)")
    text: str = Field(..., min_length=1, description="Chunk content (1024 tokens)")
    chapter_id: str = Field(..., description="Parent chapter slug")
    chapter_title: str = Field(..., description="Human-readable chapter name")
    part: str = Field(..., description="Sidebar part (e.g., 'Core Technologies')")
    chunk_index: int = Field(..., ge=0, description="Position in chapter (0-indexed)")
    token_count: int = Field(..., gt=0, description="Exact token count (tiktoken)")
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "text": "ROS 2 is a middleware framework for building robot applications...",
                "chapter_id": "module-1/ros2-architecture",
                "chapter_title": "ROS 2 Architecture Overview",
                "part": "Core Technologies",
                "chunk_index": 0,
                "token_count": 1024,
                "created_at": "2025-11-30T12:00:00Z",
            }
        }


class EmbeddingVector(BaseModel):
    """
    Semantic representation for vector search
    1536-dimensional embedding from text-embedding-3-small
    """

    id: str = Field(..., description="Same as chunk_id in payload")
    vector: list[float] = Field(
        ..., min_length=1536, max_length=1536, description="1536-dimensional embedding"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "vector": [0.0234, -0.0145, 0.0892],  # Truncated for example
            }
        }


class IndexingResult(BaseModel):
    """Result of chapter indexing operation"""

    chapter_id: str
    chunks_created: int
    total_tokens: int
    success: bool
    error: Optional[str] = None
