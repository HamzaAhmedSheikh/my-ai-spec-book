import pytest
from httpx import AsyncClient
from unittest.mock import patch
from qdrant_client.http.exceptions import UnexpectedResponse


@pytest.mark.asyncio
async def test_health_endpoint_healthy(client: AsyncClient):
    """Test the /health endpoint when Qdrant is connected."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "qdrant_connected": True}


@pytest.mark.asyncio
async def test_health_endpoint_qdrant_disconnected(client: AsyncClient):
    """Test the /health endpoint when Qdrant connection fails."""
    with patch(
        "backend.app.qdrant_client.QdrantClient.get_collections",
        side_effect=UnexpectedResponse("Connection failed"),
    ):
        response = await client.get("/health")
        assert response.status_code == 503
        assert response.json() == {
            "detail": {"status": "unhealthy", "qdrant_connected": False}
        }
