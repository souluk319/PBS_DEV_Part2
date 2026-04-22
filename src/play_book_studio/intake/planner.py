from __future__ import annotations

# 업로드 문서를 canonical study asset으로 설계하는 planner 진입점.

import re
from pathlib import PurePosixPath
from urllib.parse import urlparse

from .capture.pdf import resolve_pdf_capture
from .capture.web import resolve_web_capture_url
from .models import (
    CanonicalBook,
    CanonicalBookDraft,
    CanonicalSection,
    DocumentBlock,
    DocSourceRequest,
    FigureAsset,
    IntakeFormatSupportEntry,
    IntakeOcrMetadata,
    IntakeSupportMatrix,
    SupportStatus,
)


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9가-힣]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "untitled-book"


def _infer_title(request: DocSourceRequest) -> str:
    if request.title.strip():
        return request.title.strip()

    if request.source_type in {"pdf", "md", "asciidoc", "txt", "docx", "pptx", "xlsx", "hwp", "hwpx", "image"}:
        path = PurePosixPath(request.uri.replace("\\", "/"))
        return path.stem or "Uploaded source"

    parsed = urlparse(request.uri)
    if parsed.path.strip("/"):
        return PurePosixPath(parsed.path).name or parsed.netloc or "Web source"
    return parsed.netloc or "Web source"


def _infer_product(*values: str) -> str:
    haystack = " ".join(value.strip().lower() for value in values if value).strip()
    if not haystack:
        return "unknown"
    if (
        "openshift" in haystack
        or "openshift_container_platform" in haystack
        or re.search(r"\bocp\b", haystack)
    ):
        return "openshift"
    if "kubernetes" in haystack or re.search(r"\bk8s\b", haystack):
        return "kubernetes"
    return "unknown"


def _infer_version(*values: str) -> str:
    haystack = " ".join(value.strip() for value in values if value).strip()
    if not haystack:
        return "unknown"
    match = re.search(r"\b(\d+\.\d+)\b", haystack)
    if match:
        return match.group(1)
    return "unknown"


def _pack_label_for_uploaded(product: str, version: str) -> str:
    if product == "openshift" and version != "unknown":
        return f"OpenShift {version} Custom Pack"
    if product == "openshift":
        return "OpenShift Custom Pack"
    return "User Custom Pack"


def _pack_id_for_uploaded(product: str, version: str) -> str:
    product_token = product if product != "unknown" else "custom"
    version_token = version.replace(".", "-") if version != "unknown" else "uploaded"
    return f"{product_token}-{version_token}-custom"


def _support_entry(
    *,
    format_id: str,
    route_label: str,
    source_type: str,
    support_status: SupportStatus,
    capture_strategy: str,
    normalization_strategy: str,
    review_rule: str,
    ocr: IntakeOcrMetadata | None = None,
    accepted_extensions: tuple[str, ...] = (),
    accepted_mime_types: tuple[str, ...] = (),
    notes: tuple[str, ...] = (),
) -> IntakeFormatSupportEntry:
    return IntakeFormatSupportEntry(
        format_id=format_id,
        route_label=route_label,
        source_type=source_type,
        support_status=support_status,
        capture_strategy=capture_strategy,
        normalization_strategy=normalization_strategy,
        review_rule=review_rule,
        ocr=ocr or IntakeOcrMetadata(enabled=False, required=False, runtime="n/a"),
        accepted_extensions=accepted_extensions,
        accepted_mime_types=accepted_mime_types,
        notes=notes,
    )


def build_customer_pack_support_matrix() -> IntakeSupportMatrix:
    return IntakeSupportMatrix(
        matrix_version="customer_pack_format_support_matrix_v1",
        status_legend={
            "supported": "현재 제품 경로에서 업로드 -> capture -> normalize -> playbook 생성까지 live 로 검증된 형식",
            "staged": "제품 경로는 존재하지만 OCR/quality review gate 때문에 보수적으로 취급하는 형식",
            "rejected": "현재 intake 에서 받지 않거나 canonical playbook 경로로 올리지 않는 형식",
        },
        entries=(
            _support_entry(
                format_id="web_html",
                route_label="Web HTML",
                source_type="web",
                support_status="supported",
                capture_strategy="docs_redhat_html_single_v1 / direct_html_fetch_v1",
                normalization_strategy="html_capture_to_canonical_sections_v1",
                review_rule="HTML/Markdown/Text capture가 비어 있으면 reject 하고, 임의 요약으로 대체하지 않는다.",
                accepted_extensions=(".html", ".htm"),
                accepted_mime_types=("text/html", "application/xhtml+xml"),
                notes=("웹 소스는 canonical sections 로 정규화한 뒤 retrieval chunk 로 분리한다.",),
            ),
            _support_entry(
                format_id="pdf_text",
                route_label="Text PDF",
                source_type="pdf",
                support_status="supported",
                capture_strategy="pdf_text_extract_v1",
                normalization_strategy="markitdown_markdown_to_canonical_sections_v1",
                review_rule="텍스트 기반 PDF 는 MarkItDown markdown conversion 을 우선 쓰고, 실패하면 기존 PDF fallback 으로 보강한다.",
                ocr=IntakeOcrMetadata(
                    enabled=True,
                    required=False,
                    runtime="docling -> mdls -> string_scan -> rendered_ocr fallback",
                    fallback_order=("docling", "mdls", "string_scan", "rendered_ocr"),
                    quality_gate="merged-korean / low-quality text detection",
                    review_rule="텍스트가 충분히 복원되지 않으면 manual review 를 거친다.",
                    notes=("scan PDF 가 아니더라도 OCR fallback 이 준비돼 있다.",),
                ),
                accepted_extensions=(".pdf",),
                accepted_mime_types=("application/pdf",),
                notes=("텍스트 PDF 는 MarkItDown markdown conversion 을 우선 사용한다.",),
            ),
            _support_entry(
                format_id="pdf_scan_ocr",
                route_label="Scan PDF with OCR",
                source_type="pdf",
                support_status="staged",
                capture_strategy="pdf_scan_ocr_v1",
                normalization_strategy="docling_ocr_to_canonical_sections_v1",
                review_rule="스캔 PDF 는 OCR runtime 과 quality gate 가 필수이며, OCR 결과가 비어 있거나 품질이 낮으면 review needed 로 보낸다.",
                ocr=IntakeOcrMetadata(
                    enabled=True,
                    required=True,
                    runtime="docling OCR + rendered OCR",
                    fallback_order=("docling_ocr", "rendered_ocr"),
                    quality_gate="no-text / merged-korean detection",
                    review_rule="OCR 결과를 사람이 다시 확인해야 하는 경우가 있다.",
                    notes=("스캔 PDF 는 OCR 없이는 canonical sections 로 못 올린다.",),
                ),
                accepted_extensions=(".pdf",),
                accepted_mime_types=("application/pdf",),
                notes=("스캔 PDF 는 OCR 경로로만 canonical book 으로 승격된다.",),
            ),
            _support_entry(
                format_id="md",
                route_label="Markdown",
                source_type="md",
                support_status="supported",
                capture_strategy="markdown_text_capture_v1",
                normalization_strategy="text_markdown_to_canonical_sections_v1",
                review_rule="heading, code, table 이 깨지지 않았는지 확인하고, 비어 있는 문서면 reject 한다.",
                accepted_extensions=(".md", ".markdown"),
                accepted_mime_types=("text/markdown", "text/plain"),
                notes=("Markdown 은 명시적 heading hierarchy 를 보존한다.",),
            ),
            _support_entry(
                format_id="asciidoc",
                route_label="AsciiDoc",
                source_type="asciidoc",
                support_status="supported",
                capture_strategy="asciidoc_text_capture_v1",
                normalization_strategy="text_asciidoc_to_canonical_sections_v1",
                review_rule="heading, code block, table block 이 정상적으로 보존되는지 확인한다.",
                accepted_extensions=(".adoc", ".asciidoc"),
                accepted_mime_types=("text/asciidoc", "text/plain"),
                notes=("AsciiDoc 은 실행 절차와 코드 블록을 canonical book 에 그대로 남긴다.",),
            ),
            _support_entry(
                format_id="txt",
                route_label="Text",
                source_type="txt",
                support_status="supported",
                capture_strategy="plain_text_capture_v1",
                normalization_strategy="text_plain_to_canonical_sections_v1",
                review_rule="plain text 가 UTF-8 이 아니거나 heading 이 없으면 reject 또는 재업로드가 필요하다.",
                accepted_extensions=(".txt",),
                accepted_mime_types=("text/plain",),
                notes=("plain text 는 numeric heading 도 section anchor 로 승격한다.",),
            ),
            _support_entry(
                format_id="docx",
                route_label="Word",
                source_type="docx",
                support_status="supported",
                capture_strategy="docx_structured_capture_v1",
                normalization_strategy="markitdown_markdown_to_canonical_sections_v1",
                review_rule="MarkItDown markdown 에 heading, table, executable step 이 구조적으로 남았는지 확인한다.",
                accepted_extensions=(".docx",),
                accepted_mime_types=("application/vnd.openxmlformats-officedocument.wordprocessingml.document",),
                notes=("Word 문서는 MarkItDown markdown 을 거쳐 canonical book 으로 옮긴다.",),
            ),
            _support_entry(
                format_id="pptx",
                route_label="PowerPoint",
                source_type="pptx",
                support_status="supported",
                capture_strategy="pptx_slide_capture_v1",
                normalization_strategy="pptx_native_slide_extract_v1",
                review_rule="슬라이드 제목, 본문 순서, bullet depth, table, speaker notes 가 slide-native extract 에서 유지되는지 확인한다.",
                accepted_extensions=(".pptx",),
                accepted_mime_types=("application/vnd.openxmlformats-officedocument.presentationml.presentation",),
                notes=("PowerPoint 는 slide-native extract 로 canonical book rows 를 직접 만든다.",),
            ),
            _support_entry(
                format_id="xlsx",
                route_label="Excel",
                source_type="xlsx",
                support_status="supported",
                capture_strategy="xlsx_sheet_capture_v1",
                normalization_strategy="markitdown_markdown_to_canonical_sections_v1",
                review_rule="MarkItDown markdown 에 sheet/table headings 와 command cells 가 남는지 확인한다.",
                accepted_extensions=(".xlsx",),
                accepted_mime_types=("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",),
                notes=("Excel 은 MarkItDown markdown 을 거쳐 playbook table sections 으로 분해한다.",),
            ),
            _support_entry(
                format_id="hwp",
                route_label="Hancom HWP",
                source_type="hwp",
                support_status="staged",
                capture_strategy="hwp_binary_capture_v1",
                normalization_strategy="unhwp_structured_extract_v1",
                review_rule="unhwp extraction 을 우선 사용하고, embedded scan/bitmap block 은 후속 hybrid OCR lane 으로 넘긴다.",
                accepted_extensions=(".hwp",),
                accepted_mime_types=("application/x-hwp", "application/haansofthwp"),
                notes=(
                    "HWP 는 unhwp 기반 structured extraction 을 우선 사용한다.",
                    "현재 단계에서는 fixture validation 전이므로 staged 로 유지한다.",
                ),
            ),
            _support_entry(
                format_id="hwpx",
                route_label="Hancom HWPX",
                source_type="hwpx",
                support_status="staged",
                capture_strategy="hwpx_zip_capture_v1",
                normalization_strategy="unhwp_structured_extract_v1",
                review_rule="unhwp extraction 을 우선 사용하고, embedded scan/bitmap block 은 후속 hybrid OCR lane 으로 넘긴다.",
                accepted_extensions=(".hwpx",),
                accepted_mime_types=("application/x-hwpx", "application/zip"),
                notes=(
                    "HWPX 는 unhwp 기반 structured extraction 을 우선 사용한다.",
                    "현재 단계에서는 fixture validation 전이므로 staged 로 유지한다.",
                ),
            ),
            _support_entry(
                format_id="image_ocr",
                route_label="Image OCR",
                source_type="image",
                support_status="staged",
                capture_strategy="image_ocr_capture_v1",
                normalization_strategy="image_ocr_to_canonical_sections_v1",
                review_rule="이미지는 OCR 결과의 신뢰도에 따라 manual review 가 필요할 수 있다.",
                ocr=IntakeOcrMetadata(
                    enabled=True,
                    required=True,
                    runtime="docling image OCR",
                    fallback_order=("docling_ocr",),
                    quality_gate="low-confidence image OCR",
                    review_rule="이미지 OCR 은 review-needed 로 내려갈 수 있다.",
                    notes=("이미지 OCR 은 scan PDF 만큼 보수적으로 취급한다.",),
                ),
                accepted_extensions=(".png", ".jpg", ".jpeg", ".webp"),
                accepted_mime_types=("image/png", "image/jpeg", "image/webp"),
                notes=("이미지 OCR 은 화면 캡처/스캔된 안내문을 북으로 승격한다.",),
            ),
            _support_entry(
                format_id="csv",
                route_label="CSV",
                source_type="csv",
                support_status="rejected",
                capture_strategy="not_supported_v1",
                normalization_strategy="not_supported_v1",
                review_rule="현재 customer-pack intake 는 CSV 를 canonical playbook source 로 받지 않는다.",
                notes=("CSV 는 structured table source 로 자동 승격하지 않는다.",),
            ),
            _support_entry(
                format_id="zip",
                route_label="ZIP Archive",
                source_type="zip",
                support_status="rejected",
                capture_strategy="not_supported_v1",
                normalization_strategy="not_supported_v1",
                review_rule="압축 아카이브는 직접 업로드 지원 대상이 아니다.",
                notes=("압축 파일은 먼저 개별 source 로 풀어서 올려야 한다.",),
            ),
            _support_entry(
                format_id="json",
                route_label="JSON",
                source_type="json",
                support_status="rejected",
                capture_strategy="not_supported_v1",
                normalization_strategy="not_supported_v1",
                review_rule="JSON 은 현재 customer-pack intake 지원 포맷이 아니다.",
                notes=("JSON dump 는 사람이 읽을 수 있는 source 로 다시 변환해야 한다.",),
            ),
        ),
    )


def _resolve_text_capture(request: DocSourceRequest) -> tuple[str, str, str, tuple[str, ...]]:
    capture_strategy = {
        "md": "markdown_text_capture_v1",
        "asciidoc": "asciidoc_text_capture_v1",
        "txt": "plain_text_capture_v1",
    }[request.source_type]
    source_label = {
        "md": "Markdown",
        "asciidoc": "AsciiDoc",
        "txt": "Text",
    }[request.source_type]
    return (
        request.uri,
        capture_strategy,
        f"Capture the uploaded {source_label} source and preserve heading hierarchy, ordered steps, and fenced commands before canonical normalization.",
        (
            f"{source_label} sources should preserve explicit heading structure and command blocks where present.",
            "The normalized book view should stay separate from downstream retrieval chunks.",
        ),
    )


def _resolve_binary_capture(request: DocSourceRequest) -> tuple[str, str, str, tuple[str, ...]]:
    capture_strategy = {
        "docx": "docx_structured_capture_v1",
        "pptx": "pptx_slide_capture_v1",
        "xlsx": "xlsx_sheet_capture_v1",
        "hwp": "hwp_binary_capture_v1",
        "hwpx": "hwpx_zip_capture_v1",
        "image": "image_ocr_capture_v1",
    }[request.source_type]
    source_label = {
        "docx": "Word",
        "pptx": "PowerPoint",
        "xlsx": "Excel",
        "hwp": "Hancom HWP",
        "hwpx": "Hancom HWPX",
        "image": "Image",
    }[request.source_type]
    return (
        request.uri,
        capture_strategy,
        f"Capture the uploaded {source_label} source and preserve structural markers, tables, and executable steps before canonical normalization.",
        (
            f"{source_label} sources should preserve headings, tables, and operational commands where possible.",
            "The normalized book view should stay separate from downstream retrieval chunks.",
        ),
    )


def _detect_block_kinds(text: str) -> tuple[str, ...]:
    kinds: list[str] = []
    normalized = text or ""
    if normalized.strip():
        kinds.append("paragraph")
    if "[CODE]" in normalized and "[/CODE]" in normalized:
        kinds.append("code")
    if "[TABLE" in normalized and "[/TABLE]" in normalized:
        kinds.append("table")
    if "[FIGURE" in normalized and "[/FIGURE]" in normalized:
        kinds.append("figure")
    return tuple(kinds)


_TAGGED_BLOCK_END_MARKERS = {
    "CODE": "[/CODE]",
    "TABLE": "[/TABLE]",
    "FIGURE": "[/FIGURE]",
}
_LIST_ITEM_RE = re.compile(r"^(?:[-*]\s+|\d+\.\s+|[A-Za-z]\)\s+)")
_MARKER_ATTR_RE = re.compile(r'([a-z_]+)="((?:[^"\\]|\\.)*)"')


def _document_block_id(section_key: str, block_ordinal: int) -> str:
    return f"{section_key}:block-{block_ordinal:02d}"


def _append_document_block(
    blocks: list[DocumentBlock],
    *,
    section_key: str,
    block_type: str,
    text: str,
    block_ordinal: int,
    source_page_or_slide: str,
    hierarchy_hint: str,
    table_html_or_cells: str = "",
    figure_asset_ref: str = "",
    confidence: float = 0.0,
) -> int:
    normalized = str(text or "").strip()
    if not normalized and not str(figure_asset_ref or "").strip():
        return block_ordinal
    blocks.append(
        DocumentBlock(
            block_id=_document_block_id(section_key, block_ordinal),
            block_type=block_type,  # type: ignore[arg-type]
            text=normalized,
            source_page_or_slide=source_page_or_slide,
            order_key=f"{source_page_or_slide}:{block_ordinal:02d}",
            hierarchy_hint=hierarchy_hint,
            table_html_or_cells=table_html_or_cells,
            figure_asset_ref=str(figure_asset_ref or "").strip(),
            confidence=confidence,
        )
    )
    return block_ordinal + 1


def _parse_marker_attrs(text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for key, value in _MARKER_ATTR_RE.findall(text or ""):
        attrs[key.strip().lower()] = value.replace('\\"', '"').replace("\\\\", "\\").strip()
    return attrs


def _section_document_blocks(
    *,
    section_key: str,
    heading: str,
    section_level: int,
    section_text: str,
    source_page_or_slide: str,
) -> tuple[DocumentBlock, ...]:
    blocks: list[DocumentBlock] = []
    block_ordinal = 1
    block_ordinal = _append_document_block(
        blocks,
        section_key=section_key,
        block_type="heading",
        text=heading,
        block_ordinal=block_ordinal,
        source_page_or_slide=source_page_or_slide,
        hierarchy_hint=f"h{max(section_level, 1)}",
        confidence=0.95,
    )

    buffered_lines: list[str] = []
    buffered_kind = "paragraph"
    active_tag = ""
    active_tag_attrs: dict[str, str] = {}
    active_tag_lines: list[str] = []

    def flush_buffer() -> None:
        nonlocal block_ordinal, buffered_lines, buffered_kind
        if not buffered_lines:
            return
        text = "\n".join(buffered_lines).strip()
        if not text:
            buffered_lines = []
            buffered_kind = "paragraph"
            return
        kind = buffered_kind
        hint = "body"
        confidence = 0.78
        if kind == "list_item":
            hint = "list-depth:1"
            confidence = 0.86
        elif kind == "note":
            hint = "note"
            confidence = 0.82
        block_ordinal = _append_document_block(
            blocks,
            section_key=section_key,
            block_type=kind,
            text=text,
            block_ordinal=block_ordinal,
            source_page_or_slide=source_page_or_slide,
            hierarchy_hint=hint,
            confidence=confidence,
        )
        buffered_lines = []
        buffered_kind = "paragraph"

    for line in str(section_text or "").splitlines():
        stripped = line.strip()
        upper = stripped.upper()
        if active_tag:
            if upper == _TAGGED_BLOCK_END_MARKERS[active_tag]:
                tagged_text = "\n".join(active_tag_lines).strip()
                kind = active_tag.lower()
                figure_asset_ref = ""
                hierarchy_hint = kind
                if kind == "figure":
                    figure_asset_ref = str(active_tag_attrs.get("ref") or "").strip()
                    tagged_text = tagged_text or str(active_tag_attrs.get("alt") or "").strip()
                    hierarchy_hint = str(active_tag_attrs.get("placement_hint") or "figure").strip() or "figure"
                block_ordinal = _append_document_block(
                    blocks,
                    section_key=section_key,
                    block_type=kind,
                    text=tagged_text,
                    block_ordinal=block_ordinal,
                    source_page_or_slide=source_page_or_slide,
                    hierarchy_hint=hierarchy_hint,
                    table_html_or_cells=tagged_text if kind == "table" else "",
                    figure_asset_ref=figure_asset_ref,
                    confidence=0.92 if kind in {"table", "code"} else 0.88,
                )
                active_tag = ""
                active_tag_attrs = {}
                active_tag_lines = []
                continue
            active_tag_lines.append(line)
            continue

        if upper.startswith("[CODE"):
            flush_buffer()
            active_tag = "CODE"
            active_tag_attrs = _parse_marker_attrs(stripped)
            active_tag_lines = []
            continue
        if upper.startswith("[TABLE"):
            flush_buffer()
            active_tag = "TABLE"
            active_tag_attrs = _parse_marker_attrs(stripped)
            active_tag_lines = []
            continue
        if upper.startswith("[FIGURE"):
            flush_buffer()
            active_tag = "FIGURE"
            active_tag_attrs = _parse_marker_attrs(stripped)
            active_tag_lines = []
            continue
        if not stripped:
            flush_buffer()
            continue

        next_kind = "paragraph"
        if stripped.lower().startswith("slide notes"):
            next_kind = "note"
        elif _LIST_ITEM_RE.match(stripped):
            next_kind = "list_item"
        elif buffered_kind == "note" and buffered_lines:
            next_kind = "note"

        if buffered_lines and next_kind != buffered_kind:
            flush_buffer()
        buffered_kind = next_kind
        buffered_lines.append(line)

    flush_buffer()
    if active_tag and active_tag_lines:
        block_ordinal = _append_document_block(
            blocks,
            section_key=section_key,
            block_type="paragraph",
            text="\n".join(active_tag_lines),
            block_ordinal=block_ordinal,
            source_page_or_slide=source_page_or_slide,
            hierarchy_hint="body",
            confidence=0.6,
        )
    return tuple(blocks)


def _document_block_kinds(document_blocks: tuple[DocumentBlock, ...]) -> tuple[str, ...]:
    kinds: list[str] = []
    for block in document_blocks:
        kind = str(block.block_type or "").strip()
        if not kind or kind == "heading" or kind in kinds:
            continue
        kinds.append(kind)
    return tuple(kinds)


def _section_path_label(section_path: tuple[str, ...], heading: str) -> str:
    if section_path:
        return " > ".join(part for part in section_path if part)
    return heading


def _section_key(book_slug: str, anchor: str, ordinal: int) -> str:
    if anchor.strip():
        return f"{book_slug}:{anchor.strip()}"
    return f"{book_slug}:section-{ordinal}"


class CustomerPackPlanner:
    def support_matrix(self) -> IntakeSupportMatrix:
        return build_customer_pack_support_matrix()

    def plan(self, request: DocSourceRequest) -> CanonicalBookDraft:
        title = _infer_title(request)
        slug = _slugify(title)
        inferred_product = _infer_product(request.title, request.uri, title)
        inferred_version = _infer_version(request.title, request.uri, title)
        source_collection = "uploaded"
        pack_id = _pack_id_for_uploaded(inferred_product, inferred_version)
        pack_label = _pack_label_for_uploaded(inferred_product, inferred_version)

        if request.source_type == "web":
            acquisition_uri, capture_strategy = resolve_web_capture_url(request.uri)
            acquisition_step = "Resolve the source URL and prefer an html-single snapshot before parsing."
            notes = (
                "Web sources should preserve original chapter/page mapping where possible.",
                "The normalized book view should stay separate from downstream retrieval chunks.",
            )
        elif request.source_type == "pdf":
            acquisition_uri, capture_strategy = resolve_pdf_capture(request.uri)
            acquisition_step = "Extract text and structural markers from PDF pages before section normalization."
            notes = (
                "PDF sources need a lightweight structure recovery pass before chunk derivation.",
                "Page numbers can remain as auxiliary metadata until section anchors become reliable.",
            )
        elif request.source_type in {"md", "asciidoc", "txt"}:
            acquisition_uri, capture_strategy, acquisition_step, notes = _resolve_text_capture(request)
        else:
            acquisition_uri, capture_strategy, acquisition_step, notes = _resolve_binary_capture(request)

        return CanonicalBookDraft(
            book_slug=slug,
            title=title,
            source_type=request.source_type,
            source_uri=request.uri,
            source_collection=source_collection,
            pack_id=pack_id,
            pack_label=pack_label,
            inferred_product=inferred_product,
            inferred_version=inferred_version,
            acquisition_uri=acquisition_uri,
            capture_strategy=capture_strategy,
            acquisition_step=acquisition_step,
            normalization_step="Build canonical sections that preserve headings, anchors, code blocks, and tables.",
            derivation_step="Derive a source-view document first, then retrieval chunks and embeddings as downstream artifacts.",
            notes=notes,
        )

    def build_canonical_book(
        self,
        rows: list[dict[str, object]],
        *,
        request: DocSourceRequest | None = None,
        figure_assets: list[dict[str, object]] | tuple[FigureAsset, ...] | None = None,
    ) -> CanonicalBook:
        if not rows:
            raise ValueError("rows must not be empty")

        first = rows[0]
        request = request or DocSourceRequest(
            source_type="web",
            uri=str(first.get("source_url") or ""),
            title=str(first.get("book_title") or first.get("book_slug") or ""),
            language_hint="ko",
        )
        draft = self.plan(request)
        book_slug = str(first.get("book_slug") or draft.book_slug)
        title = str(first.get("book_title") or draft.title)
        source_uri = str(first.get("source_url") or request.uri)

        sections: list[CanonicalSection] = []
        for ordinal, row in enumerate(rows, start=1):
            heading = str(row.get("heading") or "").strip() or f"Section {ordinal}"
            anchor = str(row.get("anchor") or "").strip()
            section_key = _section_key(book_slug, anchor, ordinal)
            section_path = tuple(
                str(item).strip()
                for item in (row.get("section_path") or [])
                if str(item).strip()
            )
            section_text = str(row.get("text") or "").strip()
            source_page_or_slide = str(
                row.get("source_page_or_slide")
                or row.get("source_container_ref")
                or f"section:{ordinal}"
            ).strip()
            document_blocks = _section_document_blocks(
                section_key=section_key,
                heading=heading,
                section_level=int(row.get("section_level") or 0),
                section_text=section_text,
                source_page_or_slide=source_page_or_slide,
            )
            sections.append(
                CanonicalSection(
                    ordinal=ordinal,
                    section_key=section_key,
                    heading=heading,
                    section_level=int(row.get("section_level") or 0),
                    section_path=section_path,
                    section_path_label=_section_path_label(section_path, heading),
                    anchor=anchor,
                    viewer_path=str(row.get("viewer_path") or "").strip(),
                    source_url=str(row.get("source_url") or source_uri).strip(),
                    text=section_text,
                    block_kinds=_document_block_kinds(document_blocks) or _detect_block_kinds(section_text),
                    document_blocks=document_blocks,
                )
            )

        normalized_figure_assets: list[FigureAsset] = []
        for payload in figure_assets or []:
            if isinstance(payload, FigureAsset):
                normalized_figure_assets.append(payload)
                continue
            if not isinstance(payload, dict):
                continue
            asset_ref = str(payload.get("asset_ref") or payload.get("asset_name") or "").strip()
            if not asset_ref:
                continue
            normalized_figure_assets.append(
                FigureAsset(
                    asset_ref=asset_ref,
                    content_type=str(payload.get("content_type") or "application/octet-stream").strip()
                    or "application/octet-stream",
                    source_page_or_slide=str(payload.get("source_page_or_slide") or "").strip(),
                    placement_hint=str(payload.get("placement_hint") or "").strip(),
                    caption=str(payload.get("caption") or "").strip(),
                    alt=str(payload.get("alt") or "").strip(),
                    figure_type=str(payload.get("figure_type") or "image").strip() or "image",
                    asset_name=str(payload.get("asset_name") or asset_ref).strip() or asset_ref,
                    width_px=int(payload.get("width_px") or 0),
                    height_px=int(payload.get("height_px") or 0),
                    nearby_text=str(payload.get("nearby_text") or "").strip(),
                    asset_url=str(payload.get("asset_url") or "").strip(),
                )
            )

        return CanonicalBook(
            canonical_model=draft.canonical_model,
            book_slug=book_slug,
            title=title,
            source_type=request.source_type,
            source_uri=source_uri,
            source_collection=draft.source_collection,
            pack_id=draft.pack_id,
            pack_label=draft.pack_label,
            inferred_product=draft.inferred_product,
            inferred_version=draft.inferred_version,
            language_hint=request.language_hint,
            source_view_strategy="normalized_sections_v1",
            retrieval_derivation=draft.retrieval_derivation,
            sections=tuple(sections),
            figure_assets=tuple(normalized_figure_assets),
            notes=draft.notes,
        )


__all__ = ["CustomerPackPlanner"]
