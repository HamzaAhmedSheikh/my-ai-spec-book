"""RAG (Retrieval-Augmented Generation) implementation for the Physical AI chatbot.

This module handles:
- Query embedding generation using OpenAI text-embedding-3-small
- Vector similarity search in Qdrant
- Context retrieval and formatting
- LLM response generation with retrieved context using OpenAI Agents SDK
"""

import logging
import time
from typing import Any, Dict, List, Optional

from agents import Agent, Runner, function_tool
from openai import OpenAI

from .config import settings
from .models import ChatResponse, Source
from .qdrant_client import qdrant_client_instance

logger = logging.getLogger(__name__)

# Initialize OpenAI client (singleton pattern)
_openai_client = None


def get_openai_client() -> OpenAI:
    """Get or initialize the OpenAI client."""
    global _openai_client
    if _openai_client is None:
        logger.info("Initializing OpenAI client")
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please set it in your .env file or environment variables."
            )
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    return _openai_client


print(settings.OPENAI_API_KEY)


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for input text using OpenAI text-embedding-3-small.

    Args:
        text: Input text to embed

    Returns:
        List of floats representing the embedding vector (1536 dimensions)
    """
    try:
        client = get_openai_client()

        # Create embedding using OpenAI API
        response = client.embeddings.create(model="text-embedding-3-small", input=text)

        embedding = response.data[0].embedding
        logger.debug(f"Generated embedding with {len(embedding)} dimensions")
        return embedding

    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def retrieve_chunks(query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant chunks from Qdrant based on query vector.

    Args:
        query_vector: The embedding vector of the user's query
        top_k: Number of top results to retrieve (default: 5)

    Returns:
        List of dictionaries containing chunk data and metadata
    """
    try:
        collection_name = "ai-spec-book"

        logger.info(
            f"Searching Qdrant collection '{collection_name}' with top_k={top_k}"
        )

        # Updated to use query_points instead of search
        search_result = (
            qdrant_client_instance.get_client()
            .query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=top_k,
            )
            .points
        )

        # Format the results
        chunks = []
        for scored_point in search_result:
            chunk_data = {
                "chapter": scored_point.payload.get("chapter_id", "Unknown"),
                "section": scored_point.payload.get("section_title", "Unknown"),
                "page": scored_point.payload.get("page", "N/A"),
                "relevance_score": round(scored_point.score, 3),
                "text_content": scored_point.payload.get("content", ""),
            }
            chunks.append(chunk_data)

        logger.info(f"Retrieved {len(chunks)} chunks from Qdrant")
        return chunks

    except Exception as e:
        logger.error(f"Error retrieving chunks from Qdrant: {e}")
        raise


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved chunks into a context string for the LLM.

    Args:
        chunks: List of chunk dictionaries with text and metadata

    Returns:
        Formatted context string
    """
    if not chunks:
        return "No relevant context found."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        chapter = chunk.get("chapter", "Unknown")
        section = chunk.get("section", "Unknown")
        text = chunk.get("text_content", "")

        context_parts.append(
            f"[Source {i}] Chapter: {chapter}, Section: {section}\n{text}"
        )

    return "\n\n".join(context_parts)


# Define retrieval tool for the agent
@function_tool
def search_knowledge_base(question: str, top_k: int = 5) -> str:
    """
    Search the physical AI knowledge base for relevant information.

    Args:
        question: The question to search for in the knowledge base
        top_k: Number of top results to retrieve (default: 5)

    Returns:
        Formatted context from the most relevant sources
    """
    try:
        logger.info(
            f"Tool called: search_knowledge_base with question: {question[:50]}..."
        )

        # Generate embedding for the question using OpenAI
        query_vector = generate_embedding(question)

        # Retrieve relevant chunks
        chunks = retrieve_chunks(query_vector, top_k=top_k)

        if not chunks:
            return "No relevant information found in the knowledge base. The question might be outside the scope of the available content."

        # Format and return context
        context = format_context(chunks)
        logger.info(f"Tool returned {len(chunks)} chunks")
        return context

    except Exception as e:
        logger.error(f"Error in search_knowledge_base tool: {e}")
        return f"Error searching knowledge base: {str(e)}"


async def chat_with_rag(question: str, top_k: int = 5) -> ChatResponse:
    """
    Main RAG pipeline: retrieve context and generate answer using Agent with tools.

    Args:
        question: User's question
        top_k: Number of chunks to retrieve

    Returns:
        ChatResponse with answer, sources, and metadata
    """
    start_time = time.time()

    try:
        # Validate input
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        logger.info(f"Processing RAG query: {question[:100]}...")

        # Create agent with retrieval tool
        system_instructions = """You are a helpful AI assistant that answers questions about physical AI and robotics.

Instructions:
- Use the search_knowledge_base tool to find relevant information from the book
- Base your answer ONLY on the information retrieved from the knowledge base
- If the knowledge base doesn't contain enough information, clearly state that
- Be concise but comprehensive
- Cite specific chapters and sections when possible
- If you're uncertain, acknowledge it

Always use the search_knowledge_base tool before answering to ensure you have the most relevant context."""

        # Create agent with the search tool
        agent = Agent(
            name="RAG Assistant",
            instructions=system_instructions,
            # model=settings.OPENAI_MODEL,
            tools=[search_knowledge_base],
        )

        # Run the agent with the user's question
        result = await Runner.run(agent, question)

        answer = result.final_output.strip()

        # Extract sources from the retrieved chunks
        # We need to run the search again to get metadata for sources
        query_vector = generate_embedding(question)
        chunks = retrieve_chunks(query_vector, top_k=top_k)

        # Format sources
        sources = [
            Source(
                chapter=chunk["chapter"],
                section=chunk["section"],
                page=chunk["page"],
                relevance_score=chunk["relevance_score"],
            )
            for chunk in chunks
        ]

        # Get context for response
        context = format_context(chunks) if chunks else ""

        latency = time.time() - start_time
        logger.info(f"RAG pipeline completed in {latency:.2f}s")

        return ChatResponse(
            answer=answer, sources=sources, context=context, latency=latency
        )

    except Exception as e:
        logger.error(f"Error during RAG chat: {e}", exc_info=True)
        raise


async def grounded_chat(question: str, selected_text: str) -> ChatResponse:
    """
    Answer questions based on user-selected text (no retrieval).

    Args:
        question: User's question
        selected_text: Text selected by the user

    Returns:
        ChatResponse with answer based only on selected text
    """
    start_time = time.time()

    try:
        # Validate input
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        if not selected_text or not selected_text.strip():
            raise ValueError("Selected text cannot be empty")

        logger.info(
            f"Processing grounded chat query with {len(selected_text)} chars of text"
        )

        system_instructions = """You are a helpful AI assistant that answers questions based ONLY on the provided text.

Instructions:
- Answer the question using ONLY the information in the selected text
- If the text doesn't contain the answer, clearly state that
- Be precise and concise
- Do not add information from outside the provided text"""

        # Create agent
        agent = Agent(
            name="Grounded Chat Assistant",
            instructions=system_instructions,
            # model=settings.OPENAI_MODEL,
        )

        user_prompt = f"""Selected Text:
{selected_text}

Question: {question}

Answer:"""

        # Run the agent synchronously
        result = await Runner.run(agent, user_prompt)

        answer = result.final_output.strip()
        latency = time.time() - start_time

        logger.info(f"Grounded chat completed in {latency:.2f}s")

        return ChatResponse(
            answer=answer, sources=[], context=selected_text, latency=latency
        )

    except Exception as e:
        logger.error(f"Error during grounded chat: {e}", exc_info=True)
        raise
