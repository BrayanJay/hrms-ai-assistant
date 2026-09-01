import pytest
from app.services.generation.citation_builder import build_citations


def _make_text_chunk(citation: int, content: str = "some policy text", doc_id: str = "doc-1") -> dict:
    return {
        "citation": citation,
        "type": "text",
        "content": content,
        "doc_id": doc_id,
        "doc_name": "HR Policy.pdf",
        "page": 1,
    }


def _make_image_chunk(citation: int, doc_id: str = "doc-1") -> dict:
    return {
        "citation": citation,
        "type": "image",
        "image_bytes": b"fake-image-bytes",
        "doc_id": doc_id,
        "doc_name": "HR Policy.pdf",
        "page": 2,
    }


def test_citations_extracted_in_answer_order():
    """Citations appear in the order they are referenced in the answer."""
    answer = "First point [2]. Second point [1]."
    context = [_make_text_chunk(1), _make_text_chunk(2)]

    result = build_citations(answer, context)

    assert len(result) == 2
    assert result[0]["citation"] == 2
    assert result[1]["citation"] == 1


def test_duplicate_citations_deduplicated():
    """A citation referenced multiple times appears only once in output."""
    answer = "See [1] for details. Also [1] confirms this."
    context = [_make_text_chunk(1)]

    result = build_citations(answer, context)

    assert len(result) == 1
    assert result[0]["citation"] == 1


def test_citation_not_in_context_is_ignored():
    """A citation number in the answer that has no matching context chunk is skipped."""
    answer = "Refer to [99] for more information."
    context = [_make_text_chunk(1)]

    result = build_citations(answer, context)

    assert result == []


def test_image_chunk_returns_image_bytes_not_content():
    """Image chunks use image_bytes key; text chunks use content key."""
    answer = "See chart [1] and policy [2]."
    context = [_make_image_chunk(1), _make_text_chunk(2)]

    result = build_citations(answer, context)

    assert len(result) == 2
    assert "image_bytes" in result[0]
    assert "content" not in result[0]
    assert "content" in result[1]
    assert "image_bytes" not in result[1]


def test_no_citations_in_answer_returns_empty():
    """Answer with no [N] markers returns an empty citations list."""
    answer = "Here is a general response with no citations."
    context = [_make_text_chunk(1)]

    result = build_citations(answer, context)

    assert result == []


def test_empty_context_returns_empty():
    """No context means no citations can be built, regardless of answer."""
    answer = "See [1] and [2]."
    result = build_citations(answer, context=[])

    assert result == []


def test_only_referenced_chunks_are_returned():
    """Context chunks not referenced in the answer are excluded from output."""
    answer = "Only [1] is referenced."
    context = [_make_text_chunk(1), _make_text_chunk(2), _make_text_chunk(3)]

    result = build_citations(answer, context)

    assert len(result) == 1
    assert result[0]["citation"] == 1


def test_doc_metadata_preserved():
    """doc_id, doc_name, and page are included in citation output."""
    answer = "See [1]."
    chunk = _make_text_chunk(1, doc_id="doc-42")
    chunk["doc_name"] = "Leave Policy 2026.pdf"
    chunk["page"] = 5

    result = build_citations(answer, [chunk])

    assert result[0]["doc_id"] == "doc-42"
    assert result[0]["doc_name"] == "Leave Policy 2026.pdf"
    assert result[0]["page"] == 5
