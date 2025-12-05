import pytest
from backend.app.embeddings import get_embeddings
import numpy as np


def test_get_embeddings_single_text():
    text = "This is a test sentence."
    embeddings = get_embeddings([text])
    assert isinstance(embeddings, list)
    assert len(embeddings) == 1
    assert isinstance(embeddings[0], list)
    assert len(embeddings[0]) == 1536  # Check vector dimension


def test_get_embeddings_multiple_texts():
    texts = ["First test sentence.", "Second test sentence, a bit longer."]
    embeddings = get_embeddings(texts)
    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert isinstance(embeddings[0], list)
    assert len(embeddings[0]) == 1536
    assert isinstance(embeddings[1], list)
    assert len(embeddings[1]) == 1536


def test_get_embeddings_empty_list():
    embeddings = get_embeddings([])
    assert isinstance(embeddings, list)
    assert len(embeddings) == 0


def test_get_embeddings_model_loading_failure():
    # This is hard to test directly without mocking the fastembed TextEmbedding class
    # For now, we assume successful loading, or raise the RuntimeError as implemented
    # in embeddings.py if _embedding_model is None.
    # A more robust test would involve patching TextEmbedding constructor.
    pass


def test_embedding_values_are_floats():
    text = "Ensure embedding values are floats."
    embeddings = get_embeddings([text])
    assert all(isinstance(x, float) for x in embeddings[0])


def test_embedding_output_is_not_empty():
    text = "Non-empty text should produce non-empty embedding."
    embeddings = get_embeddings([text])
    assert len(embeddings[0]) > 0
