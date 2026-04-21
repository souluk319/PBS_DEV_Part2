---
status: active
doc_type: integration_gate
artifact_id: phase1_validation_bootstrap_gate
owner: worker-contracts-gates
last_updated: 2026-04-21
---

# Phase-1 Validation Bootstrap Gate

## Goal

현재 저장소에서 재현 가능한 최소 backend/bootstrap gate를 고정한다. 이 gate는 `docs/contracts/gates` lane에서 관리하는 phase-1 baseline이며, 전체 runtime promotion gate를 대체하지 않는다.

## Gate Scope

- tracked integration docs exist and stay readable
- corpus truth evidence stays present and non-empty
- citation grounding evidence stays green
- backend bootstrap pytest subset stays green

## Pass / Fail Matrix

| Item | Pass / Fail | Measurement | Evidence | Current Gap |
| --- | --- | --- | --- | --- |
| Integration artifacts are tracked | Pass when all three docs exist | File existence check | `docs/integration/*.md` | None |
| Corpus truth evidence is present | Pass when runtime truth, citation grounding, and corpus rebuild reports exist and remain non-empty | JSON existence + key/value sanity | `reports/build_logs/runtime_truth_freeze_report.json`, `reports/build_logs/citation_grounding_gate_report.json`, `reports/build_logs/active_gold_corpus_rebuild_report.json` | None |
| Runtime truth snapshot is green | Pass when runtime truth report status is `ok` and rebuild/smoke exit codes are `0` | Read JSON keys | `reports/build_logs/runtime_truth_freeze_report.json` | Path fields remain external-root evidence, not local-root paths |
| Bootstrap backend subset is green | Pass when the selected pytest subset returns exit code `0` | Run focused pytest command | `tests/test_app_server.py`, `tests/test_customer_pack_direct_viewer_route.py`, `tests/test_customer_pack_read_boundary.py`, selected tests from `tests/test_app_viewers_routes.py` | None on selected subset |
| Full viewer route suite is not yet phase-1 ready | Fail outside this gate today | Broad suite currently fails on fixture drift and truth-bucket drift | `tests/test_app_viewers_routes.py` | `monitoring.md` fixture missing under `data/wiki_runtime_books/full_rebuild/`; figure source-meta expectation still drifts between `official_candidate_runtime` and `official_gold_playbook_runtime` |

## Phase-1 Command

```powershell
python -m pytest tests/test_app_server.py tests/test_customer_pack_direct_viewer_route.py tests/test_customer_pack_read_boundary.py tests/test_app_viewers_routes.py -q -k "canonicalize_viewer_path or viewer_document_route_supports_entity_and_figure_paths or viewer_document_route_falls_back_to_normalized_sections_for_known_book or viewer_path_local_raw_html_fallback"
```

## Evidence Snapshot

- `runtime_truth_freeze_report.json`: `status=ok`, `one_click_rebuild_exit_code=0`, `post_switch_smoke_exit_code=0`
- `citation_grounding_gate_report.json`: `citation_anchor_resolution_rate=1.0`, `viewer_jump_success_rate=1.0`
- `active_gold_corpus_rebuild_report.json`: `playbook_count=29`, `chunk_count=27907`

## Exit Rule

- Phase-1 is green only when docs/evidence sanity and the selected bootstrap pytest subset are both green.
- Promotion to a broader gate requires fixing the known viewer-route drifts, not documenting around them.
