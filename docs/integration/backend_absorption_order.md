---
status: active
doc_type: integration_contract
artifact_id: backend_absorption_order
owner: worker-contracts-gates
last_updated: 2026-04-21
---

# Backend Absorption Order

## Goal

Phase-1 backend bootstrap이 truth-bearing artifacts를 어떤 순서로 흡수해야 하는지 고정한다. Release packet이나 viewer decoration은 truth absorption보다 뒤에 온다.

## Ordered Absorption Contract

| Order | Backend absorption target | Measurement | Evidence | Current Gap |
| --- | --- | --- | --- | --- |
| 1 | Bootstrap-stable roots only: `manifests/`, `data/`, `data/bronze/`, `artifacts/` | Confirm root bootstrap contract exists | `src/play_book_studio/config/settings_paths.py` | None |
| 2 | Source authority manifests: `source_manifest_path`, `source_catalog_path`, `corpus_working_manifest_path` | Confirm manifest resolution happens before downstream reads | `src/play_book_studio/config/settings_paths.py`, `src/play_book_studio/app/presenters.py` | None |
| 3 | Corpus inputs: `normalized_docs_path`, `chunks_path`, `bm25_corpus_path` | Confirm corpus readers prefer shared truth candidates, not viewer-only artifacts | `src/play_book_studio/config/settings_paths.py` | None |
| 4 | Reader artifacts: `playbook_documents_path`, `playbook_books_dir` | Confirm reader surface derives from same settings contract | `src/play_book_studio/config/settings_paths.py` | None |
| 5 | Runtime truth and source meta | Confirm source meta merges runtime truth with manifest provenance | `src/play_book_studio/app/presenters.py`, `src/play_book_studio/app/server_routes_viewer.py`, `src/play_book_studio/runtime_truth_freeze.py` | None |
| 6 | Relations refresh before active switch | Pass when relation refresh precedes active runtime activation | `RUNTIME_ARCHITECTURE_CONTRACT.md`, `reports/build_logs/ocp420_one_click_runtime_report.json` | Current one-click evidence still shows `activate_full_rebuild_runtime` before `generate_full_rebuild_wiki_relations` |
| 7 | Smoke and package outputs last | Pass when smoke/reporting trails materialization and activation | `reports/build_logs/ocp420_one_click_runtime_report.json`, `reports/build_logs/ocp_operator_package_packet.md` | None for evidence order, but relation refresh debt remains |

## Current Evidence Order

`reports/build_logs/ocp420_one_click_runtime_report.json` currently records this backend execution order:

1. `build_manifest`
2. `materialize_full_rebuild_books`
3. `activate_full_rebuild_runtime`
4. `generate_full_rebuild_wiki_relations`

## Phase-1 Decision

- Phase-1 gate tracks the current backend order as evidence.
- Phase-1 does not declare relation refresh debt solved.
- Any later promotion beyond phase-1 should realign step `4` ahead of step `3`, because active runtime contract requires `relation refresh -> active switch`, not the reverse.
