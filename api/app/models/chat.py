"""
Chat API Models
Pydantic models for /chat and /chat/grounded endpoints
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """
    Request model for global context chat (full-book search)
    POST /chat
    """

    query: str = Field(
        ..., min_length=3, max_length=1000, description="User's question about the book"
    )
    conversation_id: Optional[str] = Field(
        None, description="Optional session identifier for multi-turn conversations"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean query string"""
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace")
        return v.strip()


class GroundedChatRequest(BaseModel):
    """
    Request model for grounded context chat (selected text mode)
    POST /chat/grounded
    """

    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="User's question about the selected text",
    )
    selected_text: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Text highlighted by user from book page",
    )
    source_chapter: Optional[str] = Field(
        None, description="Chapter slug where text was selected (optional metadata)"
    )
    conversation_id: Optional[str] = Field(
        None, description="Optional session identifier"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean query string"""
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace")
        return v.strip()

    @field_validator("selected_text")
    @classmethod
    def validate_selection(cls, v: str) -> str:
        """Validate selected text meets minimum requirements"""
        cleaned = v.strip()
        word_count = len(cleaned.split())
        if word_count < 5:
            raise ValueError(
                f"Selected text too short (minimum 5 words, got {word_count})"
            )
        return cleaned


class SourceCitation(BaseModel):
    """Reference to book chapter where information was retrieved"""

    chapter: str = Field(
        ...,
        min_length=1,
        description="Chapter slug (e.g., 'module-1/ros2-architecture')",
    )
    title: str = Field(..., min_length=1, description="Human-readable chapter title")
    relevance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score (0.0-1.0, higher = more relevant)",
    )


class ChatResponse(BaseModel):
    """
    Response model for both /chat and /chat/grounded endpoints
    """

    answer: str = Field(..., min_length=1, description="LLM-generated response")
    sources: list[SourceCitation] = Field(
        default_factory=list, description="Chapter citations (global mode only)"
    )
    grounded_in: Optional[str] = Field(
        None, description="Confirmation of selected text (grounded mode only)"
    )
    conversation_id: str = Field(..., description="Session identifier")
    grounded: bool = Field(
        ...,
        description="Whether response used selected text (true) or full-book search (false)",
    )
    retrieved_chunks: Optional[list[dict]] = Field(None, description="Raw chunks retrieved from Qdrant (no LLM processing)")


class HealthResponse(BaseModel):
    """Health check response - GET /health"""

    status: str = Field(..., description="API health status")
    version: str = Field(..., description="API version (semver)")
    timestamp: Optional[str] = Field(None, description="Current server time (ISO 8601)")


class ErrorResponse(BaseModel):
    """Generic error response"""

    detail: str = Field(..., description="Error message")
