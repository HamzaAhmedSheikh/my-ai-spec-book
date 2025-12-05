"""
Contract tests for POST /index endpoint

Tests request handling, IndexResponse schema, concurrent indexing prevention (409),
and error handling (500).
Based on contracts/index.yaml specification.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, Mock
from datetime import datetime
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_index_endpoint_success(async_client: AsyncClient):
    """
    Test POST /index endpoint with a successful indexing operation returns 200.
    """
    with patch("backend.app.routes.run_indexing") as mock_indexing:
        mock_indexing.return_value = {
            "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "status": "completed",
            "files_processed": 105,
            "chunks_created": 5234,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "error": None,
        }

        response = await async_client.post("/index", json={"force_reindex": True})

        assert response.status_code == 200
        data = response.json()

        # Verify response schema matches IndexResponse
        assert "job_id" in data
        assert "status" in data
        assert "files_processed" in data
        assert "chunks_created" in data
        assert "started_at" in data

        # Verify data types and values
        assert data["status"] == "completed"
        assert isinstance(data["files_processed"], int)
        assert isinstance(data["chunks_created"], int)
        assert data["files_processed"] > 0
        assert data["chunks_created"] > 0


@pytest.mark.asyncio
async def test_index_endpoint_empty_request(async_client: AsyncClient):
    """
    Test POST /index with empty request body (force_reindex defaults to False).
    """
    with patch("backend.app.routes.run_indexing") as mock_indexing:
        mock_indexing.return_value = {
            "job_id": "test-job-id",
            "status": "completed",
            "files_processed": 10,
            "chunks_created": 50,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "error": None,
        }

        response = await async_client.post("/index", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_index_endpoint_concurrent_indexing_error(async_client: AsyncClient):
    """
    Test POST /index endpoint when indexing is already in progress returns 409 Conflict.
    """
    with patch("backend.app.routes.run_indexing") as mock_indexing:
        mock_indexing.side_effect = HTTPException(
            status_code=409, detail="Indexing already in progress"
        )

        response = await async_client.post("/index", json={})

        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
        assert "already in progress" in data["detail"].lower()


@pytest.mark.asyncio
async def test_index_endpoint_internal_server_error(async_client: AsyncClient):
    """
    Test POST /index endpoint when an unexpected internal server error occurs returns 500.
    """
    with patch("backend.app.routes.run_indexing") as mock_indexing:
        mock_indexing.side_effect = Exception("Unexpected indexing error")

        response = await async_client.post("/index", json={})

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_index_endpoint_partial_failure(async_client: AsyncClient):
    """
    Test POST /index when indexing completes with errors (status=failed).
    """
    with patch("backend.app.routes.run_indexing") as mock_indexing:
        mock_indexing.return_value = {
            "job_id": "failed-job-id",
            "status": "failed",
            "files_processed": 50,
            "chunks_created": 200,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "error": "Failed to process 5 files due to parsing errors",
        }

        response = await async_client.post("/index", json={})

        assert response.status_code == 200  # Request succeeded, but indexing had issues
        data = response.json()
        assert data["status"] == "failed"
        assert "error" in data
        assert data["error"] is not None


@pytest.mark.asyncio
async def test_index_response_schema_compliance(async_client: AsyncClient):
    """
    Test that /index response follows exact schema from contracts/index.yaml.
    """
    with patch("backend.app.routes.run_indexing") as mock_indexing:
        mock_indexing.return_value = {
            "job_id": "schema-test-id",
            "status": "completed",
            "files_processed": 100,
            "chunks_created": 1000,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "error": None,
        }

        response = await async_client.post("/index", json={})

        assert response.status_code == 200
        data = response.json()

        # Verify required fields exist
        required_fields = {
            "job_id",
            "status",
            "files_processed",
            "chunks_created",
            "started_at",
        }
        assert all(field in data for field in required_fields)

        # Verify data types
        assert isinstance(data["job_id"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["files_processed"], int)
        assert isinstance(data["chunks_created"], int)

        # Verify status values
        assert data["status"] in ["pending", "running", "completed", "failed"]


@pytest.mark.asyncio
async def test_index_force_reindex_parameter(async_client: AsyncClient):
    """
    Test that force_reindex parameter is properly handled.
    """
    with patch("backend.app.routes.run_indexing") as mock_indexing:
        mock_indexing.return_value = {
            "job_id": "force-reindex-test",
            "status": "completed",
            "files_processed": 105,
            "chunks_created": 5000,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "error": None,
        }

        # Test with force_reindex=True
        response = await async_client.post("/index", json={"force_reindex": True})
        assert response.status_code == 200

        # Test with force_reindex=False
        response = await async_client.post("/index", json={"force_reindex": False})
        assert response.status_code == 200
