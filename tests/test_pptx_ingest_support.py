from __future__ import annotations

from play_book_studio.app.intake_api import build_customer_pack_support_matrix, customer_pack_request_from_payload


def test_customer_pack_request_accepts_pptx() -> None:
    request = customer_pack_request_from_payload(
        {
            "source_type": "pptx",
            "uri": "C:/tmp/sample.pptx",
            "title": "sample",
        }
    )
    assert request.source_type == "pptx"


def test_support_matrix_prefers_pptx_native_slide_extract() -> None:
    matrix = build_customer_pack_support_matrix()
    entries = {
        str(entry.get("format_id") or ""): entry
        for entry in (matrix.get("entries") or [])
        if isinstance(entry, dict)
    }
    pptx_entry = entries["pptx"]
    assert pptx_entry["source_type"] == "pptx"
    assert pptx_entry["support_status"] == "supported"
    assert pptx_entry["normalization_strategy"] == "pptx_native_slide_extract_v1"
    assert ".pptx" in pptx_entry["accepted_extensions"]


def test_pptx_support_matrix_still_signals_quality_first_review_rule() -> None:
    matrix = build_customer_pack_support_matrix()
    entries = {
        str(entry.get("format_id") or ""): entry
        for entry in (matrix.get("entries") or [])
        if isinstance(entry, dict)
    }
    pptx_entry = entries["pptx"]
    assert "슬라이드 제목" in str(pptx_entry["review_rule"])
    assert "speaker notes" in str(pptx_entry["review_rule"])
