import pytest
from backend.app.indexing import extract_frontmatter
import os


# Create a temporary markdown file with frontmatter for testing
@pytest.fixture
def temp_markdown_file_with_frontmatter(tmp_path):
    content = """---
title: Test Document
description: A document for testing frontmatter.
sidebar_position: 1
---
# Test Content
This is the main content of the document.
"""
    file_path = tmp_path / "test_doc_fm.md"
    file_path.write_text(content)
    return file_path


# Create a temporary markdown file without frontmatter for testing
@pytest.fixture
def temp_markdown_file_without_frontmatter(tmp_path):
    content = """# No Frontmatter
This document has no frontmatter.
"""
    file_path = tmp_path / "test_doc_no_fm.md"
    file_path.write_text(content)
    return file_path


# Create an empty markdown file
@pytest.fixture
def temp_empty_markdown_file(tmp_path):
    file_path = tmp_path / "empty_doc.md"
    file_path.write_text("")
    return file_path


def test_extract_frontmatter_with_valid_frontmatter(
    temp_markdown_file_with_frontmatter,
):
    metadata = extract_frontmatter(temp_markdown_file_with_frontmatter)
    assert metadata == {
        "title": "Test Document",
        "description": "A document for testing frontmatter.",
        "sidebar_position": 1,
    }


def test_extract_frontmatter_without_frontmatter(
    temp_markdown_file_without_frontmatter,
):
    metadata = extract_frontmatter(temp_markdown_file_without_frontmatter)
    assert metadata == {}  # Should return an empty dictionary


def test_extract_frontmatter_empty_file(temp_empty_markdown_file):
    metadata = extract_frontmatter(temp_empty_markdown_file)
    assert metadata == {}


def test_extract_frontmatter_missing_title(tmp_path):
    content = """---
description: Missing title.
---
# Content
"""
    file_path = tmp_path / "missing_title.md"
    file_path.write_text(content)
    metadata = extract_frontmatter(file_path)
    assert "title" not in metadata
    assert metadata["description"] == "Missing title."


def test_extract_frontmatter_invalid_yaml(tmp_path):
    content = """---
title: "Invalid YAML: [
---
# Content
"""
    file_path = tmp_path / "invalid_yaml.md"
    file_path.write_text(content)
    # frontmatter library handles invalid YAML gracefully by returning an empty metadata dict
    # or raising an exception depending on the exact malformation.
    # We expect it not to crash but return empty or partial.
    metadata = extract_frontmatter(file_path)
    assert (
        metadata == {} or "title" not in metadata
    )  # Depending on frontmatter's error handling, this might vary
