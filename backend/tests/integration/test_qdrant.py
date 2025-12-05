import pytest
from backend.app.config import settings
from backend.app.qdrant_client import QdrantClientSingleton
from backend.app.embeddings import get_embeddings
from backend.app.indexing import full_collection_replacement
from qdrant_client import models
from qdrant_client.http.exceptions import UnexpectedResponse


@pytest.fixture(scope="module")
async def qdrant_test_client():
    """Provides a Qdrant client instance for testing, ensuring a clean collection."""
    qdrant_instance = QdrantClientSingleton()
    client = qdrant_instance.get_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    # Ensure clean slate before tests
    await full_collection_replacement(client, collection_name)
    yield client
    # Clean up after all tests in this module
    await full_collection_replacement(client, collection_name)


@pytest.mark.asyncio
async def test_collection_creation(qdrant_test_client):
    """Test that the collection is created with the correct configuration."""
    collection_name = settings.QDRANT_COLLECTION_NAME
    collection_info = qdrant_test_client.get_collection(collection_name=collection_name)
    assert collection_info.config.vectors.size == 1536
    assert collection_info.config.vectors.distance == models.Distance.COSINE


@pytest.mark.asyncio
async def test_vector_upsert_and_similarity_search(qdrant_test_client):
    """Test upserting vectors and performing a similarity search."""
    collection_name = settings.QDRANT_COLLECTION_NAME

    # 1. Prepare data
    texts = ["hello world", "goodbye world", "fastapi qdrant"]
    embeddings = get_embeddings(texts)

    points = []
    for i, emb in enumerate(embeddings):
        points.append(
            models.PointStruct(
                id=i,
                vector=emb,
                payload={"text": texts[i], "source_document": f"doc_{i}.md"},
            )
        )

    # 2. Upsert points
    qdrant_test_client.upsert(collection_name=collection_name, wait=True, points=points)

    # Verify points count
    collection_info = qdrant_test_client.get_collection(collection_name=collection_name)
    assert collection_info.points_count == len(texts)

    # 3. Perform similarity search
    query_text = "world"
    query_vector = get_embeddings([query_text])[0]

    search_result = qdrant_test_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=2,
        score_threshold=0.1,
    )

    assert len(search_result) > 0
    # The most relevant should be "hello world" or "goodbye world"
    assert any("world" in hit.payload["text"] for hit in search_result)


@pytest.mark.asyncio
async def test_connection_error_handling(mocker):
    """Test handling of Qdrant connection errors."""
    # Mock QdrantClient to raise an exception on initialization or any operation
    mocker.patch(
        "qdrant_client.QdrantClient.get_collections",
        side_effect=UnexpectedResponse("Connection error"),
    )
    mocker.patch(
        "qdrant_client.QdrantClient.recreate_collection",
        side_effect=UnexpectedResponse("Connection error"),
    )

    qdrant_instance = QdrantClientSingleton()
    client = qdrant_instance.get_client()

    with pytest.raises(
        UnexpectedResponse
    ):  # Expecting it to bubble up from _create_collection_if_not_exists
        client.get_collection(collection_name="non_existent")
