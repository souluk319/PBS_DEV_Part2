---
status: active
doc_type: architecture_contract
audience:
  - codex
  - engineer
precedence: 3
supersedes:
  - P0_ARCHITECTURE_FREEZE_ADDENDUM.md
  - PARSED_ARTIFACT_CONTRACT.md
  - PIPELINE_PLAIN_GUIDE.md
last_updated: 2026-04-18
---

# RUNTIME ARCHITECTURE CONTRACT

## Purpose

이 문서는 제품의 기술적 불변조건을 고정한다.
Codex 는 runtime, corpus, viewer, parsing 작업 시 이 문서를 기준으로 구현한다.

## Renewal Execution Frame

현재 작업은 PBS architecture 위에서 `renewal delivery` 를 수행하는 것이다.

기본 규칙은 아래다.

- `customer order -> shared source -> structured runtime -> library/corpus/workspace outputs`
- 주문 수행을 위해 `order-only parser`, `order-only corpus`, `order-only viewer` 를 따로 만들지 않는다.
- `OCP operator package` 는 기존 PBS runtime 의 `derived package output` 으로 만든다.

## Locked System Model

현재 시스템은 아래 다섯 층으로 본다.

1. `Source Intake`
   - official repo source such as AsciiDoc
   - official published HTML benchmark / fallback
   - official published PDF benchmark / fallback
   - source assets such as images, figures, diagrams
   - customer/private documents
2. `Parse And Normalize`
   - parsed artifact
   - source lineage
   - block recovery
3. `Structured Runtime Core`
   - structured book
   - relation assets
   - figure asset catalog
   - runtime manifest
   - citation map
4. `Derived Products`
   - Playbook Library render assets
   - Playbook Corpus retrieval assets
   - evaluation assets
   - operator package deliverables
5. `Product Surfaces`
   - Playbook Library
   - Wiki Runtime Viewer
   - Chat Workspace

## Canonical Truth

제품의 진실 소스는 `단일 markdown 파일`이 아니다.

canonical truth 는 아래 묶음이다.

- `structured book`
- `relation assets`
- `figure asset catalog`
- `runtime manifest`
- `citation map`

`markdown` 과 `html` 은 generated artifact 일 수 있지만, 단독 truth owner 로 취급하지 않는다.

## Official Source Priority Contract

공식 문서 lane 의 raw truth 우선순위는 아래로 고정한다.

1. `official repository source such as AsciiDoc`
2. `official rendered HTML for anchor verification, section parity check, and fallback`
3. `official rendered PDF for reader verification and fallback`

즉 active official runtime 은 `repo/AsciiDoc first` 이어야 하며, published HTML 이 main truth path 가 되면 안 된다.
`published HTML/PDF` fallback 은 `repo source unavailable or parse failed` 일 때만 후보가 되며, 명시적 사용자 승인 전에는 자동 실행하지 않는다.

Red Hat 의 `multi-page / single-page / PDF` surface 는 parsing 우선순위의 진실 소스가 아니라 아래 세 용도다.

- `reader benchmark`
- `verification target`
- `fallback source when repo path is unavailable or incomplete`

공식 source lane 에서 영어 본문이 발견되면 기본 remediation 은 아래 순서다.

1. `translation lane 연결`
2. `translated_ko_draft 생성`
3. `reader/chat verification`
4. `final Playbook publish`

즉 영어 본문은 삭제 기본값이 아니라 `번역 완료 대상` 이다.

## Shared Source Rule

Playbook Library 와 Playbook Corpus 는 서로 다른 raw truth 를 가지면 안 된다.

정답 구조는 아래다.

`shared raw sources -> parsed artifact -> structured book/core -> library + corpus`

즉:

- 사람용 library 와 챗봇용 corpus 는 같은 parsed/structured 기준선에서 파생된다.
- 둘 중 하나가 다른 원천에서 따로 자라면 citation mismatch 가 생기므로 금지한다.
- viewer fidelity 와 chatbot retrieval 은 같은 shared truth 에서 동시에 좋아져야 하며, 한쪽만 좋아지는 fork 를 허용하지 않는다.
- 번역 완료도 같은 shared truth 위에서 수행해야 하며, viewer 용 번역본과 corpus 용 번역본이 따로 갈라지면 안 된다.

## Order Execution Rule

고객 주문용 package 도 같은 shared truth 에서 파생한다.

- order package 는 canonical truth 의 별도 대체물이 아니다.
- order-specific selection, sequencing, packaging 은 허용되지만 raw truth fork 는 금지한다.
- release packet 이나 delivery zip 이 canonical runtime 을 대체하면 안 된다.

## Source Lanes

허용하는 source lane 은 아래다.

- `vendor_official_source`
- `reviewed_translation`
- `verified_operational_evidence`
- `playbook_synthesis`
- `customer_source_first_pack`

각 산출물은 최소 `source_lane`, `source_ref`, `source_fingerprint`, `updated_at` 를 잃지 않는다.

### Runtime Alias Mapping

현재 runtime 이 완전히 canonical lane 값으로 이행되기 전까지 아래 alias 를 허용한다.

- `official_ko` -> `vendor_official_source`
- `applied_playbook` -> `playbook_synthesis`

새 코드와 새 계약 문서는 canonical lane 을 우선하고, alias 는 migration compatibility 로만 본다.

## Data Ladder

기본 상태 사다리는 아래다.

`bronze_raw -> bronze_parsed -> silver_structured -> gold_candidate -> wiki_runtime -> active_runtime -> archived`

customer/private lane 은 아래 확장 경로를 가진다.

`customer_source -> bronze_parsed -> silver_structured -> pack_candidate -> pack_runtime -> approved_pack_runtime`

Bronze / Silver / Gold 는 `reader-grade minimum` 을 통과한 산출물 안에서의 품질 단계다.

- structure 붕괴
- 절차 붕괴
- code/table/figure block collapse

와 같은 failure output 은 등급 부여 대상이 아니라 `blocked artifact` 로 본다.

단, `blocked artifact` 판정은 폐기를 뜻하지 않는다.

- official lane 에서 영어 본문 때문에 blocked 가 걸린 경우 기본 다음 단계는 `translation completion`
- 제품 목표는 삭제가 아니라 `최종 한국어 Playbook 완성`

## Parsed Artifact Minimum

모든 parsed artifact 는 최소 아래 필드를 가진다.

- `parsed_artifact_id`
- `source_ref`
- `source_type`
- `source_lane`
- `source_fingerprint`
- `parser_route`
- `parser_backend`
- `parser_version`
- `ocr_used`
- `extraction_confidence`
- `updated_at`

복원해야 하는 최소 블록 타입은 아래다.

- `heading`
- `paragraph`
- `code`
- `table`
- `figure`
- `xref`
- `admonition`
- `procedure_step` when applicable

## Figure And Bilingual Contract

- figure 가 있는 문서는 `figure asset + caption + anchor trace` 를 유지한다.
- OCR 은 `text recovery` 를 위한 보조 수단이지, figure preservation 의 대체물이 아니다.
- 번역이 존재할 경우 `source_text` 와 `ko_text` 를 함께 유지한다.
- 명령어, 리소스명, error string, code 는 source fidelity 를 잃지 않는다.

## Corpus Contract

Playbook Corpus 는 아래 묶음이다.

- retrieval chunks
- sparse/vector index inputs
- citation context
- retrieval metadata

모든 chunk 는 최소 아래를 가진다.

- `chunk_id`
- `doc_id`
- `section_id`
- `block_id`
- `anchor_id`
- `source_lane`
- `truth_tier`
- `version or runtime id`

chunk 는 사람이 읽는 문서에서 분리되어 저장될 수 있지만, 항상 library anchor 로 되돌아갈 수 있어야 한다.

## Corpus Quality Gate

Playbook Corpus 는 아래 gate 를 통과할 때만 `active runtime quality` 로 본다.

1. `book family retrieval`
   - retrieval regression set 에서 expected playbook family hit 를 유지한다.
2. `landing precision`
   - retrieval 결과는 expected book 뿐 아니라 expected anchor / section landing 도 함께 맞아야 한다.
3. `context coverage`
   - 최소 `ops`, `learn`, `follow-up`, `ambiguous` query set 을 회귀군에 포함한다.
4. `warning cleanliness`
   - outside-corpus, relation-aware miss, similar-document risk 를 보고서에 남긴다.
5. `shared truth discipline`
   - gate 는 library 와 다른 raw truth 가 아니라 active corpus/runtime 기준선으로만 측정한다.

즉 `book slug hit 만 맞는 평가` 는 corpus quality gate 로 충분하지 않다.
active gate 는 `retrieval family + anchor landing + context query coverage` 를 함께 본다.

## Library Contract

Playbook Library 는 사용자가 보는 최종 문서 surface 다.

- 본문은 `HTML viewer` 를 기준으로 한다.
- library 는 relation, figure, anchor jump, bilingual presentation 을 지원해야 한다.
- overlay 는 본문을 점유하지 않는 보조 레이어로 유지한다.

### Playbook Publish Rule

Playbook surface 에 노출되는 문서는 아래를 만족해야 한다.

1. `reader-grade minimum`
   - 원문 절차, 단계, 코드, 표, 그림, 단락 경계가 구조적으로 무너지지 않아야 한다.
2. `chat-grade minimum`
   - 같은 shared truth 에서 corpus, citation landing, follow-up interaction 이 동작해야 한다.

동일 source family 에서 여러 파생 산출물을 만들 수는 있지만, default release/runtime surface 는 `선택된 최종 Playbook` 을 우선한다.

- 나머지 family 는 `candidate artifact` 또는 `internal variant` 로 둘 수 있다.
- winner selection 이 없는 multi-publish 를 final surface 기본값으로 두지 않는다.
- 영어 본문만 남은 source family 는 final surface 에 억지 publish 하지 않고, 번역 완료 후 최종 Playbook 으로 승격한다.

## One-Click Runtime Contract

one-click runtime 은 아래 순서를 한 묶음으로 수행해야 한다.

1. `source rebuild`
2. `parse / normalize`
3. `runtime materialization`
4. `relation refresh`
5. `active switch`
6. `smoke validation`

`relation refresh` 는 `active switch` 뒤로 밀리면 안 된다.
smoke validation 은 post-switch 상태를 검증해야 한다.

## Stop Conditions

아래는 architecture 위반이다.

1. library 와 corpus 가 서로 다른 raw truth 를 쓰는 경우
2. markdown 하나를 canonical truth 인 것처럼 취급하는 경우
3. relation graph 없이 viewer 만 남기는 경우
4. figure/diagram 을 text-only fallback 으로 대체하는 경우
5. citation 이 문서 루트로만 가고 정확한 anchor landing 을 잃는 경우
6. customer/private pack 이 boundary label 없이 official output 에 섞이는 경우
