
import os
import logging
import uuid
from qdrant_client.models import PointStruct
from app.services.qdrant_client import qdrant_service
from app.services.embedder import embedder_service
from app.config import config
from typing import List
from markdown import Markdown
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Markdown parser to strip HTML/Markdown
md = Markdown(extensions=['fenced_code', 'tables'])

def markdown_to_text(markdown_string):
    """Converts a markdown string to plain text."""
    html = md.convert(markdown_string)
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()
    # Remove multiple newlines and leading/trailing whitespace
    return re.sub(r'\n\s*\n', '\n\n', text).strip()

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Simple chunking strategy by splitting text into sentences or paragraphs.
    Then combines them to fit chunk_size with overlap.
    """
    # Split by double newline first for paragraphs, then by single newline for sentences
    raw_chunks = re.split(r'(?<=[.!?])\s+|\n{2,}', text)
    raw_chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]

    chunks = []
    current_chunk = []
    current_length = 0

    for i, part in enumerate(raw_chunks):
        part_length = len(part.split())

        if current_length + part_length <= chunk_size:
            current_chunk.append(part)
            current_length += part_length
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            # Start new chunk with overlap
            overlap_parts = raw_chunks[max(0, i - chunk_overlap) : i]
            current_chunk = overlap_parts + [part]
            current_length = sum(len(p.split()) for p in current_chunk)
            if current_length > chunk_size and current_chunk: # If single part is too large
                chunks.append(" ".join(current_chunk[:-1]))
                current_chunk = [current_chunk[-1]]
                current_length = len(current_chunk[0].split())

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Fallback for very long single sentences/paragraphs
    final_chunks = []
    for chunk in chunks:
        if len(chunk.split()) > chunk_size:
            # If a chunk is still too large, split it simply by word count
            words = chunk.split()
            for j in range(0, len(words), chunk_size - chunk_overlap):
                sub_chunk = " ".join(words[j:j + chunk_size])
                if sub_chunk:
                    final_chunks.append(sub_chunk)
        else:
            final_chunks.append(chunk)

    return [c for c in final_chunks if c]

def index_book_content(docs_path: str = "my-website/docs") -> None:
    """
    Reads markdown files, chunks content, generates embeddings, and upserts to Qdrant.
    """
    if not embedder_service.model:
        embedder_service.initialize()
    if not qdrant_service.client:
        qdrant_service.connect()
        qdrant_service.create_collection_if_not_exists()

    points_to_upsert: List[PointStruct] = []
    processed_files_count = 0
    processed_chunks_count = 0

    for root, _, files in os.walk(docs_path):
        for file in files:
            if file.endswith(".md") or file.endswith(".mdx"):
                filepath = os.path.join(root, file)
                logger.info(f"Processing file: {filepath}")
                processed_files_count += 1
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Convert markdown to plain text for chunking and embedding
                    plain_text = markdown_to_text(content)

                    # Chunk the content
                    chunks = chunk_text(
                        plain_text, config.CHUNK_SIZE, config.CHUNK_OVERLAP
                    )
                    logger.info(f"Split {filepath} into {len(chunks)} chunks")

                    # Generate embeddings for each chunk and create PointStructs
                    for i, chunk in enumerate(chunks):
                        if not chunk.strip(): # Skip empty chunks
                            continue
                        embedding = embedder_service.embed_text(chunk)
                        point_id = str(uuid.uuid4())
                        points_to_upsert.append(
                            PointStruct(
                                id=point_id,
                                vector=embedding,
                                payload={
                                    "text": chunk,
                                    "source": filepath,
                                    "chunk_id": i,
                                },
                            )
                        )
                        processed_chunks_count += 1

                except Exception as e:
                    logger.error(f"❌ Error processing {filepath}: {e}")

    if points_to_upsert:
        logger.info(f"Upserting {len(points_to_upsert)} points to Qdrant...")
        qdrant_service.upsert_points(points_to_upsert)
        logger.info("✅ Content indexing complete.")
    else:
        logger.warning("No content found to index.")

    logger.info(f"Summary: Processed {processed_files_count} files and {processed_chunks_count} chunks.")


if __name__ == "__main__":
    # Ensure environment variables are loaded if running directly
    from dotenv import load_dotenv
    load_dotenv()

    # Validate config before starting
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)

    try:
        index_book_content(docs_path="my-website/docs")
    except Exception as e:
        logger.error(f"An error occurred during indexing: {e}")
        exit(1)
