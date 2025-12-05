import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import frontmatter
from qdrant_client import models # Moved from inside full_collection_replacement

from .chunking import count_tokens, semantic_chunking
from .config import settings
from .embeddings import get_embeddings
from .models import ChunkReference, IndexResponse

logger = logging.getLogger(__name__)

# In-memory store for indexing job status (for simplicity)
_indexing_job_status: Dict[str, IndexResponse] = {}

print("Looking for files in:", settings.BOOK_CONTENT_PATH)
print("Directory exists:", os.path.isdir(settings.BOOK_CONTENT_PATH))


def get_job_status(
    job_id: Optional[str] = None,
) -> Union[IndexResponse, Dict[str, IndexResponse]]:
    if job_id:
        return _indexing_job_status.get(job_id)
    return _indexing_job_status


async def run_indexing_job(
    qdrant_client,
    book_content_path: str,
    collection_name: str = settings.QDRANT_COLLECTION_NAME,
    force_reindex: bool = False,
) -> IndexResponse:
    job_id = str(uuid.uuid4())
    start_time = datetime.now()

    _indexing_job_status[job_id] = IndexResponse(
        job_id=job_id,
        status="pending",
        files_processed=0,
        chunks_created=0,
        timestamps={"started_at": start_time.isoformat()},
    )

    try:
        if force_reindex:
            await full_collection_replacement(qdrant_client, collection_name)
        else:
            # Ensure collection exists if not forcing reindex
            try:
                qdrant_client.collection_exists(collection_name=collection_name)
                logger.info(f"Collection '{collection_name}' exists.")
            except Exception:
                logger.info(f"Collection '{collection_name}' does not exist. Creating.")
                qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=1536, distance=models.Distance.COSINE
                    ),
                )

        md_files = find_markdown_files(book_content_path)
        total_files = len(md_files)
        current_files_processed = 0
        current_chunks_created = 0

        _indexing_job_status[job_id].status = "running"

        all_qdrant_points = []
        for file_path in md_files:
            points = process_document(file_path)
            if points:
                all_qdrant_points.extend(points)
            current_files_processed += 1
            _indexing_job_status[job_id].files_processed = current_files_processed
            # Update status more frequently for long jobs (optional, for real-time feedback)
            # await asyncio.sleep(0) # Yield control if running in an event loop

        if all_qdrant_points:
            upsert_chunks_to_qdrant(qdrant_client, all_qdrant_points, collection_name)
            current_chunks_created = len(all_qdrant_points)
            _indexing_job_status[job_id].chunks_created = current_chunks_created

        end_time = datetime.now()
        _indexing_job_status[job_id].status = "completed"
        _indexing_job_status[job_id].timestamps["completed_at"] = end_time.isoformat()
        logger.info(
            f"Indexing job {job_id} completed. Processed {total_files} files, created {current_chunks_created} chunks."
        )

    except Exception as e:
        end_time = datetime.now()
        _indexing_job_status[job_id].status = "failed"
        _indexing_job_status[job_id].error = str(e)
        _indexing_job_status[job_id].timestamps["failed_at"] = end_time.isoformat()
        logger.error(f"Indexing job {job_id} failed: {e}")

    return _indexing_job_status[job_id]


def find_markdown_files(directory: str) -> List[str]:
    """
    Recursively finds all markdown (.md) files within a given directory.
    """
    markdown_files = []
    for root, dirs, files in os.walk(directory):
        # Skip node_modules directories
        if "node_modules" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))
    return markdown_files


def extract_frontmatter(file_path: str) -> Dict[str, Any]:
    """
    Extracts frontmatter from a markdown file.
    Returns a dictionary of frontmatter data.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
    return post.metadata


def process_document(file_path: str) -> List[Dict[str, Any]]:
    """
    Processes a single markdown document: extracts frontmatter, chunks content,
    generates embeddings, and prepares Qdrant points.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        content = post.content

        if not content.strip():
            logger.warning(
                f"File {file_path} is empty or contains only whitespace. Skipping."
            )
            return []

        chunks = semantic_chunking(content)
        chunk_contents = [chunk["content"] for chunk in chunks]

        # Generate embeddings for all chunks in a batch
        chunk_embeddings = get_embeddings(chunk_contents)

        qdrant_points = []
        for i, chunk in enumerate(chunks):
            embedding_vector = chunk_embeddings[i]
            # The payload should be the chunk dictionary itself, which contains all metadata.
            # The ID should be the unique chunk_id.
            qdrant_points.append(
                {
                    "id": str(chunk["chunk_id"]),
                    "vector": embedding_vector,
                    "payload": chunk,
                }
            )
        return qdrant_points
    except Exception as e:
        logger.error(f"Error processing document {file_path}: {e}")
        return []


def upsert_chunks_to_qdrant(
    qdrant_client,
    points: List[Dict[str, Any]],
    collection_name: str = settings.QDRANT_COLLECTION_NAME,
):
    """
    Batch upserts chunks as points to Qdrant.
    """
    try:
        # Convert dictionary points to models.PointStruct
        point_structs = [
            models.PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
            for p in points
        ]

        operation_info = qdrant_client.upsert(
            collection_name=collection_name, wait=True, points=point_structs
        )
        logger.info(f"Qdrant upsert operation info: {operation_info}")
        return operation_info
    except Exception as e:
        logger.error(f"Error upserting points to Qdrant: {e}")
        raise


async def full_collection_replacement(
    qdrant_client,
    collection_name: str = settings.QDRANT_COLLECTION_NAME,
):

    try:
        if qdrant_client.collection_exists(collection_name=collection_name):
            qdrant_client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted.")

        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1536, distance=models.Distance.COSINE
            ),
        )
        logger.info(f"Collection '{collection_name}' recreated with fresh config.")
    except Exception as e:
        logger.error(
            f"Error during full collection replacement for '{collection_name}': {e}"
        )
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Ensure .env is loaded for settings
    from dotenv import load_dotenv

    load_dotenv()

    # T016 Test
    print("--- Testing find_markdown_files ---")
    doc_path = settings.BOOK_CONTENT_PATH

    if not os.path.isdir(doc_path):
        print(f"Directory not found: {doc_path}. Skipping file discovery test.")
    else:
        md_files = find_markdown_files(doc_path)
        print(f"Found {len(md_files)} markdown files:")
        for f in md_files[:5]:  # Print first 5
            print(f)
        if len(md_files) > 5:
            print("...")

    # Test frontmatter extraction and processing (T017, T018, T019, T020)
    print("\n--- Testing document processing and upsert (mocked) ---")
    if md_files:
        sample_file = md_files[0]
        print(f"Processing sample file: {sample_file}")

        # Mock Qdrant client for testing purposes without actual connection
        class MockQdrantClient:
            def upsert(self, collection_name, wait, points):
                print(
                    f"Mock Qdrant: Upserted {len(points)} points to {collection_name}"
                )
                return {"status": "ok", "operation_id": 123}

            def get_collections(self):
                return type("obj", (object,), {"collections": []})()

        try:
            qdrant_mock_client = MockQdrantClient()
            qdrant_points = process_document(sample_file)
            if qdrant_points:
                print(f"Generated {len(qdrant_points)} Qdrant points for {sample_file}")
                # Simulate upsert
                upsert_info = upsert_chunks_to_qdrant(qdrant_mock_client, qdrant_points)
                print(f"Mock Upsert Info: {upsert_info}")
            else:
                print(f"No Qdrant points generated for {sample_file}")
        except Exception as e:
            print(f"Error during document processing test: {e}")
    else:
        print("No markdown files to process for testing.")
