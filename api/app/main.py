# """
# FastAPI Application Entry Point
# Physical AI Book RAG Chatbot Backend
# """

# import logging
# from contextlib import asynccontextmanager

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """
#     Application lifespan events
#     - Startup: Load environment variables, validate connections
#     - Shutdown: Cleanup resources
#     """
#     logger.info("🚀 Starting Physical AI RAG API...")

#     # Validate environment variables
#     from app.config import config

#     try:
#         config.validate()
#     except ValueError as e:
#         logger.error(f"❌ Configuration validation failed: {e}")
#         logger.warning(
#             "⚠️ API will start but some features may not work without proper configuration"
#         )

#     # Initialize services
#     from app.services.embedder import embedder_service
#     from app.services.llm import llm_service
#     from app.services.qdrant_client import qdrant_service

#     try:
#         embedder_service.initialize()
#         llm_service.initialize()
#         # Connect to Qdrant Cloud (required for global search mode)
#         try:
#             qdrant_service.connect()
#             logger.info("✅ Qdrant Cloud connected successfully")
#         except Exception as e:
#             logger.warning(f"⚠️ Qdrant connection failed: {e}")
#             logger.warning(
#                 "⚠️ Global search mode will not work, but grounded mode will still function"
#             )
#         logger.info("✅ Services initialized successfully")
#     except Exception as e:
#         logger.error(f"❌ Service initialization failed: {e}")
#         logger.warning("⚠️ API will start but chatbot features may not work")

#     yield
#     logger.info("👋 Shutting down Physical AI RAG API...")


# # Initialize FastAPI app
# app = FastAPI(
#     title="Physical AI Book RAG API",
#     description="Backend API for context-grounded chatbot with RAG capabilities",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# # CORS Configuration
# # Allow GitHub Pages frontend to call this API
# app.add_middleware(
#     CORSMiddleware,
#     # allow_origins=[
#     #     "https://HamzaAhmedSheikh.github.io",  # Production frontend (GitHub Pages)
#     #     "http://localhost:3000",  # Local Docusaurus dev server
#     #     "http://127.0.0.1:3000",  # Alternative localhost
#     # ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST"],  # Restrict to needed methods only
#     allow_headers=["Content-Type", "Authorization"],
#     max_age=3600,  # Cache preflight responses for 1 hour
# )


# @app.get("/")
# async def root():
#     """Root endpoint - API info"""
#     return {
#         "message": "Physical AI Book RAG API",
#         "version": "1.0.0",
#         "docs": "/docs",
#         "health": "/health",
#     }


# # Import routers
# from app.routers import chat, health

# app.include_router(health.router)
# app.include_router(chat.router)


# # Request Logging Middleware
# import time

# from fastapi import Request


# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     """
#     Log all API requests with timing and error tracking
#     """
#     start_time = time.time()

#     logger.info(f"→ {request.method} {request.url.path}")

#     try:
#         response = await call_next(request)
#         duration = time.time() - start_time

#         logger.info(
#             f"← {request.method} {request.url.path} - "
#             f"Status: {response.status_code} - Duration: {duration:.3f}s"
#         )

#         return response
#     except Exception as e:
#         duration = time.time() - start_time
#         logger.error(
#             f"✗ {request.method} {request.url.path} - "
#             f"Error: {str(e)} - Duration: {duration:.3f}s"
#         )
#         raise


"""
FastAPI Main Application

Endpoints:
- POST /api/chat: Query the chatbot
- POST /api/index: Index documents
- GET /api/health: Health check
"""

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.rag_service import RAGSystem

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Book Chatbot API",
    description="Query books using RAG with Qdrant and Claude",
    version="0.1.0",
)

# CORS middleware - allows frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system (singleton)
rag_system = None


def get_rag_system() -> RAGSystem:
    """Get or create RAG system instance"""
    global rag_system
    if rag_system is None:
        print("\n" + "=" * 60)
        print("🚀 INITIALIZING RAG SYSTEM")
        print("=" * 60)

        # Get configuration from environment
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")  # Optional
        openai_api_key = os.getenv("OPENAI_API_KEY")  # For LLM
        collection_name = os.getenv("COLLECTION_NAME", "book_chapters")

        # Validate required environment variables
        if not qdrant_url:
            raise ValueError("QDRANT_URL not found in environment. Please set it in .env file.")
        if not qdrant_api_key:
            raise ValueError("QDRANT_API_KEY not found in environment. Please set it in .env file.")
        
        # OpenAI or Anthropic key is required for LLM
        if not openai_api_key and not anthropic_api_key:
            raise ValueError(
                "Either OPENAI_API_KEY or ANTHROPIC_API_KEY must be set in environment. "
                "Please set one of them in .env file."
            )

        # Create RAG system
        rag_system = RAGSystem(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            anthropic_api_key=anthropic_api_key,
            collection_name=collection_name,
        )

        print("=" * 60)
        print("✅ RAG SYSTEM READY")
        print("=" * 60 + "\n")

    return rag_system


# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    query: str = Field(..., description="User's question", min_length=1)
    selection_context: Optional[str] = Field(
        None, description="Selected text for context mode"
    )
    mode: str = Field("global", description="Query mode: 'global' or 'context'")
    top_k: int = Field(5, description="Number of chunks to retrieve", ge=1, le=20)


class Source(BaseModel):
    """Source information for citations"""

    book: str
    score: float
    chunk_index: int = 0


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""

    answer: str
    sources: List[Source]
    mode: str


class IndexRequest(BaseModel):
    """Request model for indexing endpoint"""

    docs_path: str = Field("my-website/docs", description="Path to documents folder")


class IndexResponse(BaseModel):
    """Response model for indexing endpoint"""

    status: str
    books_indexed: int
    total_chunks: int
    message: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    print("\n🌟 FastAPI server starting...")
    print(f"📍 API will be available at: http://localhost:8000")
    print(f"📖 API docs at: http://localhost:8000/docs")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Book Chatbot API",
        "version": "0.1.0",
        "endpoints": {
            "chat": "POST /api/chat",
            "index": "POST /api/index",
            "health": "GET /api/health",
            "docs": "GET /docs",
        },
    }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Status of the API and its dependencies
    """
    try:
        system = get_rag_system()

        # Check Qdrant connection
        collections = system.qdrant_client.get_collections()

        return {
            "status": "healthy",
            "qdrant": "connected",
            "collections": len(collections.collections),
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "llm_model": "claude-sonnet-4-20250514",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/api/index", response_model=IndexResponse)
async def index_books(request: IndexRequest = None):
    """
    Index all books from the specified folder

    This endpoint:
    1. Scans for all .md files in docs_path
    2. Splits them into chunks
    3. Generates embeddings using BAAI/bge-small-en-v1.5
    4. Stores in Qdrant Cloud

    Args:
        request: Optional request with custom docs_path

    Returns:
        Indexing statistics

    Example:
        curl -X POST http://localhost:8000/api/index
    """
    try:
        print("\n" + "=" * 60)
        print("📚 INDEXING REQUEST RECEIVED")
        print("=" * 60)

        system = get_rag_system()

        # Use custom path or default
        docs_path = request.docs_path if request else "my-website/docs"

        # Validate path exists
        if not Path(docs_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Documents path '{docs_path}' not found. Please create the folder and add .md files.",
            )

        # Perform indexing
        result = system.index_documents(docs_path=docs_path)

        print("=" * 60)
        print("✅ INDEXING COMPLETED")
        print("=" * 60 + "\n")

        return IndexResponse(**result)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Indexing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Query the RAG chatbot

    Two modes:
    1. Global mode: Search all books for relevant information
    2. Context mode: Answer based on selected text

    Args:
        request: Chat request with query and optional context

    Returns:
        Answer with sources

    Example:
        curl -X POST http://localhost:8000/api/chat \
             -H "Content-Type: application/json" \
             -d '{"query": "What is the main theme?", "mode": "global"}'
    """
    try:
        print("\n" + "=" * 60)
        print("💬 CHAT REQUEST RECEIVED")
        print("=" * 60)

        system = get_rag_system()

        # Process query
        result = system.query(
            query=request.query,
            selection_context=request.selection_context,
            mode=request.mode,
            top_k=request.top_k,
        )

        print("=" * 60)
        print("✅ RESPONSE GENERATED")
        print("=" * 60 + "\n")

        return ChatResponse(**result)

    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("🚀 STARTING SERVER WITH UVICORN")
    print("=" * 60)
    print("📍 Host: 0.0.0.0")
    print("📍 Port: 8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
