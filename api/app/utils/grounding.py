"""
Grounding Prompt Templates
Multi-layered approach for enforcing book-only responses

Layers:
1. System Prompt: Sets baseline behavior expectations
2. Retrieval Validation: Prevents hallucination when no relevant content found
3. Few-Shot Examples: Improves refusal consistency
"""

# ============================================================================
# Layer 1: System Prompt Template
# ============================================================================

GROUNDED_SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

**STRICT RULES:**
1. ONLY answer questions using the provided book excerpts below.
2. If the excerpts do not contain enough information to answer, respond EXACTLY with:
   "I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters."
3. Always cite the chapter or section where you found the information (e.g., "According to Chapter 5 on ROS 2...").
4. Do NOT use external knowledge, even if you know the answer.
5. Do NOT make assumptions beyond what is explicitly stated in the excerpts.

**Book Excerpts:**
{context}

**Question:** {query}
"""

GLOBAL_SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

**STRICT RULES:**
1. ONLY answer questions using the book content provided below.
2. If the content does not contain enough information to answer, respond EXACTLY with:
   "I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters."
3. Always cite the specific chapters where you found the information.
4. Do NOT use external knowledge, even if you know the answer.
5. If multiple chapters discuss the topic, synthesize the information and cite all relevant sources.

**Relevant Book Content:**
{context}

**Question:** {query}
"""

# ============================================================================
# Layer 3: Few-Shot Refusal Examples
# ============================================================================

FEW_SHOT_REFUSAL_EXAMPLES = [
    {
        "query": "What is the weather in San Francisco today?",
        "answer": "I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters.",
    },
    {
        "query": "Who won the 2024 US presidential election?",
        "answer": "I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters.",
    },
    {
        "query": "What is the best restaurant in New York?",
        "answer": "I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters.",
    },
    {
        "query": "How do I fix a broken iPhone screen?",
        "answer": "I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters.",
    },
    {
        "query": "Explain quantum computing",
        "answer": "I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters.",
    },
]

# ============================================================================
# Refusal Message (Standardized)
# ============================================================================

REFUSAL_MESSAGE = "I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters."


# ============================================================================
# Prompt Builder Functions
# ============================================================================


def build_grounded_prompt(query: str, selected_text: str) -> str:
    """
    Build prompt for grounded mode (selected text)

    Args:
        query: User's question
        selected_text: Highlighted text from book page

    Returns:
        Formatted prompt with grounded system instructions
    """
    return GROUNDED_SYSTEM_PROMPT.format(context=selected_text, query=query)


def build_global_prompt(query: str, retrieved_chunks: list[str]) -> str:
    """
    Build prompt for global mode (vector search)

    Args:
        query: User's question
        retrieved_chunks: Top-k chunks from vector search

    Returns:
        Formatted prompt with global system instructions
    """
    # Concatenate chunks with separators
    context = "\n\n---\n\n".join(
        [f"**Excerpt {i + 1}:**\n{chunk}" for i, chunk in enumerate(retrieved_chunks)]
    )

    return GLOBAL_SYSTEM_PROMPT.format(context=context, query=query)


def is_refusal_response(response: str) -> bool:
    """
    Check if LLM response is a refusal (no relevant content found)

    Args:
        response: LLM-generated answer

    Returns:
        True if response is a refusal, False otherwise
    """
    return REFUSAL_MESSAGE.lower() in response.lower()
