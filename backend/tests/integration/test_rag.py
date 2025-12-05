import pytest
from unittest.mock import AsyncMock, patch
from backend.app.rag import (
    embed_query,
    retrieve_chunks,
    assemble_context,
    generate_answer,
    chat_with_rag,
    grounded_chat,
)
from backend.app.models import ChunkReference, ChatResponse
from backend.app.qdrant_client import QdrantClientSingleton
from qdrant_client import QdrantClient, models
import numpy as np


# Mock embedding function for consistent testing
@pytest.fixture
def mock_get_embeddings():
    with patch("backend.app.rag.get_embeddings") as mock_embed:

        def _mock_embed(texts):
            return [[float(hash(t) % 1000) / 1000.0] * 1536 for t in texts]

        mock_embed.side_effect = _mock_embed
        yield mock_embed


# Mock Qdrant Client for retrieve_chunks and full_collection_replacement
@pytest.fixture
def mock_qdrant_client():
    with patch(
        "backend.app.qdrant_client.QdrantClientSingleton.get_client", autospec=True
    ) as mock_get_client:
        mock_client = AsyncMock(spec=QdrantClient)

        # Mock search method
        mock_client.search.return_value = [
            type(
                "obj",
                (object,),
                {
                    "payload": ChunkReference(
                        source_document="doc1.md",
                        chunk_index=0,
                        text="first relevant chunk",
                        token_count=4,
                        title="Doc One",
                    ).model_dump(),
                    "score": 0.9,
                },
            ),
            type(
                "obj",
                (object,),
                {
                    "payload": ChunkReference(
                        source_document="doc2.md",
                        chunk_index=0,
                        text="second relevant chunk",
                        token_count=4,
                        title="Doc Two",
                    ).model_dump(),
                    "score": 0.85,
                },
            ),
        ]

        # Mock collection_exists and delete_collection for full_collection_replacement
        mock_client.collection_exists.return_value = True
        mock_client.delete_collection.return_value = None
        mock_client.recreate_collection.return_value = None  # Mock recreate

        mock_get_client.return_value = mock_client
        yield mock_client


# Mock OpenAI LLM service
@pytest.fixture
def mock_llm_service():
    with patch("backend.app.rag.llm_service") as mock_llm:
        mock_llm.generate_response.return_value = "Mocked LLM answer based on context."
        yield mock_llm


@pytest.mark.asyncio
async def test_embed_query_integration(mock_get_embeddings):
    query = "test query"
    embedding = embed_query(query)
    assert isinstance(embedding, list)
    assert len(embedding) == 1536
    mock_get_embeddings.assert_called_once_with([query])


@pytest.mark.asyncio
async def test_retrieve_chunks_integration(mock_qdrant_client):
    query_vector = [0.1] * 1536
    chunks = retrieve_chunks(query_vector)
    assert len(chunks) == 2
    assert all(isinstance(c, ChunkReference) for c in chunks)
    mock_qdrant_client.search.assert_called_once()


@pytest.mark.asyncio
async def test_assemble_context_integration():
    chunks = [
        ChunkReference(
            source_document="doc1.md",
            chunk_index=0,
            text="first relevant chunk",
            token_count=4,
            title="Doc One",
        ),
        ChunkReference(
            source_document="doc2.md",
            chunk_index=0,
            text="second relevant chunk",
            token_count=4,
            title="Doc Two",
        ),
    ]
    context = assemble_context(chunks)
    assert "Doc One" in context
    assert "first relevant chunk" in context
    assert "Doc Two" in context
    assert "second relevant chunk" in context
    assert "Source 1" in context
    assert "Source 2" in context


@pytest.mark.asyncio
async def test_generate_answer_integration(mock_llm_service):
    question = "What is the capital?"
    context = "Paris is the capital of France."
    answer = generate_answer(question, context)
    assert answer == "Mocked LLM answer based on context."
    mock_llm_service.generate_response.assert_called_once()
    args, kwargs = mock_llm_service.generate_response.call_args
    messages = args[0]
    assert any(
        "You are a helpful assistant" in msg["content"]
        for msg in messages
        if msg["role"] == "system"
    )
    assert any(
        "Context:\nParis is the capital of France.\n\nQuestion: What is the capital?"
        in msg["content"]
        for msg in messages
        if msg["role"] == "user"
    )


@pytest.mark.asyncio
async def test_chat_with_rag_integration(
    mock_get_embeddings, mock_qdrant_client, mock_llm_service
):
    question = "How does this work?"
    response = await chat_with_rag(question)
    assert isinstance(response, ChatResponse)
    assert response.answer == "Mocked LLM answer based on context."
    assert len(response.sources) == 2
    assert response.latency is not None

    mock_get_embeddings.assert_called_once_with([question])
    mock_qdrant_client.search.assert_called_once()
    mock_llm_service.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_grounded_chat_integration(mock_llm_service):
    question = "Summarize this."
    selected_text = "This is a very important paragraph about a new technology."
    response = await grounded_chat(question, selected_text)
    assert isinstance(response, ChatResponse)
    assert response.answer == "Mocked LLM answer based on context."
    assert len(response.sources) == 0
    assert response.latency is not None

    mock_llm_service.generate_response.assert_called_once()
    args, kwargs = mock_llm_service.generate_response.call_args
    messages = args[0]
    assert any(
        f"Context:\nProvided text:\n{selected_text}\n\nQuestion: {question}"
        in msg["content"]
        for msg in messages
        if msg["role"] == "user"
    )
