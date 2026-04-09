"""Mock RAG engine for Plex-MCP testing.

Provides mock implementations of LanceDB and SentenceTransformers to avoid
heavy dependencies and network calls in CI/CD.
"""

from unittest.mock import patch

import numpy as np


class MockTable:
    """Mock LanceDB table."""

    def __init__(self, name="plex_media"):
        self.name = name
        self.rows = []

    def count_rows(self):
        return len(self.rows)

    def search(self, vector):
        # Return self to allow chaining .limit().to_list()
        return self

    def limit(self, n):
        return self

    def to_list(self):
        # Return a sample result
        return [{"content": "Mock result", "metadata": {"title": "Mock Title"}, "_distance": 0.1}]


class MockLanceDBContent:
    """Mock LanceDB connection object."""

    def __init__(self, uri):
        self.uri = uri
        self.tables = {}

    def connect(self, uri):
        return self

    def open_table(self, name):
        if name not in self.tables:
            raise ValueError(f"Table {name} not found")
        return self.tables[name]

    def create_table(self, name, data=None, mode="overwrite"):
        self.tables[name] = MockTable(name)
        if data:
            self.tables[name].rows.extend(data)
        return self.tables[name]

    def table_names(self):
        return list(self.tables.keys())

    def drop_table(self, name):
        if name in self.tables:
            del self.tables[name]


class MockSentenceTransformer:
    """Mock SentenceTransformer."""

    def __init__(self, model_name="mock"):
        self.model_name = model_name

    def encode(self, sentences, **kwargs):
        # Return deterministic float vectors (dim 384 for MiniLM)
        if isinstance(sentences, str):
            sentences = [sentences]
        return np.random.rand(len(sentences), 384).astype(np.float32)


def patch_rag_engine():
    """Context manager or manual patcher for RAG dependencies."""
    mock_lancedb = MockLanceDBContent("memory://")
    mock_transformer = MockSentenceTransformer()

    patches = [
        patch("lancedb.connect", side_effect=mock_lanced_connect),
        patch("sentence_transformers.SentenceTransformer", return_value=mock_transformer),
    ]
    return patches


def mock_lanced_connect(uri):
    return MockLanceDBContent(uri)
