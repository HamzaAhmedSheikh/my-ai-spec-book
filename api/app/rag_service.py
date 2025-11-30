"""
RAG System
Main RAG service that orchestrates embedding, retrieval, and LLM generation
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict

from app.services.embedder import embedder_service
from app.services.qdrant_client import qdrant_service
from app.services.retriever import retriever_service
from app.services.llm import llm_service
from app.utils.chunking import book_chunker
from app.config import config
from qdrant_client.models import PointStruct
import uuid

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Main RAG system that coordinates all components:
    - FastEmbed for embeddings (BAAI/bge-small-en-v1.5)
    - Qdrant Cloud for vector storage
    - LLM for response generation
    """

    def __init__(
        self,
        qdrant_url: str,
        qdrant_api_key: str,
        anthropic_api_key: Optional[str] = None,
        collection_name: str = "book_chapters",
    ):
        """
        Initialize RAG system

        Args:
            qdrant_url: Qdrant Cloud cluster URL
            qdrant_api_key: Qdrant Cloud API key
            anthropic_api_key: Optional Anthropic API key (if using Claude)
            collection_name: Qdrant collection name
        """
        self.collection_name = collection_name
        
        # Update environment variables BEFORE importing/config accesses
        import os
        os.environ["QDRANT_URL"] = qdrant_url
        os.environ["QDRANT_API_KEY"] = qdrant_api_key
        
        # Update config values directly (since config reads from os.getenv)
        # Reload config to pick up new environment variables
        config.QDRANT_URL = qdrant_url
        config.QDRANT_API_KEY = qdrant_api_key
        
        if anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
        
        # Check if OpenAI API key is available (required for LLM)
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key and not anthropic_api_key:
            logger.warning("⚠️ Neither OPENAI_API_KEY nor ANTHROPIC_API_KEY found. LLM may not work.")
        
        # Initialize services
        logger.info("Initializing RAG system components...")
        
        # Initialize embedder
        embedder_service.initialize()
        logger.info("✅ Embedder initialized")
        
        # Connect to Qdrant (will use updated config values)
        qdrant_service.connect()
        qdrant_service.create_collection_if_not_exists()
        logger.info("✅ Qdrant connected")
        
        # Initialize LLM (will use OPENAI_API_KEY from config)
        try:
            llm_service.initialize()
            logger.info("✅ LLM service initialized")
        except Exception as e:
            logger.warning(f"⚠️ LLM initialization failed: {e}. Chat endpoints may not work.")
        
        # Store reference to qdrant_client for health checks
        self.qdrant_client = qdrant_service.client

    def index_documents(self, docs_path: str) -> Dict:
        """
        Index all markdown documents from the specified path

        Args:
            docs_path: Path to directory containing markdown files

        Returns:
            Dict with indexing statistics
        """
        docs_dir = Path(docs_path)
        
        if not docs_dir.exists():
            raise FileNotFoundError(f"Directory not found: {docs_path}")
        
        # Find all markdown files recursively
        md_files = list(docs_dir.rglob("*.md"))
        
        if not md_files:
            raise FileNotFoundError(f"No .md files found in {docs_path}")
        
        logger.info(f"Found {len(md_files)} markdown files")
        
        all_points = []
        total_chunks = 0
        processed_files = 0
        
        # Process each file
        for file_path in md_files:
            try:
                # Skip certain files
                if file_path.name.startswith("_"):
                    continue
                
                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Remove frontmatter
                import re
                frontmatter_pattern = r"^---\s*\n.*?\n---\s*\n"
                content = re.sub(frontmatter_pattern, "", content, flags=re.DOTALL).strip()
                
                if not content or len(content) < 50:
                    continue
                
                # Generate chapter ID from path
                chapter_id = str(file_path.relative_to(docs_dir)).replace("\\", "/").replace(".md", "")
                
                # Extract title
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                chapter_title = title_match.group(1).strip() if title_match else file_path.stem.replace("-", " ").title()
                
                # Determine part
                path_str = str(file_path).replace("\\", "/")
                if "module-1-ros2" in path_str or "module-2-gazebo-unity" in path_str or "module-3-nvidia-isaac" in path_str:
                    part = "Core Technologies"
                elif "module-4-vla" in path_str:
                    part = "AI Integration"
                else:
                    part = "Getting Started"
                
                # Chunk content
                chunks = book_chunker.chunk_with_metadata(
                    text=content,
                    chapter_id=chapter_id,
                    chapter_title=chapter_title,
                    part=part,
                )
                
                if not chunks:
                    continue
                
                # Generate embeddings
                chunk_texts = [chunk["text"] for chunk in chunks]
                embeddings = embedder_service.embed_batch(chunk_texts)
                
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
                        },
                    )
                    all_points.append(point)
                
                total_chunks += len(chunks)
                processed_files += 1
                logger.info(f"✅ Processed {file_path.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"❌ Failed to process {file_path.name}: {str(e)}")
                continue
        
        # Upload to Qdrant in batches
        if all_points:
            batch_size = 100
            for i in range(0, len(all_points), batch_size):
                batch = all_points[i : i + batch_size]
                qdrant_service.upsert_points(batch)
                logger.info(f"Uploaded batch {i//batch_size + 1} ({len(batch)} points)")
        
        return {
            "status": "success",
            "books_indexed": processed_files,
            "total_chunks": total_chunks,
            "message": f"Indexed {processed_files} files with {total_chunks} chunks",
        }

    def query(
        self,
        query: str,
        selection_context: Optional[str] = None,
        mode: str = "global",
        top_k: int = 5,
    ) -> Dict:
        """
        Query the RAG system

        Args:
            query: User's question
            selection_context: Optional selected text for context mode
            mode: "global" or "context"
            top_k: Number of chunks to retrieve

        Returns:
            Dict with answer, sources, and mode
        """
        if mode == "context" and selection_context:
            # Grounded mode: answer based on selected text only
            result = llm_service.generate_grounded_response(
                query=query,
                selected_text=selection_context,
            )
            
            return {
                "answer": result["answer"],
                "sources": [],  # No sources in grounded mode
                "mode": "context",
            }
        else:
            # Global mode: search all documents
            retrieved_chunks = retriever_service.retrieve_top_k_chunks(
                query=query,
                k=top_k,
            )
            
            if not retrieved_chunks:
                return {
                    "answer": "I couldn't find relevant information in the book to answer your question.",
                    "sources": [],
                    "mode": "global",
                }
            
            # Generate response with retrieved context
            result = llm_service.generate_global_response(
                query=query,
                retrieved_chunks=retrieved_chunks,
            )
            
            # Format sources
            sources = []
            for source in result.get("sources", []):
                sources.append({
                    "book": source.chapter if hasattr(source, "chapter") else str(source),
                    "score": source.relevance_score if hasattr(source, "relevance_score") else 0.0,
                    "chunk_index": 0,
                })
            
            return {
                "answer": result["answer"],
                "sources": sources,
                "mode": "global",
            }

