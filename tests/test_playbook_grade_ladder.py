from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.intake_api import build_customer_pack_plan
from play_book_studio.intake import classify_customer_pack_playbook_grade


def test_build_customer_pack_plan_exposes_stage_strategy() -> None:
    plan = build_customer_pack_plan(
        {
            "source_type": "pptx",
            "uri": "C:/tmp/sample.pptx",
            "title": "운영 점검 절차",
        }
    )

    stage_strategy = dict(plan.get("stage_strategy") or {})
    assert stage_strategy["source_type"] == "pptx"
    assert stage_strategy["program_target_grade"] == "gold"
    assert stage_strategy["current_lane_target_grade"] == "silver"
    assert stage_strategy["normalize_merge_point"] == "document blocks -> canonical sections"


def test_classify_playbook_grade_returns_bronze_for_minimum_parsed_payload() -> None:
    grade = classify_customer_pack_playbook_grade(
        {
            "sections": [{"heading": "개요", "text": "본문"}],
            "quality_contract": {
                "section_count": 1,
                "document_block_count": 1,
                "sections_with_document_blocks": 1,
            },
            "quality_status": "review",
            "quality_score": 40,
            "quality_flags": ["quality_review_required"],
            "parser_challenger_scorecard": {},
        },
        source_type="hwpx",
    )

    assert grade["grade"] == "bronze"
    assert "quality_review_required" in grade["promotion_blockers"]
    assert grade["current_lane_target_grade"] == "bronze"


def test_classify_playbook_grade_returns_gold_only_for_high_fidelity_payload() -> None:
    grade = classify_customer_pack_playbook_grade(
        {
            "sections": [
                {"heading": "개요", "text": "본문 1"},
                {"heading": "절차", "text": "본문 2"},
            ],
            "quality_contract": {
                "section_count": 2,
                "document_block_count": 7,
                "sections_with_document_blocks": 2,
            },
            "quality_status": "ready",
            "quality_score": 95,
            "quality_flags": [],
            "parser_challenger_scorecard": {
                "evaluated_candidate_count": 1,
                "gold_candidate_count": 1,
                "current_candidate_id": "pptx_native_slide_extract",
                "recommended_candidate_id": "pptx_native_slide_extract",
            },
        },
        source_type="pptx",
    )

    assert grade["grade"] == "gold"
    assert grade["program_target_grade"] == "gold"
    assert grade["promotion_blockers"] == []
