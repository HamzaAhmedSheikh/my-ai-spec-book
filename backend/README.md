# Backend Service for Physical AI Book RAG Chatbot

This directory contains the FastAPI backend service for the Physical AI book RAG chatbot.

## Setup Instructions

1.  **Environment Variables**: Create a `.env` file in this directory based on `.env.example`.
    *   `OPENAI_API_KEY`: Your OpenAI API key.
    *   `QDRANT_URL`: URL for your Qdrant instance (e.g., `http://localhost:6333`).
    *   `QDRANT_API_KEY`: API key for Qdrant (if authentication is enabled).
    *   `BOOK_CONTENT_PATH`: Path to the book's markdown content (e.g., `./my-website/docs/physical-ai`).
    *   `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS (e.g., `http://localhost:3000,http://localhost:8000`).

2.  **Install Dependencies**:
    ```bash
    uv sync
    ```

3.  **Run the Application**:
    ```bash
    uvicorn app.main:app --reload
    ```

## API Documentation

(To be added in T048)

## Environment Variable Requirements

See `.env.example` for required environment variables.
