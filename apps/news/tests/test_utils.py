import pytest  # noqa: F401
from apps.news.views import chunked_queryset


def test_chunked_queryset_divides_correctly():
    sample = list(range(10))  # Sample list of 10 integers

    # Chunk into groups of 3
    chunks = list(chunked_queryset(sample, chunk_size=3))

    assert len(chunks) == 4  # [0–2], [3–5], [6–8], [9]
    assert chunks[0] == [0, 1, 2]
    assert chunks[1] == [3, 4, 5]
    assert chunks[2] == [6, 7, 8]
    assert chunks[3] == [9]


def test_chunked_queryset_handles_empty_input():
    result = list(chunked_queryset([], chunk_size=3))
    assert result == []


def test_chunked_queryset_handles_exact_chunk():
    result = list(chunked_queryset([1, 2, 3, 4], chunk_size=2))
    assert result == [[1, 2], [3, 4]]
