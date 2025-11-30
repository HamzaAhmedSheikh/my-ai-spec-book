"""
Chapter Indexing Script
Recursively finds all markdown files in docs directory, chunks them, 
generates embeddings using FastEmbed, and uploads to Qdrant Cloud

Usage:
    cd api
    python scripts/index_chapters.py [docs_directory]

This script should be run once to populate the vector store with book content
"""

import sys
import os
from pathlib import Path
import logging
from qdrant_client.models import PointStruct
import uuid
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.qdrant_client import qdrant_service
from app.services.embedder import embedder_service
from app.utils.chunking import book_chunker
from app.config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_chapter_file(file_path: Path) -> str:
    """
    Read markdown file content and strip frontmatter
    
    Args:
        file_path: Path to .md file
        
    Returns:
        File content as string (without frontmatter)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove frontmatter if present (--- ... ---)
    frontmatter_pattern = r'^---\s*\n.*?\n---\s*\n'
    content = re.sub(frontmatter_pattern, '', content, flags=re.DOTALL)
    
    return content.strip()


def extract_metadata_from_markdown(content: str, file_path: Path) -> dict:
    """
    Extract metadata from markdown (title, chapter info)
    
    Args:
        content: Markdown content
        file_path: File path for fallback
        
    Returns:
        Dict with title and other metadata
    """
    # Try to extract title from first H1
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem.replace('-', ' ').title()
    
    # Extract chapter number if in filename
    chapter_match = re.search(r'chapter-(\d+)', file_path.stem)
    chapter_num = chapter_match.group(1) if chapter_match else None
    
    return {
        "title": title,
        "chapter_num": chapter_num,
    }


def get_chapter_id_from_path(file_path: Path, docs_root: Path) -> str:
    """
    Generate chapter ID from file path relative to docs root
    
    Args:
        file_path: Full path to markdown file
        docs_root: Root of docs directory
        
    Returns:
        Chapter ID (e.g., "physical-ai/module-1-ros2/chapter-1-introduction")
    """
    # Get relative path from docs root
    rel_path = file_path.relative_to(docs_root)
    
    # Convert to chapter ID (remove .md, use forward slashes)
    chapter_id = str(rel_path).replace('\\', '/').replace('.md', '')
    
    return chapter_id


def get_part_from_path(file_path: Path) -> str:
    """
    Determine part/category from file path
    
    Args:
        file_path: Path to markdown file
        
    Returns:
        Part name (e.g., "Core Technologies", "AI Integration")
    """
    path_str = str(file_path).replace('\\', '/')
    
    # Map module folders to parts
    if 'module-1-ros2' in path_str:
        return "Core Technologies"
    elif 'module-2-gazebo-unity' in path_str:
        return "Core Technologies"
    elif 'module-3-nvidia-isaac' in path_str:
        return "Core Technologies"
    elif 'module-4-vla' in path_str:
        return "AI Integration"
    elif 'introduction' in path_str:
        return "Getting Started"
    else:
        return "Getting Started"


def find_all_markdown_files(docs_dir: Path) -> List[Path]:
    """
    Recursively find all markdown files in docs directory
    
    Args:
        docs_dir: Root directory to search
        
    Returns:
        List of Path objects to markdown files
    """
    md_files = []
    
    # Find all .md files recursively, excluding _category_.json
    for file_path in docs_dir.rglob('*.md'):
        # Skip certain files if needed
        if file_path.name.startswith('_'):
            continue
        md_files.append(file_path)
    
    return sorted(md_files)


def index_chapters(docs_dir: str):
    """
    Main indexing function
    
    Args:
        docs_dir: Path to directory containing chapter markdown files
    """
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        logger.error(f"Directory not found: {docs_dir}")
        return
    
    # Initialize services
    logger.info("Initializing services...")
    try:
        config.validate()
        qdrant_service.connect()
        qdrant_service.create_collection_if_not_exists()
        embedder_service.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        return
    
    # Find all markdown files recursively
    md_files = find_all_markdown_files(docs_path)
    logger.info(f"Found {len(md_files)} markdown files")
    
    if len(md_files) == 0:
        logger.warning(f"No .md files found in {docs_dir}")
        return
    
    all_points = []
    total_chunks = 0
    processed_files = 0
    
    # Process each chapter
    for idx, file_path in enumerate(md_files):
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing ({idx+1}/{len(md_files)}): {file_path.name}")
        logger.info(f"Path: {file_path}")
        
        try:
            # Read file
            content = read_chapter_file(file_path)
            
            if not content or len(content.strip()) < 50:
                logger.warning(f"Skipping {file_path.name} - content too short")
                continue
            
            logger.info(f"Read {len(content)} characters")
            
            # Extract metadata
            chapter_id = get_chapter_id_from_path(file_path, docs_path)
            metadata = extract_metadata_from_markdown(content, file_path)
            chapter_title = metadata["title"]
            part = get_part_from_path(file_path)
            
            logger.info(f"Chapter ID: {chapter_id}")
            logger.info(f"Chapter Title: {chapter_title}")
            logger.info(f"Part: {part}")
            
            # Chunk text
            chunks = book_chunker.chunk_with_metadata(
                text=content,
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                part=part
            )
            logger.info(f"Created {len(chunks)} chunks")
            
            if len(chunks) == 0:
                logger.warning(f"No chunks created for {file_path.name}")
                continue
            
            # Generate embeddings (batch processing for efficiency)
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = embedder_service.embed_batch(chunk_texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Create Qdrant points
            for chunk, embedding in zip(chunks, embeddings):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "chapter_id": chunk["chapter_id"],
                        "chapter_title": chunk["chapter_title"],
                        "part": chunk["part"],
                        "chunk_index": chunk["chunk_index"],
                        "token_count": chunk["token_count"],
                    }
                )
                all_points.append(point)
            
            total_chunks += len(chunks)
            processed_files += 1
            logger.info(f"✅ Processed {file_path.name}: {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {file_path.name}: {str(e)}", exc_info=True)
            continue
    
    # Upload all points to Qdrant
    if all_points:
        logger.info(f"\n{'='*60}")
        logger.info(f"Uploading {len(all_points)} points to Qdrant...")
        try:
            # Upload in batches of 100 to avoid timeout
            batch_size = 100
            for i in range(0, len(all_points), batch_size):
                batch = all_points[i:i+batch_size]
                qdrant_service.upsert_points(batch)
                logger.info(f"Uploaded batch {i//batch_size + 1} ({len(batch)} points)")
            
            logger.info("✅ All points uploaded successfully")
            
            # Get collection info
            info = qdrant_service.get_collection_info()
            logger.info(f"\n{'='*60}")
            logger.info(f"Collection Info:")
            logger.info(f"  Name: {info['name']}")
            logger.info(f"  Vectors: {info['vectors_count']}")
            logger.info(f"  Points: {info['points_count']}")
            logger.info(f"  Status: {info['status']}")
            logger.info(f"\nSummary:")
            logger.info(f"  Files processed: {processed_files}/{len(md_files)}")
            logger.info(f"  Total chunks: {total_chunks}")
            logger.info(f"  Total points: {len(all_points)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to upload points: {str(e)}", exc_info=True)
    else:
        logger.warning("No points to upload")


if __name__ == "__main__":
    # Get docs directory from argument or use default
    if len(sys.argv) > 1:
        docs_directory = sys.argv[1]
    else:
        # Default: my-website/docs/physical-ai/
        project_root = Path(__file__).parent.parent.parent
        docs_directory = str(project_root / "my-website" / "docs" / "physical-ai")
    
    logger.info("="*60)
    logger.info("Chapter Indexing Script")
    logger.info("Using FastEmbed with BAAI/bge-small-en-v1.5")
    logger.info("="*60)
    logger.info(f"Docs directory: {docs_directory}")
    logger.info("")
    
    index_chapters(docs_directory)
    
    logger.info("\n" + "="*60)
    logger.info("Indexing complete!")
    logger.info("="*60)
