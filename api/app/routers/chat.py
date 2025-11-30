"""
Chat Router
API endpoints for RAG chatbot

Endpoints:
- POST /chat - Global context mode (full-book search with citations)
- POST /chat/grounded - Selected text mode (Magna Carta feature)
"""

import logging

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse, GroundedChatRequest
from app.services.llm import llm_service
from app.services.retriever import retriever_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["chat"],
)


@router.post("/chat", response_model=ChatResponse)
async def chat_global(request: ChatRequest):
    """
    Global context chat endpoint (full-book search mode)

    This endpoint searches the entire book using vector search and synthesizes
    an answer from the top-k most relevant chunks.

    Args:
        request: ChatRequest with query

    Returns:
        ChatResponse with synthesized answer and source citations

    Raises:
        HTTPException 500: If retrieval or LLM service fails
    """
    try:
        logger.info(f"Global chat request - query: '{request.query[:50]}...'")

        # Retrieve relevant chunks from vector store
        retrieved_chunks = retriever_service.retrieve_top_k_chunks(
            query=request.query,
            k=5,  # Top-5 chunks per plan.md
            score_threshold=0.7,  # Minimum similarity threshold
        )

        logger.info(f"Retrieved {len(retrieved_chunks)} chunks from vector store")

        # Generate response using LLM service with retrieved context
        result = llm_service.generate_global_response(
            query=request.query,
            retrieved_chunks=retrieved_chunks,
            conversation_id=request.conversation_id,
        )

        # Convert to ChatResponse model
        response = ChatResponse(
            answer=result["answer"],
            sources=[],
            conversation_id=result["conversation_id"],
            grounded=result["grounded"],
            retrieved_chunks=result["retrieved_chunks"],
        )

        logger.info(
            f"✅ Global response generated - conversation_id: {response.conversation_id}, "
            f"sources: {len(response.sources)}"
        )

        return response

    except Exception as e:
        logger.error(f"❌ Global chat failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate response: {str(e)}"
        )


@router.post("/chat/grounded", response_model=ChatResponse)
async def chat_grounded(request: GroundedChatRequest):
    """
    Grounded context chat endpoint (Magna Carta mode)

    This endpoint answers questions based ONLY on the selected text provided by the user.
    It enforces strict grounding to prevent hallucination.

    Args:
        request: GroundedChatRequest with query and selected_text

    Returns:
        ChatResponse with grounded answer

    Raises:
        HTTPException 500: If LLM service fails
    """
    try:
        logger.info(
            f"Grounded chat request - query: '{request.query[:50]}...', "
            f"selected_text: {len(request.selected_text)} chars"
        )

        # Generate grounded response using LLM service
        result = llm_service.generate_grounded_response(
            query=request.query,
            selected_text=request.selected_text,
            conversation_id=request.conversation_id,
        )

        # Convert to ChatResponse model
        response = ChatResponse(
            answer=result["answer"],
            grounded_in=result["grounded_in"],
            conversation_id=result["conversation_id"],
            grounded=result["grounded"],
            sources=[],  # Grounded mode doesn't use vector search sources
        )

        logger.info(
            f"✅ Grounded response generated - conversation_id: {response.conversation_id}"
        )

        return response

    except Exception as e:
        logger.error(f"❌ Grounded chat failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate response: {str(e)}"
        )
