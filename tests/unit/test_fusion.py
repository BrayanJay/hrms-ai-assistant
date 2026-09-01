import pytest
from unittest.mock import MagicMock
from app.services.retrieval.fusion import fuse


def _make_result(chunk_id: str, payload: dict | None = None):
    """Build a minimal Qdrant-style result object."""
    result = MagicMock()
    result.id = chunk_id
    result.payload = payload or {"chunk_id": chunk_id, "content": f"content of {chunk_id}"}
    return result


def test_dense_only_results_sorted_by_rrf_score():
    """Results from dense search only are sorted by descending RRF score."""
    dense = [_make_result("a"), _make_result("b"), _make_result("c")]
    result = fuse(dense_results=dense, sparse_results=[], threshold=0.0)

    # First dense result has highest RRF score (rank 0 → 1/60)
    assert result[0]["chunk_id"] == "a"
    assert result[1]["chunk_id"] == "b"
    assert result[2]["chunk_id"] == "c"


def test_overlapping_results_score_higher():
    """A chunk appearing in both dense and sparse gets a higher combined score."""
    dense = [_make_result("shared"), _make_result("dense-only")]
    sparse = [_make_result("shared"), _make_result("sparse-only")]

    result = fuse(dense_results=dense, sparse_results=sparse, threshold=0.0)

    # "shared" appears in both → score = 1/60 + 1/60; dense-only = 1/(1+60); sparse-only = 1/(1+60)
    assert result[0]["chunk_id"] == "shared"


def test_threshold_filters_low_score_results():
    """Results whose RRF score is below the threshold are excluded."""
    dense = [_make_result("a"), _make_result("b")]
    sparse = []

    # Score for rank 0: 1/60 ≈ 0.01667; rank 1: 1/61 ≈ 0.01639
    # Set threshold above rank 1's score to filter it out
    result = fuse(dense_results=dense, sparse_results=sparse, threshold=0.0166)

    assert len(result) == 1
    assert result[0]["chunk_id"] == "a"


def test_threshold_zero_returns_all():
    """With threshold=0, all results are returned."""
    dense = [_make_result("a"), _make_result("b"), _make_result("c")]
    result = fuse(dense_results=dense, sparse_results=[], threshold=0.0)

    assert len(result) == 3


def test_empty_inputs_return_empty():
    """Both inputs empty returns empty list."""
    result = fuse(dense_results=[], sparse_results=[], threshold=0.0)
    assert result == []


def test_sparse_only_results():
    """Results from sparse search only are included correctly."""
    sparse = [_make_result("x"), _make_result("y")]
    result = fuse(dense_results=[], sparse_results=sparse, threshold=0.0)

    assert result[0]["chunk_id"] == "x"
    assert result[1]["chunk_id"] == "y"


def test_payload_is_returned_not_score():
    """The returned list contains payload dicts, not score wrappers."""
    dense = [_make_result("a", payload={"chunk_id": "a", "content": "hello"})]
    result = fuse(dense_results=dense, sparse_results=[], threshold=0.0)

    assert result[0] == {"chunk_id": "a", "content": "hello"}
    assert "score" not in result[0]
