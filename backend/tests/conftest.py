import pytest
from httpx import AsyncClient
from typing import AsyncGenerator, Generator
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Set up environment variables for testing
# This ensures tests use specific settings without interfering with actual .env
os.environ["OPENAI_API_KEY"] = "sk-test-openai-key"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["QDRANT_API_KEY"] = "test-qdrant-key"
os.environ["BOOK_CONTENT_PATH"] = "./my-website/docs/physical-ai"
os.environ["CORS_ALLOWED_ORIGINS"] = "http://localhost:3000,http://localhost:8000"


@pytest.fixture(scope="module")
def test_client() -> Generator:
    """FastAPI TestClient for contract tests"""
    from fastapi.testclient import TestClient
    from backend.app.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for integration tests"""
    from backend.app.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def temp_markdown_files() -> Generator[Path, None, None]:
    """Create temporary markdown files for testing"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Create sample markdown files with frontmatter
    (temp_path / "sample1.md").write_text(
        """---
title: "Introduction to Physical AI"
description: "Overview of Physical AI concepts"
sidebar_position: 1
---

# Introduction to Physical AI

Physical AI combines artificial intelligence with physical systems like robots and autonomous vehicles.
It requires understanding of both software and hardware integration.

## Key Concepts

- Sensor fusion
- Real-time control
- Hardware constraints
"""
    )

    (temp_path / "sample2.md").write_text(
        """---
title: "ROS2 Basics"
description: "Introduction to Robot Operating System 2"
sidebar_position: 2
---

# ROS2 Basics

ROS2 is a middleware framework for building robot applications.
It provides communication protocols, tools, and libraries.
"""
    )

    yield temp_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def mock_qdrant_client():
    """Mock Qdrant client for unit tests"""
    mock = Mock()
    mock.upsert = Mock(return_value=None)
    mock.search = Mock(return_value=[])
    mock.create_collection = Mock(return_value=None)
    mock.delete_collection = Mock(return_value=None)
    mock.collection_exists = Mock(return_value=True)
    return mock


@pytest.fixture(scope="function")
def mock_openai_completion():
    """Mock OpenAI completion for RAG tests"""
    with patch("backend.app.llm.openai.ChatCompletion.create") as mock:
        mock.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="This is a test response from the AI assistant."
                    )
                )
            ]
        )
        yield mock


@pytest.fixture(scope="function")
def sample_chat_request():
    """Sample ChatRequest for testing"""
    return {"question": "What is Physical AI?"}


@pytest.fixture(scope="function")
def sample_grounded_request():
    """Sample GroundedChatRequest for testing"""
    return {
        "question": "What does this mean?",
        "selected_text": "Physical AI combines artificial intelligence with physical systems.",
    }
