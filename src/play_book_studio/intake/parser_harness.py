from __future__ import annotations

# parser challenger candidate와 quality scorecard를 묶는 로컬 하네스.

from typing import Any


PARSER_CHALLENGER_HARNESS_VERSION = "customer_pack_parser_challenger_harness_v1"

_SOURCE_TYPE_TO_FAMILY = {
    "pptx": "pptx",
    "docx": "docx",
    "xlsx": "xlsx",
    "pdf": "pdf",
    "hwp": "hwp_family",
    "hwpx": "hwp_family",
    "image": "image",
    "md": "text",
    "asciidoc": "text",
    "txt": "text",
    "web": "web",
}

_FAMILY_CANDIDATES: dict[str, tuple[dict[str, object], ...]] = {
    "pptx": (
        {
            "candidate_id": "pptx_native_slide_extract",
            "label": "PPTX Native Slide Extract",
            "role": "primary",
            "parser_backend_ids": ("pptx_native_slide_extract",),
            "parse_strategy": "native_ooxml_first",
            "evidence_expectation": "slide title/body/table/note ordering",
        },
        {
            "candidate_id": "docling_pptx",
            "label": "Docling PPTX Challenger",
            "role": "challenger",
            "parser_backend_ids": ("docling_pptx",),
            "parse_strategy": "structured_layout_challenger",
            "evidence_expectation": "reading order/layout recovery",
        },
        {
            "candidate_id": "markitdown_pptx",
            "label": "MarkItDown PPTX Debug Lane",
            "role": "debug_fallback",
            "parser_backend_ids": ("markitdown_pptx",),
            "parse_strategy": "markdown_debug_only",
            "evidence_expectation": "debug/export only",
        },
    ),
    "docx": (
        {
            "candidate_id": "docx_native_structure",
            "label": "DOCX Native Structure",
            "role": "primary",
            "parser_backend_ids": ("python_docx_native", "docx_native_structure"),
            "parse_strategy": "native_ooxml_first",
            "evidence_expectation": "heading/list/table hierarchy",
        },
        {
            "candidate_id": "docling_docx",
            "label": "Docling DOCX Challenger",
            "role": "challenger",
            "parser_backend_ids": ("docling_docx",),
            "parse_strategy": "structured_layout_challenger",
            "evidence_expectation": "merged layout/table recovery",
        },
        {
            "candidate_id": "markitdown_docx",
            "label": "MarkItDown DOCX Debug Lane",
            "role": "debug_fallback",
            "parser_backend_ids": ("markitdown_docx",),
            "parse_strategy": "markdown_debug_only",
            "evidence_expectation": "debug/export only",
        },
    ),
    "xlsx": (
        {
            "candidate_id": "xlsx_native_sheet_extract",
            "label": "XLSX Native Sheet Extract",
            "role": "primary",
            "parser_backend_ids": ("openpyxl_native", "xlsx_native_sheet_extract"),
            "parse_strategy": "native_ooxml_first",
            "evidence_expectation": "sheet/table semantics",
        },
        {
            "candidate_id": "docling_xlsx",
            "label": "Docling XLSX Challenger",
            "role": "challenger",
            "parser_backend_ids": ("docling_xlsx",),
            "parse_strategy": "structured_layout_challenger",
            "evidence_expectation": "merged-cell recovery",
        },
        {
            "candidate_id": "markitdown_xlsx",
            "label": "MarkItDown XLSX Debug Lane",
            "role": "debug_fallback",
            "parser_backend_ids": ("markitdown_xlsx",),
            "parse_strategy": "markdown_debug_only",
            "evidence_expectation": "debug/export only",
        },
    ),
    "pdf": (
        {
            "candidate_id": "docling_pdf",
            "label": "Docling PDF",
            "role": "primary",
            "parser_backend_ids": ("docling_pdf",),
            "parse_strategy": "structured_pdf_first",
            "evidence_expectation": "layout/reading-order/table recovery",
        },
        {
            "candidate_id": "pypdf_text_fallback",
            "label": "PyPDF Text Fallback",
            "role": "challenger",
            "parser_backend_ids": ("pypdf_text_fallback", "mdls", "string_scan"),
            "parse_strategy": "text_fallback",
            "evidence_expectation": "text-layer salvage",
        },
        {
            "candidate_id": "markitdown_pdf",
            "label": "MarkItDown PDF Debug Lane",
            "role": "debug_fallback",
            "parser_backend_ids": ("markitdown_pdf",),
            "parse_strategy": "markdown_debug_only",
            "evidence_expectation": "debug/export only",
        },
    ),
    "hwp_family": (
        {
            "candidate_id": "unhwp_structured_rows",
            "label": "unhwp Structured Rows",
            "role": "primary",
            "parser_backend_ids": ("unhwp_structured_rows",),
            "parse_strategy": "structured_hwp_first",
            "evidence_expectation": "content.json -> rows",
        },
        {
            "candidate_id": "unhwp_markdown_bridge",
            "label": "unhwp Markdown Bridge",
            "role": "challenger",
            "parser_backend_ids": ("unhwp_markdown_bridge",),
            "parse_strategy": "markdown_bridge_fallback",
            "evidence_expectation": "debug/fallback only",
        },
    ),
    "image": (
        {
            "candidate_id": "docling_image_ocr",
            "label": "Docling Image OCR",
            "role": "primary",
            "parser_backend_ids": ("docling_image_ocr",),
            "parse_strategy": "ocr_image_first",
            "evidence_expectation": "image text/layout recovery",
        },
        {
            "candidate_id": "surya_region_recovery",
            "label": "Surya Region Recovery",
            "role": "challenger",
            "parser_backend_ids": ("surya_region_recovery",),
            "parse_strategy": "selective_region_repair",
            "evidence_expectation": "hard region recovery",
        },
    ),
    "text": (
        {
            "candidate_id": "structured_text_builder",
            "label": "Structured Text Builder",
            "role": "primary",
            "parser_backend_ids": ("structured_text_builder",),
            "parse_strategy": "structured_text_first",
            "evidence_expectation": "explicit heading/code/table retention",
        },
    ),
    "web": (
        {
            "candidate_id": "html_section_extract",
            "label": "HTML Section Extract",
            "role": "primary",
            "parser_backend_ids": ("html_section_extract",),
            "parse_strategy": "html_extract_first",
            "evidence_expectation": "html structure retention",
        },
    ),
    "legacy_office": (
        {
            "candidate_id": "libreoffice_rescue_lane",
            "label": "LibreOffice Rescue Lane",
            "role": "primary",
            "parser_backend_ids": ("libreoffice_rescue_lane",),
            "parse_strategy": "conversion_rescue_lane",
            "evidence_expectation": "convert legacy binary office into OOXML/HTML",
        },
        {
            "candidate_id": "tika_diagnostic",
            "label": "Apache Tika Diagnostic",
            "role": "challenger",
            "parser_backend_ids": ("tika_diagnostic",),
            "parse_strategy": "diagnostic_text_metadata",
            "evidence_expectation": "breadth fallback and diagnostics",
        },
        {
            "candidate_id": "unstructured_legacy_diagnostic",
            "label": "Unstructured Legacy Diagnostic",
            "role": "challenger",
            "parser_backend_ids": ("unstructured_legacy_diagnostic",),
            "parse_strategy": "element_diagnostic",
            "evidence_expectation": "element-level diagnostic extraction",
        },
    ),
}


def parser_family_for_source_type(source_type: str) -> str:
    normalized = str(source_type or "").strip().lower()
    return _SOURCE_TYPE_TO_FAMILY.get(normalized, normalized or "unknown")


def parser_candidates_for_source_type(source_type: str) -> list[dict[str, object]]:
    family = parser_family_for_source_type(source_type)
    return [dict(item) for item in _FAMILY_CANDIDATES.get(family, ())]


def parser_candidates_for_family(format_family: str) -> list[dict[str, object]]:
    family = str(format_family or "").strip().lower()
    return [dict(item) for item in _FAMILY_CANDIDATES.get(family, ())]


def _sections(payload: dict[str, object]) -> list[dict[str, Any]]:
    return [
        dict(section)
        for section in (payload.get("sections") or [])
        if isinstance(section, dict)
    ]


def _block_type_counts(payload: dict[str, object]) -> tuple[dict[str, int], int, int]:
    sections = _sections(payload)
    counts: dict[str, int] = {}
    total = 0
    section_hits = 0
    for section in sections:
        blocks = [
            dict(block)
            for block in (section.get("document_blocks") or [])
            if isinstance(block, dict)
        ]
        if blocks:
            section_hits += 1
        for block in blocks:
            block_type = str(block.get("block_type") or "").strip()
            if not block_type:
                continue
            counts[block_type] = counts.get(block_type, 0) + 1
            total += 1
    return counts, total, section_hits


def _quality_snapshot(payload: dict[str, object]) -> dict[str, object]:
    flags = [str(item).strip() for item in (payload.get("quality_flags") or []) if str(item).strip()]
    sections = _sections(payload)
    score = int(payload.get("quality_score") or 0)
    status = str(payload.get("quality_status") or "").strip()
    summary = str(payload.get("quality_summary") or "").strip()
    if not status:
        if not sections:
            return {
                "quality_status": "review",
                "quality_score": 0,
                "quality_flags": ["no_sections"],
                "quality_summary": "섹션이 없어 challenger candidate를 비교할 수 없습니다.",
            }
        score = 70
        if len(sections) <= 1:
            score -= 10
        if any("[TABLE" in str(section.get("text") or "") for section in sections):
            score += 5
        if any("[CODE" in str(section.get("text") or "") for section in sections):
            score += 5
        status = "ready" if score >= 70 else "review"
        summary = (
            "기본 challenger comparison 점수입니다."
            if status == "ready"
            else "기본 challenger comparison 기준에서는 review가 필요합니다."
        )
    return {
        "quality_status": status or "review",
        "quality_score": max(int(score), 0),
        "quality_flags": flags,
        "quality_summary": summary,
    }


def _candidate_verdict(
    *,
    comparison_status: str,
    quality_status: str,
    quality_score: int,
    quality_flags: list[str],
    section_count: int,
    document_block_count: int,
) -> tuple[str, str]:
    if comparison_status in {"blocked", "unavailable"}:
        return "blocked", "candidate lane is unavailable"
    if comparison_status == "pending":
        return "pending", "candidate lane has not been executed yet"
    if section_count <= 0:
        return "blocked", "candidate produced no sections"
    if "no_sections" in quality_flags:
        return "blocked", "candidate quality gate reported no sections"
    if "structured_blocks_flattened" in quality_flags:
        return "degraded", "candidate flattened structured blocks"
    if quality_status == "ready" and quality_score >= 85 and document_block_count >= section_count * 2:
        return "gold_candidate", "candidate preserved enough structure for gold promotion review"
    if quality_score >= 55:
        return "degraded", "candidate is usable but still below gold-grade threshold"
    return "blocked", "candidate quality score is too low"


def _backend_matches(candidate: dict[str, object], parser_backend: str) -> bool:
    normalized = str(parser_backend or "").strip()
    if not normalized:
        return False
    if normalized == str(candidate.get("candidate_id") or "").strip():
        return True
    backend_ids = tuple(str(item).strip() for item in (candidate.get("parser_backend_ids") or ()) if str(item).strip())
    return normalized in backend_ids


def _candidate_entry(
    candidate: dict[str, object],
    *,
    payload: dict[str, object] | None,
    comparison_status: str,
    comparison_detail: str = "",
) -> dict[str, object]:
    section_count = 0
    block_type_counts: dict[str, int] = {}
    document_block_count = 0
    sections_with_document_blocks = 0
    quality_snapshot = {
        "quality_status": "",
        "quality_score": 0,
        "quality_flags": [],
        "quality_summary": "",
    }
    parser_evidence = {}
    if payload:
        section_count = len(_sections(payload))
        block_type_counts, document_block_count, sections_with_document_blocks = _block_type_counts(payload)
        quality_snapshot = _quality_snapshot(payload)
        parser_evidence = dict(payload.get("parser_evidence") or {})

    quality_flags = [str(item).strip() for item in (quality_snapshot.get("quality_flags") or []) if str(item).strip()]
    verdict, verdict_reason = _candidate_verdict(
        comparison_status=comparison_status,
        quality_status=str(quality_snapshot.get("quality_status") or ""),
        quality_score=int(quality_snapshot.get("quality_score") or 0),
        quality_flags=quality_flags,
        section_count=section_count,
        document_block_count=document_block_count,
    )
    composite_score = int(quality_snapshot.get("quality_score") or 0)
    if section_count:
        composite_score += min(section_count, 12)
    if document_block_count:
        composite_score += min(document_block_count, 20)
    if quality_flags:
        composite_score -= min(len(quality_flags) * 4, 20)

    return {
        "candidate_id": str(candidate.get("candidate_id") or "").strip(),
        "label": str(candidate.get("label") or "").strip(),
        "role": str(candidate.get("role") or "").strip(),
        "comparison_status": comparison_status,
        "comparison_detail": comparison_detail,
        "quality_verdict": verdict,
        "verdict_reason": verdict_reason,
        "parse_strategy": str(candidate.get("parse_strategy") or "").strip(),
        "evidence_expectation": str(candidate.get("evidence_expectation") or "").strip(),
        "quality_status": str(quality_snapshot.get("quality_status") or ""),
        "quality_score": int(quality_snapshot.get("quality_score") or 0),
        "quality_flags": quality_flags,
        "quality_summary": str(quality_snapshot.get("quality_summary") or ""),
        "section_count": section_count,
        "document_block_count": document_block_count,
        "sections_with_document_blocks": sections_with_document_blocks,
        "block_type_counts": block_type_counts,
        "composite_score": max(composite_score, 0),
        "parser_backend": str(parser_evidence.get("parser_backend") or ""),
        "primary_parse_strategy": str(parser_evidence.get("primary_parse_strategy") or ""),
    }


def build_parser_challenger_scorecard(
    *,
    source_type: str,
    primary_payload: dict[str, object] | None = None,
    challenger_payloads: dict[str, dict[str, object]] | None = None,
    challenger_statuses: dict[str, str] | None = None,
    challenger_details: dict[str, str] | None = None,
    format_family: str = "",
) -> dict[str, object]:
    family = str(format_family or parser_family_for_source_type(source_type)).strip().lower()
    candidates = parser_candidates_for_family(family)
    challenger_payloads = {
        str(key).strip(): dict(value)
        for key, value in (challenger_payloads or {}).items()
        if str(key).strip() and isinstance(value, dict)
    }
    challenger_statuses = {
        str(key).strip(): str(value).strip()
        for key, value in (challenger_statuses or {}).items()
        if str(key).strip() and str(value).strip()
    }
    challenger_details = {
        str(key).strip(): str(value).strip()
        for key, value in (challenger_details or {}).items()
        if str(key).strip() and str(value).strip()
    }
    parser_backend = ""
    if primary_payload:
        parser_backend = str((primary_payload.get("parser_evidence") or {}).get("parser_backend") or "").strip()

    current_candidate_id = ""
    entries: list[dict[str, object]] = []
    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id") or "").strip()
        candidate_payload = challenger_payloads.get(candidate_id)
        comparison_status = "pending"
        comparison_detail = challenger_details.get(candidate_id, "")
        if candidate_payload is not None:
            comparison_status = "evaluated"
        elif primary_payload and _backend_matches(candidate, parser_backend):
            current_candidate_id = candidate_id
            candidate_payload = dict(primary_payload)
            comparison_status = "evaluated"
        elif candidate_id in challenger_statuses:
            comparison_status = challenger_statuses[candidate_id]
        elif family == "legacy_office" and str(candidate.get("role") or "") == "primary":
            comparison_status = "blocked"
            if not comparison_detail:
                comparison_detail = "legacy office rescue lane is not implemented yet"
        entries.append(
            _candidate_entry(
                candidate,
                payload=candidate_payload,
                comparison_status=comparison_status,
                comparison_detail=comparison_detail,
            )
        )

    if not current_candidate_id and entries:
        primary_entries = [entry for entry in entries if entry.get("role") == "primary"]
        if primary_entries:
            current_candidate_id = str(primary_entries[0].get("candidate_id") or "")

    recommended_candidate_id = current_candidate_id
    evaluated_entries = [entry for entry in entries if entry.get("comparison_status") == "evaluated"]
    gold_entries = [entry for entry in evaluated_entries if entry.get("quality_verdict") == "gold_candidate"]
    if gold_entries:
        recommended_candidate_id = sorted(
            gold_entries,
            key=lambda item: (int(item.get("composite_score") or 0), int(item.get("quality_score") or 0)),
            reverse=True,
        )[0]["candidate_id"]
    elif evaluated_entries:
        recommended_candidate_id = sorted(
            evaluated_entries,
            key=lambda item: (int(item.get("composite_score") or 0), int(item.get("quality_score") or 0)),
            reverse=True,
        )[0]["candidate_id"]

    return {
        "contract_version": PARSER_CHALLENGER_HARNESS_VERSION,
        "source_type": str(source_type or "").strip().lower(),
        "format_family": family,
        "current_candidate_id": current_candidate_id,
        "recommended_candidate_id": recommended_candidate_id,
        "evaluated_candidate_count": len(evaluated_entries),
        "pending_candidate_count": sum(1 for entry in entries if entry.get("comparison_status") == "pending"),
        "blocked_candidate_count": sum(1 for entry in entries if entry.get("quality_verdict") == "blocked"),
        "gold_candidate_count": sum(1 for entry in entries if entry.get("quality_verdict") == "gold_candidate"),
        "degraded_candidate_count": sum(1 for entry in entries if entry.get("quality_verdict") == "degraded"),
        "candidates": entries,
    }


__all__ = [
    "PARSER_CHALLENGER_HARNESS_VERSION",
    "build_parser_challenger_scorecard",
    "parser_candidates_for_family",
    "parser_candidates_for_source_type",
    "parser_family_for_source_type",
]
