from __future__ import annotations

# customer-pack 공정 단계와 브론즈/실버/골드 승급 체계를 정의한다.

from typing import Any


CUSTOMER_PACK_GRADE_LADDER_VERSION = "customer_pack_grade_ladder_v1"

_SOURCE_STAGE_STRATEGIES: dict[str, dict[str, object]] = {
    "web": {
        "format_family": "web",
        "parse_stage": "html capture and section extraction",
        "preprocess_stage": "html cleanup and section boundary recovery",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "silver",
    },
    "pdf": {
        "format_family": "pdf",
        "parse_stage": "text/native pdf parse with OCR triage",
        "preprocess_stage": "layout cleanup, OCR fallback, table/code preservation",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "silver",
    },
    "md": {
        "format_family": "structured_text",
        "parse_stage": "explicit text parse",
        "preprocess_stage": "heading/code/table cleanup",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "silver",
    },
    "asciidoc": {
        "format_family": "structured_text",
        "parse_stage": "explicit text parse",
        "preprocess_stage": "heading/code/table cleanup",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "silver",
    },
    "txt": {
        "format_family": "plain_text",
        "parse_stage": "plain text parse",
        "preprocess_stage": "heading inference and noise cleanup",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "bronze",
    },
    "docx": {
        "format_family": "ooxml_word",
        "parse_stage": "native word parse plus challenger comparison",
        "preprocess_stage": "style/list/table cleanup",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "silver",
    },
    "pptx": {
        "format_family": "ooxml_slides",
        "parse_stage": "native slide parse plus challenger comparison",
        "preprocess_stage": "title ordering, bullet depth, notes and table recovery",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "silver",
    },
    "xlsx": {
        "format_family": "ooxml_sheet",
        "parse_stage": "native sheet parse plus challenger comparison",
        "preprocess_stage": "sheet/table cleanup and command cell retention",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "silver",
    },
    "hwp": {
        "format_family": "hwp_family",
        "parse_stage": "structured HWP parse",
        "preprocess_stage": "content.json row recovery and bitmap triage",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "bronze",
    },
    "hwpx": {
        "format_family": "hwp_family",
        "parse_stage": "structured HWP parse",
        "preprocess_stage": "content.json row recovery and bitmap triage",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "bronze",
    },
    "image": {
        "format_family": "ocr_image",
        "parse_stage": "ocr image parse",
        "preprocess_stage": "confidence triage and region recovery",
        "normalize_merge_point": "document blocks -> canonical sections",
        "design_goal": "reader-first html study cards",
        "current_lane_target_grade": "bronze",
    },
}


def build_customer_pack_stage_strategy(source_type: str) -> dict[str, object]:
    normalized = str(source_type or "").strip().lower()
    base = dict(
        _SOURCE_STAGE_STRATEGIES.get(
            normalized,
            {
                "format_family": normalized or "unknown",
                "parse_stage": "source parse",
                "preprocess_stage": "minimum cleanup",
                "normalize_merge_point": "document blocks -> canonical sections",
                "design_goal": "reader-first html study cards",
                "current_lane_target_grade": "bronze",
            },
        )
    )
    base.update(
        {
            "contract_version": CUSTOMER_PACK_GRADE_LADDER_VERSION,
            "source_type": normalized,
            "program_target_grade": "gold",
            "bronze_definition": "파싱되고 최소 전처리가 끝나 canonical sections 와 html viewer 까지는 올라온 상태",
            "silver_definition": "이건 책이다 싶은 구조와 읽기 흐름이 살아 있는 상태",
            "gold_definition": "위키백과 단계처럼 구조/디테일/일관성이 높은 상태",
        }
    )
    return base


def classify_customer_pack_playbook_grade(
    payload: dict[str, object],
    *,
    source_type: str,
) -> dict[str, object]:
    strategy = build_customer_pack_stage_strategy(source_type)
    quality_status = str(payload.get("quality_status") or "").strip().lower()
    quality_score = int(payload.get("quality_score") or 0)
    quality_flags = [str(item).strip() for item in (payload.get("quality_flags") or []) if str(item).strip()]
    quality_contract = dict(payload.get("quality_contract") or {})
    scorecard = dict(payload.get("parser_challenger_scorecard") or {})
    section_count = int(quality_contract.get("section_count") or len(payload.get("sections") or []))
    document_block_count = int(quality_contract.get("document_block_count") or 0)
    sections_with_document_blocks = int(quality_contract.get("sections_with_document_blocks") or 0)
    evaluated_candidate_count = int(scorecard.get("evaluated_candidate_count") or 0)
    gold_candidate_count = int(scorecard.get("gold_candidate_count") or 0)
    current_candidate_id = str(scorecard.get("current_candidate_id") or "").strip()
    recommended_candidate_id = str(scorecard.get("recommended_candidate_id") or "").strip()

    blockers: list[str] = []
    if section_count <= 0:
        blockers.append("no_sections")
    if document_block_count < max(section_count, 1):
        blockers.append("document_block_coverage_low")
    if sections_with_document_blocks < section_count:
        blockers.append("document_block_coverage_incomplete")
    if quality_status != "ready":
        blockers.append("quality_review_required")
    if quality_score < 70:
        blockers.append("quality_score_below_silver")
    if quality_flags:
        blockers.append("quality_flags_present")

    grade = "blocked"
    rationale = "아직 canonical book 승급 조건을 만족하지 못했습니다."
    if section_count > 0 and document_block_count >= max(section_count, 1):
        grade = "bronze"
        rationale = "파싱과 최소 전처리가 끝나 canonical book/viewer 까지는 올라온 상태입니다."
    if (
        grade == "bronze"
        and quality_status == "ready"
        and quality_score >= 70
        and sections_with_document_blocks >= section_count
        and document_block_count >= max(section_count * 2, 3)
    ):
        grade = "silver"
        rationale = "reader-grade 구조가 살아 있어 책처럼 읽히는 단계입니다."
    if (
        grade == "silver"
        and quality_score >= 90
        and not quality_flags
        and evaluated_candidate_count >= 1
        and gold_candidate_count >= 1
        and current_candidate_id == recommended_candidate_id
        and document_block_count >= max(section_count * 3, 4)
        and section_count >= 2
    ):
        grade = "gold"
        rationale = "구조, 디테일, 일관성이 높아 gold-grade 승급 후보입니다."

    return {
        "contract_version": CUSTOMER_PACK_GRADE_LADDER_VERSION,
        "source_type": str(source_type or "").strip().lower(),
        "grade": grade,
        "program_target_grade": "gold",
        "current_lane_target_grade": str(strategy.get("current_lane_target_grade") or "bronze"),
        "rationale": rationale,
        "promotion_blockers": blockers,
        "section_count": section_count,
        "document_block_count": document_block_count,
        "sections_with_document_blocks": sections_with_document_blocks,
        "quality_status": quality_status or "review",
        "quality_score": quality_score,
        "quality_flags": quality_flags,
        "evaluated_candidate_count": evaluated_candidate_count,
        "gold_candidate_count": gold_candidate_count,
        "current_candidate_id": current_candidate_id,
        "recommended_candidate_id": recommended_candidate_id,
    }


__all__ = [
    "CUSTOMER_PACK_GRADE_LADDER_VERSION",
    "build_customer_pack_stage_strategy",
    "classify_customer_pack_playbook_grade",
]
