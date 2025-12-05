import pytest
from httpx import AsyncClient
import os
import shutil
from pathlib import Path
from datetime import datetime

from backend.app.config import settings
from backend.app.indexing import (
    find_markdown_files,
    process_document,
    upsert_chunks_to_qdrant,
    full_collection_replacement,
)
from backend.app.qdrant_client import QdrantClientSingleton
from qdrant_client import QdrantClient


# Fixture for a temporary book content path
@pytest.fixture(scope="module")
def temp_book_content_path(tmp_path_factory):
    """
    Creates a temporary directory with sample markdown files for testing.
    """
    path = tmp_path_factory.mktemp("temp_book_content")

    # Create a nested directory structure
    (path / "chapter1").mkdir()
    (path / "chapter2").mkdir()

    # Create sample markdown files
    (path / "chapter1" / "intro.md").write_text(
        """---\ntitle: Chapter 1 Introduction
sidebar_position: 1
---\nThis is the introduction to Chapter 1. It contains some text.
"""
    )
    (path / "chapter1" / "details.md").write_text(
        """---\ntitle: Chapter 1 Details
sidebar_position: 2
---\nMore details for Chapter 1. This content is different.
"""
    )
    (path / "chapter2" / "conclusion.md").write_text(
        """---\ntitle: Chapter 2 Conclusion
sidebar_position: 3
---\nConcluding remarks for Chapter 2. Final thoughts here.
"""
    )
    # File with no frontmatter
    (path / "no_fm.md").write_text("A document without frontmatter.")

    # Empty file
    (path / "empty.md").write_text("")

    yield str(path)
    shutil.rmtree(path)  # Clean up after tests


@pytest.fixture(scope="module")
async def setup_qdrant_for_indexing(temp_book_content_path) -> QdrantClient:
    """
    Ensures Qdrant is clean and returns a client for indexing tests.
    """
    qdrant_instance = QdrantClientSingleton()
    qdrant_client = qdrant_instance.get_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    # Ensure a clean slate before tests run
    await full_collection_replacement(qdrant_client, collection_name)

    yield qdrant_client

    # Clean up after all tests in this module are done
    # await full_collection_replacement(qdrant_client, collection_name)


@pytest.mark.asyncio
async def test_full_indexing_pipeline(
    setup_qdrant_for_indexing, temp_book_content_path
):
    """
    Tests the full indexing pipeline from file discovery to Qdrant storage.
    """
    qdrant_client = setup_qdrant_for_indexing
    collection_name = settings.QDRANT_COLLECTION_NAME

    # Step 1: File discovery (T016)
    md_files = find_markdown_files(temp_book_content_path)
    assert len(md_files) >= 3  # Expect at least the 3 created files with content

    all_qdrant_points = []
    for file_path in md_files:
        if "empty.md" in file_path:
            # Empty files should result in no points
            assert not process_document(file_path)
            continue

        # Step 2: Document processing (T017, T018, T020 - partial error handling)
        points = process_document(file_path)
        assert points  # Should generate some points for non-empty files
        assert all(
            isinstance(p["vector"], list) and len(p["vector"]) == 1536 for p in points
        )
        assert all(
            "source_document" in p["payload"] and "text" in p["payload"] for p in points
        )

        all_qdrant_points.extend(points)

    assert len(all_qdrant_points) > 0

    # Step 3: Upsert to Qdrant (T019)
    await upsert_chunks_to_qdrant(qdrant_client, all_qdrant_points, collection_name)

    # Verify Qdrant storage
    collection_info = qdrant_client.get_collection(collection_name=collection_name)
    assert collection_info.points_count == len(all_qdrant_points)

    # Test retrieval
    sample_query_vector = [0.1] * 1536  # Dummy vector for test
    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=sample_query_vector,
        limit=1,
        score_threshold=0.1,  # Low threshold to get some results
    )
    assert len(search_result) > 0


@pytest.mark.asyncio
async def test_re_indexing_idempotency(
    setup_qdrant_for_indexing, temp_book_content_path
):
    """
    Tests that re-indexing the same content doesn't create duplicate entries
    and updates existing ones.
    """
    qdrant_client = setup_qdrant_for_indexing
    collection_name = settings.QDRANT_COLLECTION_NAME

    # Initial indexing
    md_files = find_markdown_files(temp_book_content_path)
    all_qdrant_points_initial = []
    for file_path in md_files:
        if "empty.md" in file_path:
            continue
        all_qdrant_points_initial.extend(process_document(file_path))

    await upsert_chunks_to_qdrant(
        qdrant_client, all_qdrant_points_initial, collection_name
    )
    initial_points_count = qdrant_client.get_collection(
        collection_name=collection_name
    ).points_count

    # Re-index the same content
    all_qdrant_points_reindex = []
    for file_path in md_files:
        if "empty.md" in file_path:
            continue
        all_qdrant_points_reindex.extend(process_document(file_path))

    await upsert_chunks_to_qdrant(
        qdrant_client, all_qdrant_points_reindex, collection_name
    )

    # Assert that the number of points remains the same (updated, not duplicated)
    final_points_count = qdrant_client.get_collection(
        collection_name=collection_name
    ).points_count
    assert final_points_count == initial_points_count

    # Verify that updating a file changes its content without new points
    # This requires modifying a file and re-indexing, then checking content
    modified_file_path = Path(temp_book_content_path) / "chapter1" / "intro.md"
    original_content = modified_file_path.read_text()
    new_content = original_content + "\n\nThis is new content for re-indexing."
    modified_file_path.write_text(new_content)

    # Re-index only the modified file's content
    modified_points = process_document(str(modified_file_path))
    await upsert_chunks_to_qdrant(qdrant_client, modified_points, collection_name)

    # Points count should still be the same, as upsert updates by ID
    assert (
        qdrant_client.get_collection(collection_name=collection_name).points_count
        == initial_points_count
    )

    # Verify the content has been updated for the relevant chunks (more complex, but possible)
    # For a full test, one would retrieve a chunk and check its text content.
