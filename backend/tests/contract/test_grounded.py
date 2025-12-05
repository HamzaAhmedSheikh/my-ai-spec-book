"""
Contract tests for POST /chat/grounded endpoint

Tests validation (selected_text required, 1-10,000 chars), context constraint,
empty sources array, and error handling.
Based on contracts/grounded.yaml specification.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch
from backend.app.models import ChatResponse
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_grounded_chat_endpoint_success(async_client: AsyncClient):
    """Test the /chat/grounded endpoint with a valid request returns 200."""
    with patch("backend.app.rag.grounded_chat") as mock_grounded_chat:
        mock_grounded_chat.return_value = ChatResponse(
            answer="Mocked grounded answer based on selected text.",
            sources=[],
            latency=0.05,
        )
        response = await async_client.post(
            "/chat/grounded",
            json={
                "question": "What is this about?",
                "selected_text": "This is a paragraph about the grounded chat feature.",
            },
        )
        assert response.status_code == 200

        data = response.json()
        # Verify response schema
        assert "answer" in data
        assert "sources" in data
        assert "latency" in data

        # Verify grounded mode specific: sources should be empty
        assert data["sources"] == []

        mock_grounded_chat.assert_called_once_with(
            "What is this about?",
            "This is a paragraph about the grounded chat feature.",
        )


@pytest.mark.asyncio
async def test_grounded_chat_endpoint_missing_selected_text(async_client: AsyncClient):
    """Test the /chat/grounded endpoint with missing selected_text returns 422."""
    response = await async_client.post(
        "/chat/grounded", json={"question": "What is this about?"}
    )
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_grounded_chat_endpoint_empty_selected_text(async_client: AsyncClient):
    """Test the /chat/grounded endpoint with empty selected_text returns 422."""
    response = await async_client.post(
        "/chat/grounded", json={"question": "What is this about?", "selected_text": ""}
    )
    assert response.status_code == 422  # Pydantic validation error (min_length=1)


@pytest.mark.asyncio
async def test_grounded_chat_selected_text_too_long(async_client: AsyncClient):
    """Test POST /chat/grounded with selected_text exceeding 10,000 characters returns 422."""
    long_text = "A" * 10001
    response = await async_client.post(
        "/chat/grounded", json={"question": "Test?", "selected_text": long_text}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_grounded_chat_endpoint_internal_server_error(async_client: AsyncClient):
    """Test the /chat/grounded endpoint when an internal server error occurs (500)."""
    with patch(
        "backend.app.rag.grounded_chat", side_effect=Exception("Grounded chat failed")
    ):
        response = await async_client.post(
            "/chat/grounded",
            json={"question": "Any question.", "selected_text": "Some text."},
        )
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_grounded_chat_value_error(async_client: AsyncClient):
    """Test POST /chat/grounded when service raises ValueError returns 400."""
    with patch(
        "backend.app.rag.grounded_chat", side_effect=ValueError("Invalid input")
    ):
        response = await async_client.post(
            "/chat/grounded", json={"question": "Test?", "selected_text": "Some text"}
        )
        assert response.status_code == 400
        assert "Invalid input" in response.json()["detail"]


@pytest.mark.asyncio
async def test_grounded_chat_empty_sources_array(async_client: AsyncClient):
    """Test that grounded mode always returns empty sources array."""
    with patch("backend.app.rag.grounded_chat") as mock_grounded_chat:
        mock_grounded_chat.return_value = ChatResponse(
            answer="Answer based on selection", sources=[], latency=0.08
        )
        response = await async_client.post(
            "/chat/grounded",
            json={
                "question": "Explain this",
                "selected_text": "Physical AI is about robots and AI integration.",
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Grounded mode should NEVER return sources
        assert data["sources"] == []


@pytest.mark.asyncio
async def test_grounded_chat_context_constraint(async_client: AsyncClient):
    """Test that grounded mode uses only selected text as context."""
    with patch("backend.app.rag.grounded_chat") as mock_grounded_chat:
        selected_text = "ROS2 nodes communicate via topics."
        mock_grounded_chat.return_value = ChatResponse(
            answer="Based only on the selected text about ROS2 nodes.",
            sources=[],
            latency=0.06,
        )

        response = await async_client.post(
            "/chat/grounded",
            json={
                "question": "What does this say about communication?",
                "selected_text": selected_text,
            },
        )

        assert response.status_code == 200
        # Verify the service was called with the exact selected text
        mock_grounded_chat.assert_called_once_with(
            "What does this say about communication?", selected_text
        )


@pytest.mark.asyncio
async def test_grounded_chat_response_schema_compliance(async_client: AsyncClient):
    """Test that /chat/grounded response follows exact schema from contracts/grounded.yaml."""
    with patch("backend.app.rag.grounded_chat") as mock_grounded_chat:
        mock_grounded_chat.return_value = ChatResponse(
            answer="Schema test response", sources=[], latency=0.05
        )
        response = await async_client.post(
            "/chat/grounded", json={"question": "Test?", "selected_text": "Test text"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        required_fields = {"answer", "sources", "latency"}
        assert all(field in data for field in required_fields)

        # Verify sources is always empty list
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) == 0
