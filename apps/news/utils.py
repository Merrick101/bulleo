"""
Utility functions for the News app.
Located at: apps/news/utils.py
"""

from typing import Generator, List, Any


def chunked_queryset(
        queryset: Any, chunk_size: int = 3) -> Generator[
            List[Any], None, None]:
    """
    Splits a QuerySet or iterable into chunks of the specified size.

    Args:
        queryset (QuerySet | list): The queryset or iterable to chunk.
        chunk_size (int): The number of items per chunk.

    Returns:
        Generator[List[Any]]: Generator yielding chunks of items.
    """
    items = list(queryset)
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]
