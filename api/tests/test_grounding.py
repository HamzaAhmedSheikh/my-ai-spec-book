"""
Grounding Enforcement Test Suite
Tests that chatbot refuses out-of-scope questions

Test Strategy:
- 10 in-selection questions (should answer)
- 10 out-of-selection questions (should refuse)
- Acceptance criteria: <5% hallucination rate (max 1 failure in 20 tests)
"""

import pytest
from app.utils.grounding import (
    build_grounded_prompt,
    build_global_prompt,
    is_refusal_response,
    REFUSAL_MESSAGE,
)


# ============================================================================
# Mock Selected Text (Sample from book)
# ============================================================================

SAMPLE_BOOK_TEXT = """
ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software.
It is a collection of tools, libraries, and conventions that aim to simplify the task
of creating complex and robust robot behavior across a wide variety of robotic platforms.

The core concept in ROS 2 is the computational graph, which consists of nodes that
communicate via topics. A node is a process that performs computation, while a topic
is a named bus over which nodes exchange messages.
"""

# ============================================================================
# Test Cases: In-Selection (Should Answer)
# ============================================================================

IN_SELECTION_QUESTIONS = [
    "What is ROS 2?",
    "How do nodes communicate in ROS 2?",
    "What is a topic in ROS 2?",
    "What is the core concept in ROS 2?",
    "What is a node?",
    "What does ROS 2 stand for?",
    "What is the computational graph?",
    "What does ROS 2 aim to simplify?",
    "What are the main components of ROS 2?",
    "How do nodes exchange messages?",
]

# ============================================================================
# Test Cases: Out-of-Selection (Should Refuse)
# ============================================================================

OUT_OF_SELECTION_QUESTIONS = [
    "What is the weather today?",
    "Who won the 2024 election?",
    "What is quantum computing?",
    "How do I fix a broken iPhone?",
    "What is the capital of France?",
    "Explain machine learning",
    "What is the best programming language?",
    "How does blockchain work?",
    "What is the latest news?",
    "Tell me a joke",
]


# ============================================================================
# Tests: Prompt Building
# ============================================================================


def test_grounded_prompt_format():
    """Test that grounded prompt is correctly formatted"""
    query = "What is ROS 2?"
    prompt = build_grounded_prompt(query, SAMPLE_BOOK_TEXT)

    assert "STRICT RULES" in prompt
    assert "ONLY answer questions using the provided book excerpts" in prompt
    assert SAMPLE_BOOK_TEXT in prompt
    assert query in prompt


def test_global_prompt_format():
    """Test that global prompt is correctly formatted with multiple chunks"""
    query = "Explain ROS 2 architecture"
    chunks = [
        "Chunk 1: ROS 2 is a framework...",
        "Chunk 2: Nodes communicate via topics...",
    ]
    prompt = build_global_prompt(query, chunks)

    assert "STRICT RULES" in prompt
    assert "Excerpt 1" in prompt
    assert "Excerpt 2" in prompt
    assert chunks[0] in prompt
    assert chunks[1] in prompt
    assert query in prompt


# ============================================================================
# Tests: Refusal Detection
# ============================================================================


def test_refusal_message_detection():
    """Test that refusal messages are correctly identified"""
    # Exact match
    assert is_refusal_response(REFUSAL_MESSAGE)

    # Case insensitive
    assert is_refusal_response(REFUSAL_MESSAGE.upper())
    assert is_refusal_response(REFUSAL_MESSAGE.lower())

    # Partial match
    assert is_refusal_response(f"Sorry, but {REFUSAL_MESSAGE}")

    # Non-refusal
    assert not is_refusal_response("According to Chapter 5, ROS 2 is...")
    assert not is_refusal_response("The answer is...")


# ============================================================================
# Tests: Grounding Enforcement (Integration Tests)
# ============================================================================
# NOTE: These tests require LLM API access and are marked as integration tests
# They will be skipped in CI/CD unless an API key is set


@pytest.mark.integration
@pytest.mark.parametrize("question", IN_SELECTION_QUESTIONS)
def test_in_selection_questions_should_answer(question):
    """
    Test that in-selection questions receive answers (not refusals)

    These questions can be answered using the sample book text
    """
    from app.services.llm import llm_service

    # Initialize LLM service (requires OPENAI_API_KEY or ANTHROPIC_API_KEY)
    try:
        llm_service.initialize()
    except Exception:
        pytest.skip("LLM API key not available")

    # Generate response
    result = llm_service.generate_grounded_response(query=question, selected_text=SAMPLE_BOOK_TEXT)

    # Should not be a refusal
    assert not is_refusal_response(result["answer"]), f"Expected answer but got refusal for: {question}"

    # Should contain relevant information
    assert len(result["answer"]) > 20, "Answer is too short"


@pytest.mark.integration
@pytest.mark.parametrize("question", OUT_OF_SELECTION_QUESTIONS)
def test_out_of_selection_questions_should_refuse(question):
    """
    Test that out-of-selection questions are refused

    These questions cannot be answered using the sample book text
    """
    from app.services.llm import llm_service

    # Initialize LLM service (requires OPENAI_API_KEY or ANTHROPIC_API_KEY)
    try:
        llm_service.initialize()
    except Exception:
        pytest.skip("LLM API key not available")

    # Generate response
    result = llm_service.generate_grounded_response(query=question, selected_text=SAMPLE_BOOK_TEXT)

    # Should be a refusal
    assert is_refusal_response(result["answer"]), f"Expected refusal but got answer for: {question}"


# ============================================================================
# Test: Hallucination Rate (Acceptance Criteria)
# ============================================================================


@pytest.mark.integration
def test_hallucination_rate_below_threshold():
    """
    Test that hallucination rate is <5% (max 1 failure in 20 tests)

    This is the acceptance criteria from the spec
    """
    from app.services.llm import llm_service

    # Initialize LLM service
    try:
        llm_service.initialize()
    except Exception:
        pytest.skip("LLM API key not available")

    failures = 0
    total_tests = len(IN_SELECTION_QUESTIONS) + len(OUT_OF_SELECTION_QUESTIONS)

    # Test in-selection questions (should answer)
    for question in IN_SELECTION_QUESTIONS:
        result = llm_service.generate_grounded_response(query=question, selected_text=SAMPLE_BOOK_TEXT)
        if is_refusal_response(result["answer"]):
            failures += 1  # False negative (refused when should answer)

    # Test out-of-selection questions (should refuse)
    for question in OUT_OF_SELECTION_QUESTIONS:
        result = llm_service.generate_grounded_response(query=question, selected_text=SAMPLE_BOOK_TEXT)
        if not is_refusal_response(result["answer"]):
            failures += 1  # Hallucination (answered when should refuse)

    hallucination_rate = failures / total_tests
    assert hallucination_rate < 0.05, f"Hallucination rate {hallucination_rate:.1%} exceeds 5% threshold"


# ============================================================================
# Test: API Endpoint Integration
# ============================================================================


@pytest.mark.integration
def test_grounded_endpoint_integration():
    """
    Test /api/chat endpoint with valid grounded request
    """
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Valid request for grounded mode
    request_data = {
        "query": "What is ROS 2?",
        "selection_context": SAMPLE_BOOK_TEXT,
        "mode": "context",
        "top_k": 5, # Explicitly include top_k even if not used in grounded mode
    }

    response = client.post("/api/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert "sources" in data # Should be empty for grounded mode as per llm_service
    assert data["mode"] == "context"
    assert len(data["answer"]) > 0


def test_grounded_endpoint_validation():
    """
    Test /api/chat endpoint validation for grounded mode

    Should reject:
    - Empty query
    - Selected text too short (<10 chars)
    - Missing selection_context
    """
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Missing selection_context
    response = client.post("/api/chat", json={"query": "What is ROS 2?", "mode": "context"})
    assert response.status_code == 422 # Because selection_context is required for mode "context"

    # Selected text too short
    response = client.post("/api/chat", json={"query": "What is ROS 2?", "selection_context": "ROS", "mode": "context"})
    assert response.status_code == 422


# ============================================================================
# Tests: Global Chat Endpoint (User Story 4)
# ============================================================================

# External knowledge queries that should be refused
EXTERNAL_KNOWLEDGE_QUESTIONS = [
    "What is the weather today?",
    "Who is the current US president?",
    "What is the stock price of Tesla?",
    "How do I cook pasta?",
    "What are the latest COVID-19 statistics?",
]


@pytest.mark.integration
def test_global_chat_endpoint():
    """
    Test /api/chat endpoint with valid global request
    """
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Valid request (assuming vector store is populated)
    request_data = {
        "query": "What is ROS 2?",
        "mode": "global",
        "top_k": 5,
    }

    response = client.post("/api/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert "sources" in data
    assert data["mode"] == "global"
    assert len(data["answer"]) > 0


@pytest.mark.integration
@pytest.mark.parametrize("question", EXTERNAL_KNOWLEDGE_QUESTIONS)
def test_global_endpoint_refuses_external_knowledge(question):
    """
    Test that /api/chat endpoint (global mode) refuses external knowledge questions

    These questions are not covered in the book and should receive refusal responses
    """
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    request_data = {
        "query": question,
        "mode": "global",
        "top_k": 5,
    }

    response = client.post("/api/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Should be a refusal message
    assert is_refusal_response(data["answer"]), f"Expected refusal but got answer for: {question}"


@pytest.mark.integration
def test_global_chat_with_citations():
    """
    Test that global chat includes source citations
    """
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Query about a topic likely to be in the book
    request_data = {
        "query": "Explain ROS 2 architecture",
        "mode": "global",
        "top_k": 5,
    }

    response = client.post("/api/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # If relevant content is found, sources should be included
    if not is_refusal_response(data["answer"]):
        assert len(data["sources"]) > 0, "Expected source citations when answer is provided"

        # Validate source citation format from backend (book, score, chunk_index)
        for source in data["sources"]:
            assert "book" in source
            assert "score" in source
            assert "chunk_index" in source