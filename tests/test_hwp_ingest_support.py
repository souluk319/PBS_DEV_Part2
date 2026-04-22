from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from play_book_studio.app.intake_api import (
    build_customer_pack_support_matrix,
    customer_pack_request_from_payload,
)
from play_book_studio.intake.normalization.unhwp_adapter import (
    _run_unhwp_convert,
    extract_hwp_markdown_with_unhwp,
    extract_hwp_rows_with_unhwp,
    probe_unhwp,
)


def test_customer_pack_request_accepts_hwp_and_hwpx() -> None:
    for source_type in ("hwp", "hwpx"):
        request = customer_pack_request_from_payload(
            {
                "source_type": source_type,
                "uri": f"C:/tmp/sample.{source_type}",
                "title": "sample",
            }
        )
        assert request.source_type == source_type


def test_support_matrix_includes_hwp_and_hwpx_entries() -> None:
    matrix = build_customer_pack_support_matrix()
    entries = {
        str(entry.get("format_id") or ""): entry
        for entry in (matrix.get("entries") or [])
        if isinstance(entry, dict)
    }

    assert entries["hwp"]["source_type"] == "hwp"
    assert entries["hwp"]["support_status"] == "staged"
    assert entries["hwp"]["normalization_strategy"] == "unhwp_structured_extract_v1"
    assert ".hwp" in entries["hwp"]["accepted_extensions"]

    assert entries["hwpx"]["source_type"] == "hwpx"
    assert entries["hwpx"]["support_status"] == "staged"
    assert entries["hwpx"]["normalization_strategy"] == "unhwp_structured_extract_v1"
    assert ".hwpx" in entries["hwpx"]["accepted_extensions"]


def test_probe_unhwp_reports_not_configured_when_missing() -> None:
    with patch("play_book_studio.intake.normalization.unhwp_adapter.shutil.which", return_value=""):
        payload = probe_unhwp()

    assert payload["ready"] is False
    assert payload["status"] == "not_configured"


def test_extract_hwp_markdown_with_unhwp_reads_generated_markdown(tmp_path: Path) -> None:
    source = tmp_path / "sample.hwp"
    source.write_bytes(b"fake-hwp")

    def _fake_run(path: Path, *, output_dir: Path, settings=None) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "extract.md").write_text("# 제목\n\n본문", encoding="utf-8")
        (output_dir / "extract.txt").write_text("본문", encoding="utf-8")
        (output_dir / "content.json").write_text(json.dumps({"sections": []}), encoding="utf-8")

    with patch(
        "play_book_studio.intake.normalization.unhwp_adapter._run_unhwp_convert",
        side_effect=_fake_run,
    ):
        markdown = extract_hwp_markdown_with_unhwp(source)

    assert "# 제목" in markdown
    assert "본문" in markdown


def test_extract_hwp_rows_with_unhwp_prefers_structured_content_json(tmp_path: Path) -> None:
    source = tmp_path / "sample.hwpx"
    source.write_bytes(b"fake-hwpx")

    structured_payload = {
        "sections": [
            {
                "content": [
                    {
                        "Paragraph": {
                            "style": {"heading_level": 0},
                            "content": [{"Text": {"text": "1. 개요"}}],
                        }
                    },
                    {
                        "Paragraph": {
                            "style": {"heading_level": 0},
                            "content": [{"Text": {"text": "첫 번째 설명"}}],
                        }
                    },
                    {
                        "Table": {
                            "rows": [
                                {
                                    "cells": [
                                        {"content": [{"Text": {"text": "항목"}}]},
                                        {"content": [{"Text": {"text": "값"}}]},
                                    ]
                                },
                                {
                                    "cells": [
                                        {"content": [{"Text": {"text": "모드"}}]},
                                        {"content": [{"Text": {"text": "active"}}]},
                                    ]
                                },
                            ]
                        }
                    },
                ]
            }
        ]
    }

    def _fake_run(path: Path, *, output_dir: Path, settings=None) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "content.json").write_text(json.dumps(structured_payload), encoding="utf-8")

    with patch(
        "play_book_studio.intake.normalization.unhwp_adapter._run_unhwp_convert",
        side_effect=_fake_run,
    ):
        rows = extract_hwp_rows_with_unhwp(
            source,
            book_slug="sample-book",
            book_title="샘플 문서",
            source_url="/tmp/sample.hwpx",
            viewer_path_base="/playbooks/customer-packs/draft/index.html",
        )

    assert len(rows) == 1
    assert rows[0]["heading"] == "1. 개요"
    assert "첫 번째 설명" in str(rows[0]["text"])
    assert "[TABLE]" in str(rows[0]["text"])


def test_run_unhwp_convert_forces_utf8_subprocess(tmp_path: Path) -> None:
    source = tmp_path / "sample.hwpx"
    source.write_bytes(b"fake-hwpx")
    output_dir = tmp_path / "output"

    with (
        patch(
            "play_book_studio.intake.normalization.unhwp_adapter._resolve_unhwp_bin",
            return_value="C:/tools/unhwp.exe",
        ),
        patch("play_book_studio.intake.normalization.unhwp_adapter.subprocess.run") as run_mock,
    ):
        _run_unhwp_convert(source, output_dir=output_dir)

    _, kwargs = run_mock.call_args
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["errors"] == "replace"
