"""
Contract tests for POST /chat endpoint

Tests request validation, response schema, error codes (400, 500, 503), and latency measurement.
Based on contracts/chat.yaml specification.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch
from backend.app.models import ChatResponse
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_chat_endpoint_success(async_client: AsyncClient):
    """Test the /chat endpoint with a valid request returns 200 and correct schema."""
    with patch("backend.app.rag.chat_with_rag") as mock_chat_with_rag:
        mock_chat_with_rag.return_value = ChatResponse(
            answer="Mocked answer for your question.",
            sources=[
                {
                    "source_document": "doc1.md",
                    "chunk_index": 0,
                    "text": "source text",
                    "token_count": 5,
                    "title": "Doc Title",
                }
            ],
            latency=0.123,
        )
        response = await async_client.post(
            "/chat", json={"question": "What is physical AI?"}
        )
        assert response.status_code == 200

        data = response.json()
        # Verify response schema
        assert "answer" in data
        assert "sources" in data
        assert "latency" in data

        # Verify data types
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["latency"], float)

        mock_chat_with_rag.assert_called_once_with("What is physical AI?")


@pytest.mark.asyncio
async def test_chat_endpoint_empty_question(async_client: AsyncClient):
    """Test POST /chat with empty question returns 422 (validation error)."""
    response = await async_client.post("/chat", json={"question": ""})
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_chat_endpoint_missing_question(async_client: AsyncClient):
    """Test POST /chat with missing question field returns 422."""
    response = await async_client.post("/chat", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint_question_too_long(async_client: AsyncClient):
    """Test POST /chat with question exceeding 500 characters returns 422."""
    long_question = "A" * 501
    response = await async_client.post("/chat", json={"question": long_question})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint_internal_server_error(async_client: AsyncClient):
    """Test the /chat endpoint when an internal server error occurs (500)."""
    with patch(
        "backend.app.rag.chat_with_rag", side_effect=Exception("Something went wrong")
    ):
        response = await async_client.post("/chat", json={"question": "Any question."})
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_endpoint_rag_value_error(async_client: AsyncClient):
    """Test the /chat endpoint when RAG service raises a ValueError (400)."""
    with patch(
        "backend.app.rag.chat_with_rag", side_effect=ValueError("Invalid input to RAG")
    ):
        response = await async_client.post("/chat", json={"question": "Test question."})
        assert response.status_code == 400
        assert "Invalid input to RAG" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_endpoint_service_unavailable(async_client: AsyncClient):
    """Test POST /chat when Qdrant/external service is unavailable returns 503."""
    with patch(
        "backend.app.rag.chat_with_rag",
        side_effect=HTTPException(status_code=503, detail="Service unavailable"),
    ):
        response = await async_client.post("/chat", json={"question": "Test question."})
        assert response.status_code == 503
        assert "Service unavailable" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_latency_measurement(async_client: AsyncClient):
    """Test that latency is measured and included in response."""
    with patch("backend.app.rag.chat_with_rag") as mock_chat_with_rag:
        mock_chat_with_rag.return_value = ChatResponse(
            answer="Test answer", sources=[], latency=1.234
        )
        response = await async_client.post("/chat", json={"question": "Test?"})

        assert response.status_code == 200
        data = response.json()
        assert "latency" in data
        assert data["latency"] > 0


@pytest.mark.asyncio
async def test_chat_no_results_found(async_client: AsyncClient):
    """Test POST /chat when no relevant context is found."""
    with patch("backend.app.rag.chat_with_rag") as mock_chat_with_rag:
        mock_chat_with_rag.return_value = ChatResponse(
            answer="I don't have information about that topic.", sources=[], latency=0.5
        )
        response = await async_client.post(
            "/chat", json={"question": "Unrelated question"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sources"] == []
        assert len(data["answer"]) > 0


@pytest.mark.asyncio
async def test_chat_response_schema_compliance(async_client: AsyncClient):
    """Test that /chat response follows exact schema from contracts/chat.yaml."""
    with patch("backend.app.rag.chat_with_rag") as mock_chat_with_rag:
        mock_chat_with_rag.return_value = ChatResponse(
            answer="Schema compliance test",
            sources=[
                {
                    "source_document": "test.md",
                    "chunk_index": 0,
                    "text": "content",
                    "token_count": 10,
                    "title": "Test",
                }
            ],
            latency=0.8,
        )
        response = await async_client.post("/chat", json={"question": "Schema test?"})

        assert response.status_code == 200
        data = response.json()

        # Verify required fields exist
        required_fields = {"answer", "sources", "latency"}
        assert all(field in data for field in required_fields)

        # Verify sources structure
        if data["sources"]:
            source = data["sources"][0]
            assert "source_document" in source
            assert "chunk_index" in source
