---
status: active
doc_type: integration_contract
artifact_id: corpus_truth_contract
owner: worker-contracts-gates
last_updated: 2026-04-21
---

# Corpus Truth Contract

## Goal

Phase-1 corpus truth baseline을 `shared truth` 기준으로 잠근다. Library, runtime, corpus는 같은 truth bundle에서만 파생된다.

## Canonical Truth Bundle

- `structured_book`
- `relation_assets`
- `figure_asset_catalog`
- `runtime_manifest`
- `citation_map`

`markdown` 또는 `html` 단독 파일은 truth owner가 아니다.

## Acceptance Criteria

| Item | Pass / Fail | Measurement | Evidence | Current Gap |
| --- | --- | --- | --- | --- |
| Canonical owner is singular | Pass when `canonical_truth_owner=structured_book` and `canonical_truth_owner_count_per_book=1` | Read runtime truth freeze metrics | `reports/build_logs/runtime_truth_freeze_report.json` | None in snapshot evidence |
| Runtime and source family stay aligned | Pass when `runtime_count`, `active_slug_count`, `source_slug_count`, `source_first_slug_count` are equal | Compare freeze report counts | `reports/build_logs/runtime_truth_freeze_report.json` | None in snapshot evidence |
| Anchor landing remains stable | Pass when `anchor_id_stability_sample_rate=1.0` and unresolved/mismatch counts are `0` | Read anchor metrics | `reports/build_logs/runtime_truth_freeze_report.json`, `reports/build_logs/citation_grounding_gate_report.json` | None in snapshot evidence |
| Corpus materialization is non-empty | Pass when `playbook_count > 0`, `chunk_count > 0`, and `qdrant_upserted_count == chunk_count` | Read rebuild summary | `reports/build_logs/active_gold_corpus_rebuild_report.json` | None in snapshot evidence |
| Citation landing is grounded | Pass when citation/viewer rates stay `1.0` and broken/mismatch counts stay `0` | Read citation gate metrics | `reports/build_logs/citation_grounding_gate_report.json` | None in snapshot evidence |

## Current Snapshot

- `canonical_truth_owner`: `structured_book`
- `runtime_count`: `29`
- `anchor_id_stability_sample_rate`: `1.0`
- `citation_anchor_resolution_rate`: `1.0`
- `viewer_jump_success_rate`: `1.0`
- `chunk_count`: `27907`
- `qdrant_upserted_count`: `27907`

## Evidence Paths

- `reports/build_logs/runtime_truth_freeze_report.json`
- `reports/build_logs/citation_grounding_gate_report.json`
- `reports/build_logs/active_gold_corpus_rebuild_report.json`

## Current Gap

- `runtime_truth_freeze_report.json` stores evidence paths rooted at `C:\Users\soulu\cywell\ocp-play-studio\ocp-play-studio\...`, not this workspace root. Treat those path fields as frozen evidence payloads until runtime truth outputs are rebound to repo-relative or workspace-local paths.
