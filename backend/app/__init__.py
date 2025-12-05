"""
UV-Based RAG Chatbot Backend for Physical AI Textbook

This package provides a FastAPI-based RAG (Retrieval-Augmented Generation) chatbot
that answers questions about the Physical AI book using vector search and LLM generation.

Main modules:
- config: Environment configuration management
- models: Pydantic data models for API contracts
- routes: FastAPI endpoint handlers
- rag: RAG service (retrieval + generation)
- embeddings: Embedding generation using fastembed
- chunking: Text chunking logic
- indexing: Document indexing pipeline
- llm: OpenAI API wrapper
- qdrant_client: Qdrant vector database client
"""

__version__ = "0.1.0"
