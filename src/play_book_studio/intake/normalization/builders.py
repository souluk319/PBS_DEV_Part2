from __future__ import annotations

# captured source에서 canonical study asset을 조립하는 web/pdf 빌더 모음.

from collections.abc import Callable
from pathlib import Path
import re
from typing import Any

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.models import SourceManifestEntry
from play_book_studio.ingestion.normalize import extract_sections

from ..models import CustomerPackDraftRecord
from ..planner import CustomerPackPlanner
from .pdf import (
    extract_pdf_markdown_with_docling,
    extract_pdf_markdown_with_docling_ocr,
    extract_pdf_outline,
    extract_pdf_pages,
)
from .markitdown_adapter import MARKITDOWN_SOURCE_TYPES, convert_with_markitdown
from .pdf_rows import (
    _build_pdf_rows,
    _build_pdf_rows_from_docling_markdown,
    _docling_korean_quality_ok,
)
from .unhwp_adapter import extract_hwp_markdown_with_unhwp, extract_hwp_rows_with_unhwp

try:  # pragma: no cover - optional runtime dependency
    from docling.document_converter import DocumentConverter
except Exception:  # noqa: BLE001
    DocumentConverter = None

try:  # pragma: no cover - optional runtime dependency
    from docx import Document as DocxDocument
    from docx.document import Document as DocxDocumentType
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table as DocxTable
    from docx.text.paragraph import Paragraph as DocxParagraph
except Exception:  # noqa: BLE001
    DocxDocument = None
    DocxDocumentType = None
    CT_Tbl = None
    CT_P = None
    DocxTable = None
    DocxParagraph = None

try:  # pragma: no cover - optional runtime dependency
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
except Exception:  # noqa: BLE001
    Presentation = None
    MSO_SHAPE_TYPE = None

try:  # pragma: no cover - optional runtime dependency
    from openpyxl import load_workbook
except Exception:  # noqa: BLE001
    load_workbook = None


def build_canonical_book(
    record: CustomerPackDraftRecord,
    *,
    settings: Settings | None = None,
    extract_pdf_markdown_with_docling_fn: Callable[[Path], str] = extract_pdf_markdown_with_docling,
    extract_pdf_markdown_with_docling_ocr_fn: Callable[[Path], str] = extract_pdf_markdown_with_docling_ocr,
    extract_pdf_outline_fn: Callable[[Path], list] = extract_pdf_outline,
    extract_pdf_pages_fn: Callable[[Path], list[str]] = extract_pdf_pages,
):
    if record.request.source_type in MARKITDOWN_SOURCE_TYPES:
        return _build_markitdown_first_canonical_book(
            record,
            extract_pdf_markdown_with_docling_fn=extract_pdf_markdown_with_docling_fn,
            extract_pdf_markdown_with_docling_ocr_fn=extract_pdf_markdown_with_docling_ocr_fn,
            extract_pdf_outline_fn=extract_pdf_outline_fn,
            extract_pdf_pages_fn=extract_pdf_pages_fn,
        )
    if record.request.source_type == "pdf":
        return _build_pdf_canonical_book(
            record,
            extract_pdf_markdown_with_docling_fn=extract_pdf_markdown_with_docling_fn,
            extract_pdf_markdown_with_docling_ocr_fn=extract_pdf_markdown_with_docling_ocr_fn,
            extract_pdf_outline_fn=extract_pdf_outline_fn,
            extract_pdf_pages_fn=extract_pdf_pages_fn,
        )
    if record.request.source_type == "web":
        return _build_web_canonical_book(record)
    if record.request.source_type in {"md", "asciidoc", "txt"}:
        return _build_text_canonical_book(record)
    if record.request.source_type == "docx":
        return _build_docx_canonical_book(record)
    if record.request.source_type == "pptx":
        return _build_pptx_canonical_book(record, settings=settings)
    if record.request.source_type == "xlsx":
        return _build_xlsx_canonical_book(record)
    if record.request.source_type in {"hwp", "hwpx"}:
        return _build_hwp_canonical_book(record, settings=settings)
    if record.request.source_type == "image":
        return _build_image_canonical_book(record)
    raise ValueError("지원하지 않는 source_type입니다.")


def _append_normalization_note(book, note: str):
    book.notes = tuple(book.notes) + (note,)
    return book


def _build_markitdown_first_canonical_book(
    record: CustomerPackDraftRecord,
    *,
    extract_pdf_markdown_with_docling_fn: Callable[[Path], str],
    extract_pdf_markdown_with_docling_ocr_fn: Callable[[Path], str],
    extract_pdf_outline_fn: Callable[[Path], list],
    extract_pdf_pages_fn: Callable[[Path], list[str]],
):
    try:
        return _append_normalization_note(
            _build_markitdown_canonical_book(record),
            f"Normalization backend: MarkItDown ({record.request.source_type} -> markdown).",
        )
    except Exception as exc:
        fallback_builder = {
            "pdf": lambda: _build_pdf_canonical_book(
                record,
                extract_pdf_markdown_with_docling_fn=extract_pdf_markdown_with_docling_fn,
                extract_pdf_markdown_with_docling_ocr_fn=extract_pdf_markdown_with_docling_ocr_fn,
                extract_pdf_outline_fn=extract_pdf_outline_fn,
                extract_pdf_pages_fn=extract_pdf_pages_fn,
            ),
            "docx": lambda: _build_docx_canonical_book(record),
            "pptx": lambda: _build_pptx_canonical_book(record),
            "xlsx": lambda: _build_xlsx_canonical_book(record),
        }[record.request.source_type]
        return _append_normalization_note(
            fallback_builder(),
            f"Normalization backend: legacy fallback after MarkItDown failure ({exc.__class__.__name__}).",
        )


def _build_markitdown_canonical_book(record: CustomerPackDraftRecord):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
    markdown = convert_with_markitdown(capture_path)
    if _markitdown_output_is_low_confidence(record.request.source_type, markdown):
        raise ValueError(f"MarkItDown produced low-confidence {record.request.source_type} output.")
    normalized = _normalize_text_block(
        "md",
        markdown,
        origin_source_type=record.request.source_type,
        book_title=record.plan.title,
    )
    if not normalized:
        raise ValueError(f"{record.request.source_type.upper()}에서 canonical section을 만들지 못했습니다.")
    return _build_structured_text_canonical_book(
        record,
        source_type="md",
        normalized=normalized,
        origin_source_type=record.request.source_type,
    )


def _markitdown_output_is_low_confidence(source_type: str, markdown: str) -> bool:
    stripped = str(markdown or "").strip()
    if not stripped:
        return True
    if source_type == "pdf":
        compact = stripped.replace("\ufeff", "").strip()
        if compact.lower().startswith("%pdf-"):
            return True
    return False


def _build_web_canonical_book(record: CustomerPackDraftRecord):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")

    html = capture_path.read_text(encoding="utf-8")
    manifest_entry = SourceManifestEntry(
        book_slug=record.plan.book_slug,
        title=record.plan.title,
        source_url=record.request.uri,
        viewer_path=f"/playbooks/customer-packs/{record.draft_id}/index.html",
        high_value=False,
        viewer_strategy="internal_text",
        body_language_guess=record.request.language_hint,
        approval_status="derived",
    )
    sections = extract_sections(html, manifest_entry)
    if not sections:
        raise ValueError("capture한 문서에서 canonical section을 만들지 못했습니다.")
    rows = [section.to_dict() for section in sections]
    return CustomerPackPlanner().build_canonical_book(rows, request=record.request)


def _build_pdf_canonical_book(
    record: CustomerPackDraftRecord,
    *,
    extract_pdf_markdown_with_docling_fn: Callable[[Path], str],
    extract_pdf_markdown_with_docling_ocr_fn: Callable[[Path], str],
    extract_pdf_outline_fn: Callable[[Path], list],
    extract_pdf_pages_fn: Callable[[Path], list[str]],
):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
    try:
        markdown = extract_pdf_markdown_with_docling_fn(capture_path)
        markdown_rows = _build_pdf_rows_from_docling_markdown(markdown, record)
        # Quality gate: docling sometimes merges Korean characters without spaces
        # (e.g. "컨트롤플레인정보"). Detect and fall back to pypdf in that case.
        if markdown_rows and _docling_korean_quality_ok(markdown_rows):
            return _append_normalization_note(
                CustomerPackPlanner().build_canonical_book(markdown_rows, request=record.request),
                "Normalization backend: docling pdf structured extract.",
            )
    except Exception:
        pass
    try:
        markdown = extract_pdf_markdown_with_docling_ocr_fn(capture_path)
        markdown_rows = _build_pdf_rows_from_docling_markdown(markdown, record)
        if markdown_rows:
            return _append_normalization_note(
                CustomerPackPlanner().build_canonical_book(markdown_rows, request=record.request),
                "Normalization backend: docling pdf ocr extract.",
            )
    except Exception:
        pass
    pages = extract_pdf_pages_fn(capture_path)
    outline = extract_pdf_outline_fn(capture_path)
    rows = _build_pdf_rows(pages, record, outline=outline)
    if not rows:
        raise ValueError("PDF에서 canonical section을 만들지 못했습니다.")
    return _append_normalization_note(
        CustomerPackPlanner().build_canonical_book(rows, request=record.request),
        "Normalization backend: pypdf text fallback.",
    )


_MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_ASCIIDOC_HEADING_RE = re.compile(r"^(={1,6})\s+(.*?)\s*$")
_NUMERIC_HEADING_RE = re.compile(r"^(\d+(?:\.\d+){0,5})\.?\s+(.*?)\s*$")
_FENCED_CODE_START_RE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})(?P<language>[\w.+-]*)\s*$")
_TABLE_SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")
_PDF_INLINE_PAGE_MARKER_RE = re.compile(r"^[가-힣A-Za-z][가-힣A-Za-z0-9\s()./_-]{1,24}\s+\d+$")
_TABLE_PLACEHOLDER_RE = re.compile(r"^[-–—=:./\\|]+$")
_GENERIC_TABLE_HEADER_TOKENS = {
    "이름",
    "항목",
    "용도",
    "값",
    "설명",
    "구분",
    "유형",
    "종류",
    "키",
    "비고",
    "예시",
    "플랫폼",
    "지원",
    "절차",
    "명령어",
    "name",
    "item",
    "type",
    "value",
    "description",
    "purpose",
    "notes",
    "command",
}


def _slug_anchor(value: str, *, ordinal: int) -> str:
    cleaned = re.sub(r"[^a-z0-9가-힣]+", "-", value.strip().lower())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or f"section-{ordinal}"


def _is_fenced_code_closer(line: str, *, fence_char: str, minimum_width: int) -> bool:
    stripped = (line or "").strip()
    return bool(
        stripped
        and len(stripped) >= minimum_width
        and set(stripped) == {fence_char}
    )


def _replace_fenced_code_blocks(text: str) -> str:
    lines = text.split("\n")
    normalized_lines: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = _FENCED_CODE_START_RE.match(line)
        if match is None:
            normalized_lines.append(line)
            index += 1
            continue
        fence = match.group("fence")
        language = str(match.group("language") or "").strip().lower()
        body_lines: list[str] = []
        index += 1
        while index < len(lines):
            candidate = lines[index]
            if _is_fenced_code_closer(candidate, fence_char=fence[0], minimum_width=len(fence)):
                index += 1
                break
            body_lines.append(candidate)
            index += 1
        attrs = f' language="{language}"' if language else ""
        body = "\n".join(body_lines).strip("\n")
        normalized_lines.append(f"[CODE{attrs}]\n{body}\n[/CODE]")
    return "\n".join(normalized_lines)


def _split_markdown_table_row(line: str) -> list[str] | None:
    stripped = (line or "").strip()
    if "|" not in stripped:
        return None
    inner = stripped[1:-1] if stripped.startswith("|") and stripped.endswith("|") else stripped
    cells = [cell.strip() for cell in inner.split("|")]
    if len(cells) < 2:
        return None
    return cells


def _is_markdown_table_separator(row: list[str]) -> bool:
    return bool(row) and all(_TABLE_SEPARATOR_CELL_RE.fullmatch(cell or "") for cell in row)


def _replace_markdown_tables(text: str) -> str:
    lines = text.split("\n")
    normalized_lines: list[str] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("[CODE"):
            normalized_lines.append(lines[index])
            index += 1
            while index < len(lines):
                normalized_lines.append(lines[index])
                if lines[index].strip() == "[/CODE]":
                    index += 1
                    break
                index += 1
            continue
        if stripped.startswith("[TABLE"):
            normalized_lines.append(lines[index])
            index += 1
            while index < len(lines):
                normalized_lines.append(lines[index])
                if lines[index].strip() == "[/TABLE]":
                    index += 1
                    break
                index += 1
            continue
        header = _split_markdown_table_row(lines[index])
        separator = _split_markdown_table_row(lines[index + 1]) if index + 1 < len(lines) else None
        if (
            header
            and separator
            and len(header) == len(separator)
            and _is_markdown_table_separator(separator)
        ):
            table_rows = [header]
            index += 2
            while index < len(lines):
                row = _split_markdown_table_row(lines[index])
                if row is None or len(row) != len(header):
                    break
                table_rows.append(row)
                index += 1
            normalized_lines.append(_table_to_tagged_text(table_rows))
            continue
        normalized_lines.append(lines[index])
        index += 1
    return "\n".join(normalized_lines)


def _pdf_title_tokens(title: str) -> tuple[str, ...]:
    compact = re.sub(r"\([^)]*\)", " ", str(title or ""))
    compact = re.sub(r"^\d+(?:[.\-]\d+)*\s*", " ", compact).strip()
    tokens = [
        token
        for token in re.findall(r"[A-Za-z가-힣]{2,}", compact)
        if token.lower() not in {"openshift", "container", "platform"}
    ]
    return tuple(dict.fromkeys(tokens))


def _should_drop_pdf_inline_page_marker(line: str, *, book_title: str) -> bool:
    stripped = (line or "").strip()
    if not stripped or not _PDF_INLINE_PAGE_MARKER_RE.fullmatch(stripped):
        return False
    lowered = stripped.lower()
    return any(token.lower() in lowered for token in _pdf_title_tokens(book_title))


def _clean_pdf_markitdown_text(text: str, *, book_title: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in str(text or "").replace("\x00", "").splitlines():
        if _should_drop_pdf_inline_page_marker(raw_line, book_title=book_title):
            continue
        cleaned_lines.append(raw_line)
    return "\n".join(cleaned_lines)


def _looks_like_table_fragment(text: str) -> bool:
    stripped = (text or "").strip()
    return stripped.count("|") >= 2 or (stripped.startswith("|") and stripped.endswith("|"))


def _normalize_text_block(
    source_type: str,
    text: str,
    *,
    origin_source_type: str = "",
    book_title: str = "",
) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if origin_source_type == "pdf":
        normalized = _clean_pdf_markitdown_text(normalized, book_title=book_title)
    if source_type in {"md", "asciidoc"}:
        normalized = _replace_fenced_code_blocks(normalized)
    if source_type == "md":
        normalized = _replace_markdown_tables(normalized)
    return normalized.strip()


def _text_heading_match(
    source_type: str,
    line: str,
    *,
    origin_source_type: str = "",
) -> tuple[int, str] | None:
    stripped = line.strip()
    if not stripped:
        return None
    if source_type == "md":
        match = _MARKDOWN_HEADING_RE.match(stripped)
        if match:
            return len(match.group(1)), match.group(2).strip()
    if source_type == "asciidoc":
        match = _ASCIIDOC_HEADING_RE.match(stripped)
        if match:
            return len(match.group(1)), match.group(2).strip()
    match = _NUMERIC_HEADING_RE.match(stripped)
    if match:
        if origin_source_type == "pdf" and _looks_like_table_fragment(stripped):
            return None
        return match.group(1).count(".") + 1, f"{match.group(1)} {match.group(2).strip()}".strip()
    return None


def _build_text_canonical_book(record: CustomerPackDraftRecord):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")

    normalized = _normalize_text_block(record.request.source_type, capture_path.read_text(encoding="utf-8"))
    return _build_structured_text_canonical_book(
        record,
        source_type=record.request.source_type,
        normalized=normalized,
    )


def _build_structured_text_canonical_book(
    record: CustomerPackDraftRecord,
    *,
    source_type: str,
    normalized: str,
    origin_source_type: str = "",
):
    if not normalized:
        raise ValueError("텍스트 소스에서 canonical section을 만들지 못했습니다.")

    viewer_base = f"/playbooks/customer-packs/{record.draft_id}/index.html"
    current_heading = record.plan.title or record.plan.book_slug
    current_level = 1
    current_body: list[str] = []
    path_stack: list[str] = [current_heading]
    rows: list[dict[str, object]] = []
    active_block_end = ""

    def flush() -> None:
        ordinal = len(rows) + 1
        heading = current_heading.strip() or f"Section {ordinal}"
        anchor = _slug_anchor(heading, ordinal=ordinal)
        body = "\n".join(current_body).strip()
        if not body:
            return
        section_path = tuple(path_stack[:current_level]) if path_stack else (heading,)
        rows.append(
            {
                "book_slug": record.plan.book_slug,
                "book_title": record.plan.title,
                "heading": heading,
                "section_level": current_level,
                "section_path": list(section_path),
                "anchor": anchor,
                "source_url": record.request.uri,
                "viewer_path": f"{viewer_base}#{anchor}",
                "text": body,
            }
        )

    for line in normalized.splitlines():
        stripped_line = line.strip()
        if active_block_end:
            current_body.append(line)
            if stripped_line == active_block_end:
                active_block_end = ""
            continue
        if stripped_line.startswith("[CODE"):
            active_block_end = "[/CODE]"
            current_body.append(line)
            continue
        if stripped_line.startswith("[TABLE"):
            active_block_end = "[/TABLE]"
            current_body.append(line)
            continue
        if stripped_line.startswith("[FIGURE"):
            active_block_end = "[/FIGURE]"
            current_body.append(line)
            continue
        heading = _text_heading_match(
            source_type,
            line,
            origin_source_type=origin_source_type,
        )
        if heading:
            if not rows and not "\n".join(current_body).strip():
                current_level, current_heading = heading
                path_stack = path_stack[: max(current_level - 1, 0)]
                path_stack.append(current_heading)
                current_body = []
                continue
            flush()
            current_level, current_heading = heading
            path_stack = path_stack[: max(current_level - 1, 0)]
            path_stack.append(current_heading)
            current_body = []
            continue
        current_body.append(line)

    flush()
    return CustomerPackPlanner().build_canonical_book(rows, request=record.request)


def _table_to_tagged_text(rows: list[list[str]]) -> str:
    normalized_rows = [
        [_normalize_table_cell_text(cell) for cell in row]
        for row in rows
        if any(_table_cell_has_value(cell) for cell in row)
    ]
    if not normalized_rows:
        return ""
    rendered_rows, has_header = _repair_table_rows_for_storage(normalized_rows)
    attrs = "" if has_header else ' header="false"'
    return f"[TABLE{attrs}]\n" + "\n".join(rendered_rows) + "\n[/TABLE]"


def _normalize_table_cell_text(cell: str) -> str:
    normalized = " ".join(str(cell or "").replace("\u00a0", " ").split()).strip()
    if _TABLE_PLACEHOLDER_RE.fullmatch(normalized):
        return ""
    return normalized


def _table_cell_has_value(cell: str) -> bool:
    return bool(_normalize_table_cell_text(cell))


def _trim_sparse_table_columns(rows: list[list[str]]) -> list[list[str]]:
    normalized_rows = [
        [_normalize_table_cell_text(cell) for cell in row]
        for row in rows
        if any(_table_cell_has_value(cell) for cell in row)
    ]
    if not normalized_rows:
        return []
    width = max(len(row) for row in normalized_rows)
    padded_rows = [row + [""] * (width - len(row)) for row in normalized_rows]
    keep_indexes = [
        index
        for index in range(width)
        if any(_table_cell_has_value(row[index]) for row in padded_rows)
    ]
    if not keep_indexes:
        keep_indexes = [0]
    return [[row[index] for index in keep_indexes] for row in padded_rows]


def _table_meaningful_cells(row: list[str]) -> list[str]:
    return [cell for cell in (_normalize_table_cell_text(item) for item in row) if cell]


def _looks_like_sparse_pdf_table(rows: list[list[str]]) -> bool:
    if len(rows) < 2:
        return False
    total_cells = sum(len(row) for row in rows)
    if total_cells <= 0:
        return False
    emptyish_cells = sum(
        1
        for row in rows
        for cell in row
        if not _table_cell_has_value(cell)
    )
    max_cols = max(len(row) for row in rows)
    compact_rows = sum(1 for row in rows if len(_table_meaningful_cells(row)) <= 4)
    return max_cols >= 4 and (emptyish_cells / total_cells) >= 0.35 and compact_rows >= max(2, len(rows) - 1)


def _collapse_sparse_table_rows(rows: list[list[str]]) -> list[list[str]]:
    collapsed: list[list[str]] = []
    for row in rows:
        meaningful = _table_meaningful_cells(row)
        if not meaningful:
            continue
        key = meaningful[0].rstrip(":").strip()
        remainder = " ".join(meaningful[1:]).strip()
        if remainder:
            collapsed.append([key, remainder])
        else:
            collapsed.append([key])
    return collapsed


def _collapsed_rows_have_header(rows: list[list[str]]) -> bool:
    if len(rows) < 2:
        return False
    header = rows[0]
    if len(header) < 2:
        return False
    first = header[0].strip().lower()
    second = header[1].strip().lower()
    if first in _GENERIC_TABLE_HEADER_TOKENS or second in _GENERIC_TABLE_HEADER_TOKENS:
        return True
    if len(first) <= 12 and len(second) <= 16 and not first.endswith(":") and not second.endswith(":"):
        return first in {"field", "key", "setting"} or second in {"value", "description", "purpose"}
    return False


def _repair_table_rows_for_storage(rows: list[list[str]]) -> tuple[list[str], bool]:
    normalized_rows = _trim_sparse_table_columns(rows)
    if not normalized_rows:
        return [], False
    has_header = True
    render_rows = normalized_rows
    if _looks_like_sparse_pdf_table(rows):
        collapsed_rows = _collapse_sparse_table_rows(normalized_rows)
        if collapsed_rows:
            render_rows = collapsed_rows
            has_header = _collapsed_rows_have_header(collapsed_rows)
    if len(render_rows) <= 1:
        has_header = False
    rendered = [" | ".join(cell or "-" for cell in row) for row in render_rows]
    return rendered, has_header


def _iter_docx_blocks(document: Any):
    if not all((DocxDocumentType, CT_P, CT_Tbl, DocxParagraph, DocxTable)):
        raise RuntimeError("python-docx dependency is unavailable")
    parent = document.element.body
    for child in parent.iterchildren():
        if isinstance(child, CT_P):
            yield DocxParagraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield DocxTable(child, document)


def _docx_to_structured_text(capture_path: Path) -> str:
    if DocxDocument is None:
        raise RuntimeError("python-docx dependency is unavailable")
    document = DocxDocument(capture_path)
    lines: list[str] = []
    for block in _iter_docx_blocks(document):
        if DocxParagraph is not None and isinstance(block, DocxParagraph):
            text = block.text.strip()
            if not text:
                continue
            style_name = str(getattr(getattr(block, "style", None), "name", "") or "").lower()
            if style_name.startswith("heading"):
                match = re.search(r"(\d+)", style_name)
                level = max(1, min(int(match.group(1)) if match else 1, 6))
                lines.append(f"{'#' * level} {text}")
            else:
                lines.append(text)
            continue
        if DocxTable is not None and isinstance(block, DocxTable):
            table_rows = [
                [cell.text.strip() for cell in row.cells]
                for row in block.rows
            ]
            table_text = _table_to_tagged_text(table_rows)
            if table_text:
                lines.append(table_text)
    return "\n\n".join(line for line in lines if line).strip()


def _pptx_to_structured_text(capture_path: Path) -> str:
    if Presentation is None:
        raise RuntimeError("python-pptx dependency is unavailable")
    presentation = Presentation(capture_path)
    lines: list[str] = []
    for index, slide in enumerate(presentation.slides, start=1):
        title = ""
        if slide.shapes.title is not None and getattr(slide.shapes.title, "text", "").strip():
            title = slide.shapes.title.text.strip()
        if not title:
            title = f"Slide {index}"
        lines.append(f"# {title}")
        for shape in slide.shapes:
            text = getattr(shape, "text", "").strip()
            if text and text != title:
                lines.append(text)
            if getattr(shape, "has_table", False):
                table_rows = []
                for row in shape.table.rows:
                    table_rows.append([cell.text.strip() for cell in row.cells])
                table_text = _table_to_tagged_text(table_rows)
                if table_text:
                    lines.append(table_text)
    return "\n\n".join(line for line in lines if line).strip()


def _pptx_shape_sort_key(shape: Any) -> tuple[int, int, int]:
    return (
        int(getattr(shape, "top", 0) or 0),
        int(getattr(shape, "left", 0) or 0),
        int(getattr(shape, "shape_id", 0) or 0),
    )


def _pptx_shape_type_code(shape: Any) -> int:
    try:
        return int(getattr(shape, "shape_type", 0) or 0)
    except Exception:  # noqa: BLE001
        return 0


def _pptx_is_group_shape(shape: Any) -> bool:
    if MSO_SHAPE_TYPE is not None and getattr(shape, "shape_type", None) == MSO_SHAPE_TYPE.GROUP:
        return True
    return _pptx_shape_type_code(shape) == 6 and hasattr(shape, "shapes")


def _pptx_is_picture_shape(shape: Any) -> bool:
    if MSO_SHAPE_TYPE is not None and getattr(shape, "shape_type", None) == MSO_SHAPE_TYPE.PICTURE:
        return True
    return _pptx_shape_type_code(shape) == 13 and hasattr(shape, "image")


def _iter_pptx_content_shapes(shapes: Any):
    for shape in sorted(shapes, key=_pptx_shape_sort_key):
        if _pptx_is_group_shape(shape):
            yield from _iter_pptx_content_shapes(getattr(shape, "shapes", []))
            continue
        yield shape


def _pptx_marker_escape(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"').strip()


def _pptx_marker_figure_text(
    *,
    asset_ref: str,
    alt: str,
    caption: str,
    placement_hint: str,
) -> str:
    attrs = [
        f'ref="{_pptx_marker_escape(asset_ref)}"',
        f'alt="{_pptx_marker_escape(alt)}"',
    ]
    if placement_hint.strip():
        attrs.append(f'placement_hint="{_pptx_marker_escape(placement_hint)}"')
    body = str(caption or "").strip()
    if body:
        return "[FIGURE {attrs}]\n{body}\n[/FIGURE]".format(
            attrs=" ".join(attrs),
            body=body,
        )
    return "[FIGURE {attrs}]\n[/FIGURE]".format(attrs=" ".join(attrs))


def _pptx_image_ext(image: Any) -> str:
    ext = re.sub(r"[^a-z0-9]+", "", str(getattr(image, "ext", "") or "").lower())
    if ext in {"jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff", "webp"}:
        return "jpg" if ext == "jpeg" else ext
    return "png"


def _pptx_shape_preview_text(shape: Any) -> str:
    if getattr(shape, "has_text_frame", False):
        for block in _pptx_shape_paragraph_blocks(shape):
            normalized = " ".join(str(block or "").split()).strip()
            if normalized:
                return normalized[:200]
    if getattr(shape, "has_table", False):
        return _pptx_table_first_row_text(shape)[:200]
    return ""


def _pptx_extract_figure_asset(
    shape: Any,
    *,
    asset_dir: Path,
    slide_ordinal: int,
    figure_ordinal: int,
    title: str,
    nearby_text: str,
) -> dict[str, object] | None:
    try:
        image = shape.image
        blob = image.blob
    except Exception:  # noqa: BLE001
        return None
    if not blob:
        return None
    asset_ref = f"slide-{slide_ordinal:03d}-figure-{figure_ordinal:02d}.{_pptx_image_ext(image)}"
    asset_path = asset_dir / asset_ref
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    asset_path.write_bytes(blob)
    width_px = 0
    height_px = 0
    try:
        width_px, height_px = image.size
    except Exception:  # noqa: BLE001
        width_px = 0
        height_px = 0
    source_page_or_slide = f"slide:{slide_ordinal}"
    placement_hint = "{slide}:shape:{shape_id}:{top}:{left}".format(
        slide=source_page_or_slide,
        shape_id=int(getattr(shape, "shape_id", 0) or 0),
        top=int(getattr(shape, "top", 0) or 0),
        left=int(getattr(shape, "left", 0) or 0),
    )
    alt = f"{title or f'Slide {slide_ordinal}'} image {figure_ordinal}"
    return {
        "asset_ref": asset_ref,
        "asset_name": asset_ref,
        "content_type": str(getattr(image, "content_type", "") or "application/octet-stream").strip()
        or "application/octet-stream",
        "source_page_or_slide": source_page_or_slide,
        "placement_hint": placement_hint,
        "caption": "",
        "alt": alt,
        "figure_type": "slide_image",
        "width_px": int(width_px or 0),
        "height_px": int(height_px or 0),
        "nearby_text": str(nearby_text or "").strip(),
    }


_PPTX_DATE_ONLY_RE = re.compile(r"^\d{4}[./-]\s*\d{1,2}[./-]\s*\d{1,2}\.?\s*$")
_PPTX_DOC_CODE_RE = re.compile(r"^[A-Z]{2,}-\d{2,}-\d{3,}")


def _pptx_table_first_row_text(shape: Any) -> str:
    if not getattr(shape, "has_table", False):
        return ""
    rows = list(getattr(shape.table, "rows", []))
    if not rows:
        return ""
    first_row = rows[0]
    tokens = [str(cell.text or "").strip() for cell in first_row.cells if str(cell.text or "").strip()]
    if len(tokens) == 1:
        return tokens[0]
    return " ".join(tokens).strip()


def _pptx_title_score(text: str, *, top: int, left: int, ordinal: int, from_table: bool, is_placeholder: bool) -> int:
    score = 0
    normalized = str(text or "").strip()
    if not normalized:
        return -10_000
    score -= min(top // 100000, 30)
    score -= min(left // 300000, 12)
    if is_placeholder:
        score += 30
    if from_table:
        score += 12
    if ordinal == 1 and from_table:
        score += 12
    if len(normalized) >= 8:
        score += 8
    if re.search(r"[가-힣A-Za-z]", normalized):
        score += 10
    if _PPTX_DATE_ONLY_RE.match(normalized):
        score -= 40
    if _PPTX_DOC_CODE_RE.match(normalized):
        score -= 30
    if len(normalized) <= 4:
        score -= 12
    if not re.search(r"[가-힣A-Za-z]", normalized):
        score -= 15
    return score


def _pptx_best_title(slide: Any, *, ordinal: int) -> tuple[str, set[int]]:
    text_candidates: list[tuple[int, str, set[int]]] = []
    table_candidates: list[tuple[int, str, set[int]]] = []
    title_shape = getattr(slide.shapes, "title", None)
    title_text = str(getattr(title_shape, "text", "") or "").strip()
    if title_text:
        text_candidates.append(
            (
                _pptx_title_score(
                    title_text,
                    top=int(getattr(title_shape, "top", 0) or 0),
                    left=int(getattr(title_shape, "left", 0) or 0),
                    ordinal=ordinal,
                    from_table=False,
                    is_placeholder=True,
                ),
                title_text,
                {int(getattr(title_shape, "shape_id", 0) or 0)},
            )
        )
    for shape in sorted(slide.shapes, key=_pptx_shape_sort_key):
        shape_id = int(getattr(shape, "shape_id", 0) or 0)
        top = int(getattr(shape, "top", 0) or 0)
        left = int(getattr(shape, "left", 0) or 0)
        if getattr(shape, "has_text_frame", False):
            text = str(getattr(shape, "text", "") or "").strip()
            if text:
                first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
                if first_line:
                    text_candidates.append(
                        (
                            _pptx_title_score(
                                first_line[:160],
                                top=top,
                                left=left,
                                ordinal=ordinal,
                                from_table=False,
                                is_placeholder=False,
                            ),
                            first_line[:160],
                            {shape_id},
                        )
                    )
        table_title = _pptx_table_first_row_text(shape)
        if table_title:
            table_candidates.append(
                (
                    _pptx_title_score(
                        table_title[:160],
                        top=top,
                        left=left,
                        ordinal=ordinal,
                        from_table=True,
                        is_placeholder=False,
                    ),
                    table_title[:160],
                    {shape_id},
                )
            )
    candidates = text_candidates
    if not candidates:
        candidates = table_candidates
    elif ordinal == 1:
        best_text_score = sorted(text_candidates, key=lambda item: item[0], reverse=True)[0][0]
        best_table = sorted(table_candidates, key=lambda item: item[0], reverse=True)[0] if table_candidates else None
        if best_table is not None and best_table[0] >= best_text_score + 10:
            candidates = [best_table]
    if candidates:
        candidates.sort(key=lambda item: item[0], reverse=True)
        _, title, consumed = candidates[0]
        return title, consumed
    return f"Slide {ordinal}", set()


def _pptx_paragraph_text(paragraph: Any) -> str:
    tokens = [str(getattr(run, "text", "") or "") for run in getattr(paragraph, "runs", [])]
    joined = "".join(tokens).strip()
    return joined or str(getattr(paragraph, "text", "") or "").strip()


def _pptx_shape_paragraph_blocks(shape: Any) -> list[str]:
    if not getattr(shape, "has_text_frame", False):
        return []
    paragraphs = [
        paragraph
        for paragraph in getattr(shape.text_frame, "paragraphs", [])
        if _pptx_paragraph_text(paragraph)
    ]
    if not paragraphs:
        return []
    blocks: list[str] = []
    for paragraph in paragraphs:
        text = _pptx_paragraph_text(paragraph)
        if not text:
            continue
        level = int(getattr(paragraph, "level", 0) or 0)
        if level > 0:
            blocks.append(f"{'  ' * level}- {text}".rstrip())
        else:
            blocks.append(text)
    return blocks


def _pptx_table_block(table: Any) -> str:
    table_rows: list[list[str]] = []
    for row in getattr(table, "rows", []):
        table_rows.append([str(cell.text or "").strip() for cell in row.cells])
    return _table_to_tagged_text(table_rows)


def _pptx_notes_block(slide: Any) -> str:
    try:
        notes_slide = slide.notes_slide
    except Exception:  # noqa: BLE001
        return ""
    blocks: list[str] = []
    for shape in sorted(notes_slide.shapes, key=_pptx_shape_sort_key):
        if not getattr(shape, "has_text_frame", False):
            continue
        text_blocks = _pptx_shape_paragraph_blocks(shape)
        for block in text_blocks:
            if block and "click to add notes" not in block.lower():
                blocks.append(block)
    if not blocks:
        return ""
    return "Slide Notes\n" + "\n".join(blocks)


def _extract_pptx_native_rows(
    record: CustomerPackDraftRecord,
    *,
    settings: Settings | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    capture_path = Path(record.capture_artifact_path)
    if Presentation is None:
        raise RuntimeError("python-pptx dependency is unavailable")
    presentation = Presentation(capture_path)
    viewer_base = f"/playbooks/customer-packs/{record.draft_id}/index.html"
    rows: list[dict[str, object]] = []
    figure_assets: list[dict[str, object]] = []
    asset_dir = None
    if settings is not None:
        asset_dir = settings.customer_pack_assets_dir / record.draft_id
        asset_dir.mkdir(parents=True, exist_ok=True)
    for ordinal, slide in enumerate(presentation.slides, start=1):
        title, consumed_shape_ids = _pptx_best_title(slide, ordinal=ordinal)
        body_blocks: list[str] = []
        last_text_preview = title
        slide_figure_ordinal = 0
        for shape in _iter_pptx_content_shapes(slide.shapes):
            if int(getattr(shape, "shape_id", 0) or 0) in consumed_shape_ids:
                continue
            if _pptx_is_picture_shape(shape):
                if asset_dir is not None:
                    slide_figure_ordinal += 1
                    figure_asset = _pptx_extract_figure_asset(
                        shape,
                        asset_dir=asset_dir,
                        slide_ordinal=ordinal,
                        figure_ordinal=slide_figure_ordinal,
                        title=title,
                        nearby_text=last_text_preview,
                    )
                    if figure_asset is not None:
                        figure_assets.append(figure_asset)
                        body_blocks.append(
                            _pptx_marker_figure_text(
                                asset_ref=str(figure_asset["asset_ref"]),
                                alt=str(figure_asset["alt"]),
                                caption=str(figure_asset["caption"]),
                                placement_hint=str(figure_asset["placement_hint"]),
                            )
                        )
                continue
            if getattr(shape, "has_table", False):
                table_text = _pptx_table_block(shape.table)
                if table_text:
                    body_blocks.append(table_text)
                    last_text_preview = _pptx_table_first_row_text(shape) or last_text_preview
                continue
            for block in _pptx_shape_paragraph_blocks(shape):
                if block and block != title:
                    body_blocks.append(block)
                    last_text_preview = " ".join(str(block).split()).strip()[:200] or last_text_preview
        notes_text = _pptx_notes_block(slide)
        if notes_text:
            body_blocks.append(notes_text)
        text = "\n\n".join(block for block in body_blocks if str(block).strip()).strip()
        if not text:
            continue
        anchor = _slug_anchor(title, ordinal=ordinal)
        rows.append(
            {
                "book_slug": record.plan.book_slug,
                "book_title": record.plan.title,
                "heading": title,
                "section_level": 1,
                "section_path": [title],
                "anchor": anchor,
                "source_url": record.request.uri,
                "viewer_path": f"{viewer_base}#{anchor}",
                "source_page_or_slide": f"slide:{ordinal}",
                "text": text,
            }
        )
    return rows, figure_assets


def _xlsx_to_structured_text(capture_path: Path) -> str:
    if load_workbook is None:
        raise RuntimeError("openpyxl dependency is unavailable")
    workbook = load_workbook(capture_path, read_only=True, data_only=True)
    try:
        lines: list[str] = []
        for sheet in workbook.worksheets:
            lines.append(f"# {sheet.title}")
            table_rows: list[list[str]] = []
            for row in sheet.iter_rows(values_only=True):
                rendered = ["" if value is None else str(value).strip() for value in row]
                if any(rendered):
                    table_rows.append(rendered)
            table_text = _table_to_tagged_text(table_rows)
            if table_text:
                lines.append(table_text)
        return "\n\n".join(line for line in lines if line).strip()
    finally:
        workbook.close()


def extract_image_markdown_with_docling(path: Path) -> str:
    if DocumentConverter is None:
        raise RuntimeError("docling dependency is unavailable")
    converter = DocumentConverter()
    result = converter.convert(str(path))
    markdown = result.document.export_to_markdown()
    return str(markdown or "").strip()


def image_markdown_is_low_confidence(markdown: str) -> bool:
    normalized = _normalize_text_block("md", str(markdown or ""))
    if not normalized:
        return True
    body_lines = []
    for line in normalized.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        body_lines.append(stripped)
    body = " ".join(body_lines).strip() or normalized
    token_count = len([token for token in re.split(r"\s+", body) if token])
    alnum_count = len(re.findall(r"[A-Za-z가-힣0-9]", body))
    return token_count < 3 and alnum_count < 12


def build_image_canonical_book_from_markdown(record: CustomerPackDraftRecord, markdown: str):
    normalized = _normalize_text_block("md", str(markdown or ""))
    if not normalized:
        raise ValueError("이미지 OCR에서 canonical section을 만들지 못했습니다.")
    return _build_structured_text_canonical_book(record, source_type="md", normalized=normalized)


def _build_docx_canonical_book(record: CustomerPackDraftRecord):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
    normalized = _docx_to_structured_text(capture_path)
    if not normalized:
        raise ValueError("DOCX에서 canonical section을 만들지 못했습니다.")
    return _append_normalization_note(
        _build_structured_text_canonical_book(record, source_type="md", normalized=normalized),
        "Normalization backend: docx native structure extract.",
    )


def _build_pptx_canonical_book(record: CustomerPackDraftRecord, *, settings: Settings | None = None):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
    rows, figure_assets = _extract_pptx_native_rows(record, settings=settings)
    if rows:
        return _append_normalization_note(
            CustomerPackPlanner().build_canonical_book(
                rows,
                request=record.request,
                figure_assets=figure_assets,
            ),
            "Normalization backend: pptx native slide extract (rows first).",
        )
    normalized = _pptx_to_structured_text(capture_path)
    if not normalized:
        raise ValueError("PPTX에서 canonical section을 만들지 못했습니다.")
    return _append_normalization_note(
        _build_structured_text_canonical_book(record, source_type="md", normalized=normalized),
        "Normalization backend: pptx fallback text extract.",
    )


def _build_xlsx_canonical_book(record: CustomerPackDraftRecord):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
    normalized = _xlsx_to_structured_text(capture_path)
    if not normalized:
        raise ValueError("XLSX에서 canonical section을 만들지 못했습니다.")
    return _append_normalization_note(
        _build_structured_text_canonical_book(record, source_type="md", normalized=normalized),
        "Normalization backend: xlsx native sheet extract.",
    )


def _build_hwp_canonical_book(record: CustomerPackDraftRecord, *, settings: Settings | None = None):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
    rows = extract_hwp_rows_with_unhwp(
        capture_path,
        book_slug=record.plan.book_slug,
        book_title=record.plan.title,
        source_url=record.request.uri,
        viewer_path_base=f"/playbooks/customer-packs/{record.draft_id}/index.html",
        settings=settings,
    )
    if rows:
        return _append_normalization_note(
            CustomerPackPlanner().build_canonical_book(rows, request=record.request),
            f"Normalization backend: unhwp structured rows first ({record.request.source_type}).",
        )
    normalized = extract_hwp_markdown_with_unhwp(capture_path, settings=settings)
    if not normalized:
        raise ValueError(f"{record.request.source_type.upper()}에서 canonical section을 만들지 못했습니다.")
    return _append_normalization_note(
        _build_structured_text_canonical_book(record, source_type="md", normalized=normalized),
        f"Normalization backend: unhwp ({record.request.source_type} -> structured extract / markdown bridge).",
    )


def _build_image_canonical_book(record: CustomerPackDraftRecord):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
    return build_image_canonical_book_from_markdown(
        record,
        extract_image_markdown_with_docling(capture_path),
    )
