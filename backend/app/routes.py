"""API route handlers for the Physical AI RAG chatbot.

This module defines FastAPI routes for:
- Health checks (/health)
- Global chat (/chat)
- Grounded chat (/chat/grounded)
- Content indexing (/index)

All endpoints include comprehensive error handling with appropriate HTTP status codes
and descriptive error messages (no stack traces in production).
"""

import logging
import sys

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from .models import (
    ChatRequest,
    ChatResponse,
    GroundedChatRequest,
    HealthResponse,
    IndexRequest,
    IndexResponse,
)
from .qdrant_client import qdrant_client, qdrant_client_instance
from .rag import chat_with_rag, grounded_chat

logger = logging.getLogger(__name__)


class ServiceUnavailableError(Exception):
    """Custom exception for service unavailability (Qdrant, OpenAI, etc.)."""

    pass


class InvalidInputError(Exception):
    """Custom exception for invalid user input."""

    pass


health_router = APIRouter()
chat_router = APIRouter()  # New router for chat endpoints
index_router = APIRouter()  # New router for indexing endpoints


@health_router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Checks the health of the application and its dependencies.
    """
    qdrant_connected = False
    try:
        qdrant_client = qdrant_client_instance.get_client()
        # Attempt to get collections to verify connectivity
        collections = qdrant_client.get_collections()
        logger.info(f"Qdrant collections: {[c.name for c in collections.collections]}")
        qdrant_connected = True
    except Exception as e:
        logger.error(f"Qdrant connection check failed: {e}")
        qdrant_connected = False

    if qdrant_connected:
        return HealthResponse(status="healthy", qdrant_connected=True)
    else:
        # Optionally return 503 if Qdrant is a critical dependency
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=HealthResponse(
                status="unhealthy", qdrant_connected=False
            ).model_dump(),
        )


@chat_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle global book question answering using RAG.

    Args:
        request: ChatRequest with user's question.

    Returns:
        ChatResponse with answer, sources, context, and latency.

    Raises:
        HTTPException: 400 for invalid input, 503 for service unavailable, 500 for internal errors.
    """
    try:
        logger.info(f"Processing chat request: {request.question[:50]}...")
        response = await chat_with_rag(request.question)
        logger.info(
            f"Chat response generated successfully (latency: {response.latency:.2f}s)"
        )

        return response
    except ValueError as ve:
        logger.warning(f"Invalid input in chat endpoint: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except ServiceUnavailableError as sue:
        logger.error(f"Service unavailable in chat endpoint: {sue}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later.",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error in chat endpoint: {e}", exc_info=True
        )  # Log with traceback
        # Don't expose internal error details in production
        error_detail = (
            "Internal server error"
            if "production" in sys.argv
            else f"Internal server error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail
        )


@chat_router.post("/chat/grounded", response_model=ChatResponse)
async def grounded_chat_endpoint(request: GroundedChatRequest):
    """Handle grounded question answering using user-selected text.

    Args:
        request: GroundedChatRequest with question and selected_text.

    Returns:
        ChatResponse with answer constrained to selected text.

    Raises:
        HTTPException: 400 for invalid input, 500 for internal errors.
    """
    try:
        logger.info(
            f"Processing grounded chat request: {request.question[:50]}... (text length: {len(request.selected_text)} chars)"
        )
        response = await grounded_chat(request.question, request.selected_text)
        logger.info(
            f"Grounded chat response generated successfully (latency: {response.latency:.2f}s)"
        )
        return response
    except ValueError as ve:
        logger.warning(f"Invalid input in grounded chat endpoint: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in grounded chat endpoint: {e}", exc_info=True)
        error_detail = (
            "Internal server error"
            if "production" in sys.argv
            else f"Internal server error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail
        )


@index_router.post("/index", response_model=IndexResponse)
async def index_content_endpoint(request: IndexRequest):
    """
    Triggers indexing of book content.
    """
    from .config import settings
    from .indexing import get_job_status, run_indexing_job

    # Check if an indexing job is already running
    job_statuses = get_job_status()
    for job_id, job_status in job_statuses.items():
        if job_status.status in ["running", "pending"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An indexing job (ID: {job_id}) is already in {job_status.status} state.",
            )

    try:
        # Run indexing synchronously for now, as per task.
        # In a real app, this might be offloaded to a background task/worker.
        response = await run_indexing_job(
            qdrant_client=qdrant_client,
            book_content_path=settings.BOOK_CONTENT_PATH,
            force_reindex=request.force_reindex,
        )
        print(settings.BOOK_CONTENT_PATH, "routes")
        return response
    except Exception as e:
        logger.error(f"Error in /index endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
