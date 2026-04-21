---
status: active
doc_type: integration_program
artifact_id: pbs_ocp_execution_program
owner: execution-program-lane-6
tracked: true
last_updated: 2026-04-21
---

# PBS + OCP Ops Execution Program

## Purpose

This document tracks the long-running execution program for taking PBS + OCP Ops to completion inside the current PBS architecture. It is a living program record, not a product redefinition note.

## Completion Target

- Keep OCP operator delivery inside PBS architecture.
- Keep the landing shell and strengthen branch entry rather than replacing the shell.
- Keep Playbook as the default narrative branch and Studio Ops as the advanced operational branch.
- Keep Playbot and OCP Ops bot separate while building a first-class cross-handoff contract.
- Preserve source-first truth handling for official documents.
- Keep corpus, viewer, and chat outputs grounded to the same evidence bundle.
- Keep document truth under PBS and live operational truth under Ops while sharing one product shell.
- Produce release and readiness evidence that can be replayed locally.

## Program Rules

- One milestone equals one execution packet.
- No packet closes without validation evidence.
- No lane writes outside the declared packet scope.
- No surface renames, doctrine resets, or temporary delivery forks.
- If official source, runtime, and citation evidence diverge, the packet stays open until the source of truth is repaired.
- Shared endpoint settings should converge on one canonical name when PBS and Ops truly hit the same service.
- Deprecated `.env` keys should be commented out with the reason they stopped being authoritative, not silently deleted.

## Lane Model

| Lane | Responsibility | Write Scope | Closeout Role | Exit Condition |
| --- | --- | --- | --- | --- |
| main | Owns the packet verdict, ref stamp, and final merge decision | Program doc, harness records, packet outputs | Final integration and closeout | All packet gates pass and evidence is complete |
| lane 1 `IA / routes` | Surface map, shell model, route implications | Read-only analysis and route findings | Prevents shell/route drift | Shared shell and branch model stay coherent |
| lane 2 `ownership / pipeline` | Truth ownership, pipeline seams, backend sequence | Read-only analysis and seam findings | Prevents truth contamination | Document and ops ownership stay separate and explicit |
| lane 3 `handoff / audit` | Bot boundaries, handoff schema, replayability | Read-only analysis and handoff findings | Prevents silent bot swaps and trace gaps | Cross-handoff is explicit and auditable |
| lane 4 `architecture doc` | Product architecture and decision lock | `docs/integration/pbs_ocp_product_architecture.md` | Architecture documentation | Architecture contract is tracked and consistent |
| lane 5 `surface + UX doc` | Landing, header, and handoff blueprint | `docs/integration/pbs_ocp_surface_and_handoff_blueprint.md` | Surface/handoff documentation | Branching and bot coexistence are tracked and consistent |
| lane 6 `execution program` | Packet model, harness discipline, validation gates | This execution-program doc | Sustained program continuity | No packet runs without gates and evidence |

This program uses a six-person special squad. Main integrates the verdict while the six specialist lanes continuously pressure-test the same direction from different angles.

## Packet Breakdown

| Packet | Objective | Primary Lane | Validation Gate | Evidence Target | Current Gap |
| --- | --- | --- | --- | --- | --- |
| Packet 1 | Lock shell direction, branch labels, and truth ownership | main + lanes 1-3 | Frontmatter sanity, path existence, and scope lock | Architecture docs + harness manifest | In progress in this workspace |
| Packet 2 | Formalize landing/header branching and route contract | lanes 1, 4, 5 | Route contract review + frontend route smoke | Route map, header model, route evidence | No dedicated route contract test yet |
| Packet 3 | Formalize handoff schema, bot separation, and audit correlation | lanes 3, 5 | Payload schema review + replayability check | Handoff schema, audit correlation plan | No first-class handoff API yet |
| Packet 4 | Freeze ownership map, backend seam sequence, and env convergence rules | lane 2 + main | Focused backend/bootstrap subset passes and env alias behavior is documented | Ownership map, backend evidence, env contract notes, focused pytest subset | Shared context contract not yet coded |
| Packet 5 | Harden runtime, viewer, and ops surface interoperability | main + lanes 1-5 | UI build/test, route smoke, viewer/citation subset, compose health | UI logs, pytest evidence, compose health | Full integration replay not yet automated |
| Packet 6 | Assemble release/readiness packet and final completion freeze | main + reviewer-style check across all lanes | All prior packet gates green and evidence linked | Release/readiness packet, final report, ref-stamped closeout | Pending program completion |

## Validation Gates Per Packet

| Packet | Pass / Fail | Measurement | Command | Current Gap |
| --- | --- | --- | --- | --- |
| Packet 1 | Pass when the docs exist and the harness scope is locked | Check file existence and packet metadata | `powershell -NoProfile -Command "@('docs/integration/pbs_ocp_product_architecture.md','docs/integration/pbs_ocp_surface_and_handoff_blueprint.md','docs/integration/pbs_ocp_execution_program.md') | ForEach-Object { if (-not (Test-Path $_)) { throw \\\"Missing $_\\\" } }"` | Main index doc still pending |
| Packet 2 | Pass when shell/route branching stays coherent | Review route contract and run frontend route tests | `npm --prefix presentation-ui exec vitest run src/app/handoff.test.ts src/app/routes.test.ts` | A dedicated landing/header contract test does not exist yet |
| Packet 3 | Pass when the handoff payload contract is explicit and replay-safe | Review schema fields and verify correlation-id coverage | `powershell -NoProfile -Command "Get-Content docs/integration/pbs_ocp_surface_and_handoff_blueprint.md"` | No code-level handoff API yet |
| Packet 4 | Pass when the selected backend subset returns exit code `0` and env convergence rules are explicit | Focused bootstrap regression subset plus env contract review | `.\\.venv\\Scripts\\python.exe -m pytest tests/test_app_server.py tests/test_customer_pack_direct_viewer_route.py tests/test_customer_pack_read_boundary.py -q` and doc/config review for env aliases | Current subset has not been rerun under this program |
| Packet 5 | Pass when UI, viewer/citation, and compose health are green together | Frontend build/test, viewer subset, and compose health validation | `npm --prefix presentation-ui run build`, `npm --prefix presentation-ui run test`, `.\\.venv\\Scripts\\python.exe -m pytest tests/test_app_viewers_routes.py -q -k "canonicalize_viewer_path or viewer_document_route_supports_entity_and_figure_paths or viewer_document_route_falls_back_to_normalized_sections_for_known_book or viewer_path_local_raw_html_fallback"`, `docker compose ps` | Full integration replay not yet automated |
| Packet 6 | Pass when every prior packet is green and the closeout report is complete | Full program closeout review | `Get-Content reports/execution_harness/pbs_ocp_integrated_service_program_20260421/main/final_report.json` | Final report path not yet populated for this run |

## Repo-Local Commands

Use these commands from the repository root unless the command says otherwise.

```powershell
git diff --check
docker compose ps
```

```powershell
npm --prefix presentation-ui exec vitest run src/app/handoff.test.ts src/app/routes.test.ts
npm --prefix presentation-ui run test
npm --prefix presentation-ui run build
```

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_app_server.py tests/test_customer_pack_direct_viewer_route.py tests/test_customer_pack_read_boundary.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_app_viewers_routes.py -q -k "canonicalize_viewer_path or viewer_document_route_supports_entity_and_figure_paths or viewer_document_route_falls_back_to_normalized_sections_for_known_book or viewer_path_local_raw_html_fallback"
```

```powershell
powershell -NoProfile -Command "@('docs/integration/pbs_ocp_product_architecture.md','docs/integration/pbs_ocp_surface_and_handoff_blueprint.md','docs/integration/pbs_ocp_execution_program.md','docs/integration/pbs_ocp_integrated_service_index.md') | ForEach-Object { if (-not (Test-Path $_)) { throw \\\"Missing $_\\\" } }"
```

## Harness Discipline

- Lock `task_id`, `lane_id`, `cwd`, `write_scope`, `validation_commands`, and `git_ref_snapshot` before editing.
- Create or update `reports/execution_harness/<task_id>/<lane_id>/manifest.json`, `worklog.md`, and `final_report.json` for long-running work.
- Keep `validation_commands` stable for the packet unless a real validation gap forces a controlled update.
- Record the actual command output, not a paraphrase, when validation is the evidence source.
- Do not close a packet if the manifest, worklog, or final report is missing or stale.
- Do not use viewer or release evidence to mask a missing corpus, citation, or runtime gate.
- When `.env` keys are superseded by canonical names, leave the old keys commented with a reason and the replacement key instead of deleting them.

## Exit Criteria

- All six packets are complete and their gates are green.
- The release and readiness packet points to the same truth bundle as the runtime and viewer outputs.
- No unresolved current gap remains except explicitly documented residual risk.
- The final report contains the ref snapshot, commands run, artifacts produced, and the closeout verdict.
- The program can be replayed locally with repo-local commands only.
- The handoff between Playbot and OCP Ops bot is explicit in logs, labels, and payload contracts even if the final API arrives later.

## Risk Register

| Risk | Trigger | Mitigation | Owner | Evidence |
| --- | --- | --- | --- | --- |
| Official source drift | Vendor docs change or a source family is rebound | Re-lock packet 1 and revalidate packet 2-3 | explorer + reviewer | Updated source manifest and validation output |
| Citation mismatch | A viewer jump or anchor resolves to the wrong section | Hold packet 3 open until citation and anchor gates pass | reviewer | Citation gate report and route smoke |
| Runtime regression | A change breaks runtime activation or relation refresh order | Keep packet 4 tied to focused smoke and route checks | worker | Build logs and runtime smoke output |
| UI drift | Frontend build passes but route behavior changes | Require route tests plus build and test together | lanes 1 and 5 | UI command output and route smoke |
| Evidence path drift | Reports point to stale external paths or wrong roots | Rebind evidence to repo-local paths before closeout | main | Final report and path audit |
| Lane contamination | A lane edits files outside its scope | Reset packet scope and continue in the correct lane | main | Worklog and diff review |
| Identity drift | Labels across PBS, Playbot, Studio Ops, and ops chat diverge | Lock labels in the surface blueprint and verify them in implementation packets | lanes 1, 3, and 5 | Surface blueprint and UI evidence |
| Cross-store trace gap | PBS server sessions and ops local storage cannot be correlated | Require a shared `correlation_id` in the handoff contract | lane 3 + main | Handoff schema and audit evidence |

## Closeout Evidence Expectations

- The closeout packet names the packet number, lane, and current verdict.
- The closeout packet includes the command string used for each validation gate.
- The closeout packet includes artifact paths for manifest, worklog, final report, and any generated evidence.
- The closeout packet states the ref stamp, including `head_ref`, `head_sha`, `upstream_ref`, `upstream_sha`, and `origin_main_sha`.
- The closeout packet names any remaining gap explicitly instead of hiding it.
- The closeout packet avoids unsupported claims about readiness, completion, or verification.

## Program Verdict

This program is complete only when packet 6 can be closed with green evidence from packets 1 through 5, repo-local commands, and a ref-stamped final report.
