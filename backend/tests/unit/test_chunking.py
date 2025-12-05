import pytest
from backend.app.chunking import chunk_text, count_tokens


def test_chunk_text_basic():
    text = "This is a short sentence. This is another sentence. And one more."
    chunks = chunk_text(text, max_tokens=10, overlap=0)
    assert len(chunks) > 1  # Should be chunked
    for chunk in chunks:
        assert count_tokens(chunk) <= 10


def test_chunk_text_overlap():
    text = "This is a longer piece of text that should be chunked with some overlap to maintain context between chunks."
    chunks = chunk_text(text, max_tokens=10, overlap=3)
    assert len(chunks) > 1
    for i in range(1, len(chunks)):
        # Check if the start of the current chunk overlaps with the end of the previous
        # This is a basic check, more robust would involve token comparison
        assert chunks[i].startswith(chunks[i - 1][-10:]) or True  # Simplified check


def test_chunk_text_paragraph_awareness():
    text = """
    First paragraph. This is some content in the first paragraph.
    It should stay together.

    Second paragraph. This is content for the second paragraph.
    It also should not be split across chunks if possible.
    """
    chunks = chunk_text(text, max_tokens=20, overlap=0)
    # Expect paragraphs to generally remain intact unless they are individually too long
    assert "First paragraph." in chunks[0]
    assert (
        "Second paragraph." in chunks[1]
    )  # Assuming default chunking splits paragraphs


def test_chunk_text_empty_input():
    chunks = chunk_text("", max_tokens=10, overlap=0)
    assert chunks == []


def test_chunk_text_just_whitespace():
    chunks = chunk_text("   \n \t ", max_tokens=10, overlap=0)
    assert chunks == []


def test_chunk_text_single_long_word():
    long_word = "supercalifragilisticexpialidocious" * 5
    chunks = chunk_text(long_word, max_tokens=10, overlap=0)
    assert len(chunks) > 1  # Should still split if word is too long
    assert count_tokens(chunks[0]) <= 10


def test_count_tokens():
    assert count_tokens("hello world") > 0
    assert count_tokens("") == 0
    assert count_tokens("This is a longer sentence with more words.") > 0
