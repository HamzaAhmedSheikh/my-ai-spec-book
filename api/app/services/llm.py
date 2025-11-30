"""
LLM Service
OpenAI chat completion with grounding enforcement
"""

import logging
import uuid
import os
from typing import Optional, List, Dict

# Import the actual LLM clients
import openai
from anthropic import Anthropic

from app.config import config
from app.models.chat import SourceCitation
from app.utils.grounding import REFUSAL_MESSAGE, build_grounded_prompt

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service for generating grounded and global responses
    """

    def __init__(self):
        """
        Initialize LLMService. Clients are initialized in the `initialize` method.
        """
        self.openai_client: Optional[openai.OpenAI] = None
        self.anthropic_client: Optional[Anthropic] = None
        self.llm_provider: Optional[str] = None
        self.model: Optional[str] = None
        self.temperature: float = 0.0
        self.max_tokens: int = 1024

    def initialize(self):
        """
        Initializes the LLM client based on available API keys.
        Prioritizes OpenAI if both are present.
        """
        openai_api_key = config.OPENAI_API_KEY
        anthropic_api_key = config.ANTHROPIC_API_KEY

        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            self.llm_provider = "openai"
            self.model = "gpt-4o"  # Default OpenAI model, can be configured
            logger.info(f"✅ OpenAI LLM client initialized with model: {self.model}")
elif anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=anthropic_api_key)
            self.llm_provider = "anthropic"
            self.model = "claude-3-sonnet-20240229"  # Default Anthropic model
            logger.info(f"✅ Anthropic LLM client initialized with model: {self.model}")
        else:
            logger.warning("⚠️ No OpenAI or Anthropic API key found. LLM features will be disabled.")
            self.llm_provider = None
            self.model = "no-llm"

        self.temperature = 0.0 # Keeping temperature low for factual RAG
        self.max_tokens = 1024


    def _get_llm_response(self, messages: List[Dict], stream: bool = False) -> str:
        """
        Internal method to get response from the initialized LLM client.
        """
        if not self.llm_provider:
            return REFUSAL_MESSAGE

        try:
            if self.llm_provider == "openai":
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=stream,
                )
                if stream:
                    # Handle streaming response if needed, for now just join
                    return "".join([chunk.choices[0].delta.content or "" for chunk in response])
                return response.choices[0].message.content
            elif self.llm_provider == "anthropic":
                response = self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=messages,
                    stream=stream,
                )
                if stream:
                    # Handle streaming response if needed, for now just join
                    return "".join([chunk.delta.text for chunk in response if chunk.type == "content_block_delta"])
                return response.content[0].text
        except Exception as e:
            logger.error(f"Error getting LLM response from {self.llm_provider}: {e}")
            return "An error occurred while generating a response. Please try again later."


    def generate_grounded_response(
        self,
        query: str,
        selected_text: str,
        conversation_id: Optional[str] = None,
    ) -> dict:
        """
        Generate response grounded in selected text (Magna Carta mode)

        Args:
            query: User's question
            selected_text: Highlighted text from book page
            conversation_id: Optional session ID

        Returns:
            dict with answer, grounded_in, conversation_id, grounded=True
        """
        conv_id = conversation_id or str(uuid.uuid4())
        
        if not selected_text:
            return {
                "answer": REFUSAL_MESSAGE,
                "grounded_in": "",
                "conversation_id": conv_id,
                "grounded": True,
                "sources": [],
                "retrieved_chunks": []
            }

        # Construct prompt for grounded response
        system_prompt = (
            "You are an AI assistant tasked with answering questions strictly based on the provided text. "
            "If the question cannot be answered from the text, state that you cannot answer from the given information. "
            "Do not introduce outside knowledge."
        )
        user_prompt = f"Based on the following text, answer the question:\n\nTEXT:\n{selected_text}\n\nQUESTION: {query}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        answer = self._get_llm_response(messages)

        logger.info(f"Generated grounded response for query: {query[:50]}...")

        return {
            "answer": answer,
            "grounded_in": selected_text[:100] + "..." if len(selected_text) > 100 else selected_text,
            "conversation_id": conv_id,
            "grounded": True,
            "sources": [],
            "retrieved_chunks": [{"text": selected_text, "chapter_id": "selected_text", "chapter_title": "Selected Text", "relevance_score": 1.0}]
        }


    def generate_global_response(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        conversation_id: Optional[str] = None,
    ) -> dict:
        """
        Generate response from vector search results (global mode)

        Args:
            query: User's question
            retrieved_chunks: List of dicts with 'text', 'chapter_id', 'chapter_title', 'relevance_score'
            conversation_id: Optional session ID

        Returns:
            dict with answer, sources, conversation_id, grounded=False
        """
        conv_id = conversation_id or str(uuid.uuid4())
        
        if not retrieved_chunks:
            return {
                "answer": REFUSAL_MESSAGE,
                "sources": [],
                "conversation_id": conv_id,
                "grounded": False,
                "retrieved_chunks": []
            }

        # Prepare context from retrieved chunks
        context_texts = [chunk["text"] for chunk in retrieved_chunks]
        context_str = "\n\n".join(context_texts)

        # Construct prompt for global response
        system_prompt = (
            "You are an AI assistant answering questions about a book. "
            "Use the provided context to answer the question. "
            "If the answer is not in the context, state that you cannot answer from the given information. "
            "Provide citations by referencing the 'chapter_id' and 'chapter_title' of the chunks used. "
            "For example: 'According to [chapter_title (chapter_id)], ...'"
            "Do not introduce outside knowledge."
        )
        user_prompt = f"Based on the following context from the book, answer the question:\n\nCONTEXT:\n{context_str}\n\nQUESTION: {query}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        answer = self._get_llm_response(messages)

        # Extract unique sources for citation
        sources = []
        unique_source_identifiers = set()
        for chunk in retrieved_chunks:
            identifier = (chunk.get("chapter_id"), chunk.get("chapter_title"))
            if identifier not in unique_source_identifiers:
                sources.append(SourceCitation(
                    chapter=chunk.get("chapter_id"),
                    title=chunk.get("chapter_title"),
                    relevance_score=chunk.get("relevance_score", 0.0)
                ))
                unique_source_identifiers.add(identifier)

        logger.info(f"Generated global response for query: {query[:50]}...")

        return {
            "answer": answer,
            "sources": sources,
            "conversation_id": conv_id,
            "grounded": False,
            "retrieved_chunks": retrieved_chunks
        }


# Singleton instance
llm_service = LLMService()