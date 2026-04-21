---
status: active
doc_type: integration_entrypoint
artifact_id: pbs_ocp_integrated_service_index
owner: main
last_updated: 2026-04-21
---

# PBS + OCP Integrated Service Index

## Goal

Tie the PBS + OCP direction into one tracked entrypoint so future packets can start from a stable, repo-local contract instead of re-deriving the product strategy each time.

## Locked Direction

- Parent product stays `PlayBook Studio`.
- Customer-facing edition can read as `PlayBook Studio for OpenShift`.
- Landing page stays and becomes the shared shell.
- Header branching becomes the primary fast-entry mechanism.
- `Playbook` is the default narrative and primary branch.
- `Studio Ops` is the advanced operational branch.
- `Playbot` and `OCP Ops bot` stay separate.
- Cross-handoff becomes a first-class product capability.
- Document truth remains under PBS.
- Live operational truth remains under Ops.
- Shared endpoint env names may converge when PBS and Ops truly target the same service.
- Deprecated `.env` keys should be commented with replacement reasons instead of being silently removed.

## Document Set

| Document | Role | Use When |
| --- | --- | --- |
| `docs/integration/pbs_ocp_product_architecture.md` | Product architecture and decision lock | You need the parent-brand, surface, or edition contract |
| `docs/integration/pbs_ocp_surface_and_handoff_blueprint.md` | Landing, header, bot coexistence, and handoff blueprint | You need route, header, or handoff implementation guidance |
| `docs/integration/pbs_ocp_execution_program.md` | Long-running packet program and validation gates | You need packet sequencing, harness discipline, or closeout rules |
| `reports/execution_harness/pbs_ocp_integrated_service_program_20260421/main/manifest.json` | Main harness manifest | You need lane assignments, validation commands, or ref snapshot |

## Acceptance Criteria

| Item | Pass / Fail | Measurement | Evidence | Current Gap |
| --- | --- | --- | --- | --- |
| Product direction is singular | Pass when all three planning docs describe the same parent product, branch model, and bot model | Cross-read the docs for naming and boundary consistency | This index plus the three integration docs | Needs routine upkeep as implementation starts |
| Harness discipline is real | Pass when the main harness manifest/worklog/final report stay updated with packet evidence | Review execution-harness assets | `reports/execution_harness/pbs_ocp_integrated_service_program_20260421/main/*` | Final report still needs closeout fill-in |
| Future packets can start without re-discovery | Pass when a future worker can read this index and know where to begin | Manual read-through from this index into the linked docs | This index and linked docs | Implementation packets have not started from this index yet |

## Current Judgment

The repo is already closest to `shared landing + PBS roots + query-mode Studio Ops + reserved viewer/runtime namespaces`. The right move is not to invent a second product shell, but to formalize the existing shape into an enterprise OpenShift edition with stronger branch identity, explicit handoff, and cleaner truth ownership.

## Next Packet

The highest-leverage next implementation packet is:

`landing/header branch hardening + explicit handoff schema capture`

That packet should be followed by:

`ownership-map to backend seam codification`
