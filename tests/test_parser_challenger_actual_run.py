from __future__ import annotations

import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.intake_api import ingest_customer_pack

from test_customer_pack_read_boundary import _FakeChunkingModel, _FakeEmbeddingModel


def _embedding_patches():
    return (
        patch(
            "play_book_studio.intake.private_corpus.load_sentence_model",
            return_value=_FakeEmbeddingModel(),
        ),
        patch(
            "play_book_studio.ingestion.chunking.load_sentence_model",
            return_value=_FakeChunkingModel(),
        ),
    )


def test_docx_ingest_evaluates_native_challenger_scorecard() -> None:
    docx = pytest.importorskip("docx")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        source = root / "sample.docx"
        document = docx.Document()
        document.add_heading("운영 개요", level=1)
        document.add_paragraph("클러스터 상태를 먼저 확인한다.")
        table = document.add_table(rows=2, cols=2)
        table.cell(0, 0).text = "항목"
        table.cell(0, 1).text = "값"
        table.cell(1, 0).text = "모드"
        table.cell(1, 1).text = "active"
        document.save(source)

        with ExitStack() as stack:
            for manager in _embedding_patches():
                stack.enter_context(manager)
            stack.enter_context(
                patch(
                    "play_book_studio.intake.normalization.builders.convert_with_markitdown",
                    return_value="# 운영 개요\n\n클러스터 상태를 먼저 확인한다.",
                )
            )
            result = ingest_customer_pack(
                root,
                {
                    "source_type": "docx",
                    "uri": str(source),
                    "title": "DOCX 샘플",
                    "approval_state": "approved",
                },
            )

        book = dict(result.get("book") or {})
        scorecard = dict(book.get("parser_challenger_scorecard") or {})
        candidates = {
            str(candidate.get("candidate_id") or ""): candidate
            for candidate in (scorecard.get("candidates") or [])
            if isinstance(candidate, dict)
        }
        assert scorecard["current_candidate_id"] == "markitdown_docx"
        assert candidates["docx_native_structure"]["comparison_status"] == "evaluated"
        assert candidates["docx_native_structure"]["document_block_count"] >= 3
        assert scorecard["recommended_candidate_id"] == "docx_native_structure"


def test_xlsx_ingest_evaluates_native_challenger_scorecard() -> None:
    openpyxl = pytest.importorskip("openpyxl")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        source = root / "sample.xlsx"
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "운영 점검"
        sheet.append(["항목", "값"])
        sheet.append(["모드", "active"])
        workbook.save(source)

        with ExitStack() as stack:
            for manager in _embedding_patches():
                stack.enter_context(manager)
            stack.enter_context(
                patch(
                    "play_book_studio.intake.normalization.builders.convert_with_markitdown",
                    return_value="# 운영 점검\n\n값 요약",
                )
            )
            result = ingest_customer_pack(
                root,
                {
                    "source_type": "xlsx",
                    "uri": str(source),
                    "title": "XLSX 샘플",
                    "approval_state": "approved",
                },
            )

        book = dict(result.get("book") or {})
        scorecard = dict(book.get("parser_challenger_scorecard") or {})
        candidates = {
            str(candidate.get("candidate_id") or ""): candidate
            for candidate in (scorecard.get("candidates") or [])
            if isinstance(candidate, dict)
        }
        assert scorecard["current_candidate_id"] == "markitdown_xlsx"
        assert candidates["xlsx_native_sheet_extract"]["comparison_status"] == "evaluated"
        assert candidates["xlsx_native_sheet_extract"]["document_block_count"] >= 2
        assert scorecard["recommended_candidate_id"] == "xlsx_native_sheet_extract"


def test_pdf_ingest_evaluates_docling_challenger_scorecard() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        source = root / "sample.pdf"
        source.write_bytes(b"%PDF-1.4 fake pdf")

        with ExitStack() as stack:
            for manager in _embedding_patches():
                stack.enter_context(manager)
            stack.enter_context(
                patch(
                    "play_book_studio.intake.normalization.builders.convert_with_markitdown",
                    return_value="# PDF 요약\n\n짧은 본문",
                )
            )
            stack.enter_context(
                patch(
                    "play_book_studio.intake.normalization.service.extract_pdf_markdown_with_docling",
                    return_value="# 운영 점검\n\n본문 설명\n\n| 항목 | 값 |\n| --- | --- |\n| 모드 | active |",
                )
            )
            stack.enter_context(
                patch(
                    "play_book_studio.intake.normalization.service.extract_pdf_markdown_with_docling_ocr",
                    return_value="",
                )
            )
            stack.enter_context(
                patch(
                    "play_book_studio.intake.normalization.service.extract_pdf_pages",
                    return_value=["fallback page"],
                )
            )
            stack.enter_context(
                patch(
                    "play_book_studio.intake.normalization.service.extract_pdf_outline",
                    return_value=[],
                )
            )
            result = ingest_customer_pack(
                root,
                {
                    "source_type": "pdf",
                    "uri": str(source),
                    "title": "PDF 샘플",
                    "approval_state": "approved",
                },
            )

        book = dict(result.get("book") or {})
        scorecard = dict(book.get("parser_challenger_scorecard") or {})
        candidates = {
            str(candidate.get("candidate_id") or ""): candidate
            for candidate in (scorecard.get("candidates") or [])
            if isinstance(candidate, dict)
        }
        assert scorecard["current_candidate_id"] == "markitdown_pdf"
        assert candidates["docling_pdf"]["comparison_status"] == "evaluated"
        assert candidates["docling_pdf"]["quality_verdict"] == "gold_candidate"
        assert scorecard["recommended_candidate_id"] == "docling_pdf"
