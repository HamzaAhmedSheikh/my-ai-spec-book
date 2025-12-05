from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class ChunkReference(BaseModel):
    source_document: str
    chunk_index: int
    text: str
    token_count: int
    title: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List["Source"] = Field(default_factory=list)
    latency: Optional[float] = None
    context: Optional[str] = None


class GroundedChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    selected_text: str = Field(..., min_length=1, max_length=10000)


class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool


class IndexRequest(BaseModel):
    force_reindex: bool = False


class IndexResponse(BaseModel):
    job_id: str
    status: str
    files_processed: int
    chunks_created: int
    timestamps: dict
    error: Optional[str] = None


class Source(BaseModel):
    chapter: int
    section: str
    page: Optional[str] = "N/A"
    relevance_score: Optional[float] = None
