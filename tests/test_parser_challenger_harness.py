from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.intake import build_parser_challenger_scorecard


def _candidate_payload(
    *,
    source_type: str,
    parser_backend: str,
    quality_status: str,
    quality_score: int,
    quality_flags: list[str],
    section_text: str,
    document_blocks: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "source_type": source_type,
        "sections": [
            {
                "heading": "운영 개요",
                "text": section_text,
                "document_blocks": document_blocks,
            }
        ],
        "quality_status": quality_status,
        "quality_score": quality_score,
        "quality_flags": quality_flags,
        "quality_summary": "candidate summary",
        "parser_evidence": {
            "parser_backend": parser_backend,
            "primary_parse_strategy": "test_strategy",
        },
    }


def test_parser_challenger_scorecard_prefers_better_docling_candidate_when_evaluated() -> None:
    primary = _candidate_payload(
        source_type="pptx",
        parser_backend="pptx_native_slide_extract",
        quality_status="ready",
        quality_score=78,
        quality_flags=["structured_blocks_flattened"],
        section_text="본문만 남았다",
        document_blocks=[
            {"block_type": "heading", "text": "운영 개요"},
            {"block_type": "paragraph", "text": "본문만 남았다"},
        ],
    )
    challenger = _candidate_payload(
        source_type="pptx",
        parser_backend="docling_pptx",
        quality_status="ready",
        quality_score=95,
        quality_flags=[],
        section_text="정상적인 본문\n\n[TABLE]\n항목 | 값\n모드 | active\n[/TABLE]",
        document_blocks=[
            {"block_type": "heading", "text": "운영 개요"},
            {"block_type": "paragraph", "text": "정상적인 본문"},
            {"block_type": "list_item", "text": "- oc get nodes"},
            {"block_type": "table", "text": "항목 | 값\n모드 | active"},
        ],
    )

    scorecard = build_parser_challenger_scorecard(
        source_type="pptx",
        primary_payload=primary,
        challenger_payloads={"docling_pptx": challenger},
    )

    assert scorecard["current_candidate_id"] == "pptx_native_slide_extract"
    assert scorecard["recommended_candidate_id"] == "docling_pptx"
    candidates = {
        str(candidate.get("candidate_id") or ""): candidate
        for candidate in (scorecard.get("candidates") or [])
        if isinstance(candidate, dict)
    }
    assert candidates["pptx_native_slide_extract"]["quality_verdict"] == "degraded"
    assert candidates["docling_pptx"]["quality_verdict"] == "gold_candidate"
    assert candidates["markitdown_pptx"]["comparison_status"] == "pending"


def test_parser_challenger_scorecard_exposes_legacy_office_blocked_primary_lane() -> None:
    scorecard = build_parser_challenger_scorecard(
        source_type="ppt",
        format_family="legacy_office",
    )

    assert scorecard["format_family"] == "legacy_office"
    candidates = [
        candidate
        for candidate in (scorecard.get("candidates") or [])
        if isinstance(candidate, dict)
    ]
    assert candidates
    assert candidates[0]["candidate_id"] == "libreoffice_rescue_lane"
    assert candidates[0]["quality_verdict"] == "blocked"
    assert candidates[0]["comparison_status"] == "blocked"
    assert scorecard["blocked_candidate_count"] >= 1
