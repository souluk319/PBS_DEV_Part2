---
status: active
doc_type: integration_blueprint
artifact_id: pbs_ocp_surface_and_handoff_blueprint
owner: worker-contracts-gates
last_updated: 2026-04-21
---

# PBS OCP Surface and Handoff Blueprint

## Goal

Lock the landing/header branching model for the OpenShift edition and define how Playbot and the OCP Ops bot coexist, hand off, and resume without losing truth context, route context, or user intent.

## Design Principles

- One shared shell, multiple intent branches.
- Header state should explain where the user is, not decorate the page.
- Landing entry should choose the right branch first, then refine within that branch.
- `Playbook` remains the primary narrative and default branch.
- `Studio Ops` remains the advanced operational branch.
- Playbot remains the primary orchestration identity unless an OCP-specific operational task is actively owned by the OCP Ops bot.
- Handoffs must be explicit, reversible, and payload-driven.
- Each state transition must be observable in logs or runtime metadata.
- No hidden surface forks, no silent bot swaps, and no duplicate ownership of the same turn.

## Header and Landing Entry Model

### Entry Model

| Entry | Purpose | Measurement | Evidence | Current Gap |
| --- | --- | --- | --- | --- |
| Landing header `Playbook` branch | Fast entry into the knowledge-first PBS experience | Route resolves to Playbook-first shell | `routes.ts`, current landing shell, this blueprint | Header branching not fully formalized yet |
| Landing header `Studio Ops` branch | Fast entry into advanced OCP operations | Route resolves to Studio Ops surface without hiding PBS identity | `routes.ts`, current Studio ops toggle, this blueprint | No branch-specific scope marker yet |
| Hero card `Playbook` | Default first card for browse, read, and grounded Playbot use | Card opens library or studio in PBS mode | Current landing card pattern, this blueprint | Card contract not yet pinned in code |
| Hero card `Studio Ops` | Secondary card for operator/live-cluster work | Card opens Studio in ops mode | Current landing card pattern, this blueprint | Ops card copy and payload contract not yet pinned |
| Header `Control Tower` path | Operational status path inside PBS | Route resolves to the library control-tower view | `routes.ts`, library/control-tower route | Shared shell state around it is not yet unified |

### Header Branching Rules

- The header must branch by user intent and order scope, not by content volume.
- A landing click should preserve the active truth family and open the correct primary surface in one step.
- The OpenShift branch may reuse the shared shell, but it needs a visible scope marker so the user knows they are in the operator lane.
- If a user enters through chat, the header must still expose a stable path back to library and viewer without resetting context.
- Back navigation must not erase the active bot role unless the user explicitly exits the order lane.
- The header must not imply that Playbot and the OCP Ops bot are the same assistant.

### Recommended Branch Labels

- `Playbook`
- `Studio Ops`
- `Control Tower`

These labels are short enough for the shared shell and align with the current repo reality better than inventing a new top-level product family.

## Bot Coexistence Model

Playbot and the OCP Ops bot share one product shell but do not share the same truth owner, state owner, or turn owner at every moment.

| Role | Primary job | May own turn? | May hand off? | May mutate shared state? | Current Gap |
| --- | --- | --- | --- | --- | --- |
| Playbot | Documentation-first orchestration, grounded answers, citation, next-play guidance | Yes | Yes | Yes, through shared contract only | No explicit ownership ledger |
| OCP Ops bot | OCP operator-specific assistance, live cluster/resource narrowing, and operator-native guidance | Yes, within the ops branch | Yes | Yes, through shared contract only | No explicit coexistence policy |

### Coexistence Rules

- Only one bot owns a user turn at a time.
- The inactive bot can observe the shared handoff payload, but it cannot answer as if it owned the session.
- Playbot is the default entry point when the user intent is mixed, unclear, or cross-surface.
- OCP Ops bot is the preferred owner only after the user enters an operator-scoped flow or accepts an operator-specific handoff.
- Both bots must preserve the same source-of-truth references, citation anchors, and session identifiers.
- The bot switch must be visible in the UI and replayable in audit traces.

## Handoff States and Payloads

### State Machine

| State | Meaning | Allowed next states | Required payload | Evidence | Current Gap |
| --- | --- | --- | --- | --- | --- |
| `idle` | No active bot ownership has been established | `claimed`, `routed` | `session_id`, `surface`, `intent_summary` | State log entry | No shared state store defined |
| `claimed` | One bot has taken temporary ownership to evaluate the request | `routed`, `returned`, `closed` | `from_bot`, `claimed_at`, `reason` | Claim record | Claim timeout rule missing |
| `routed` | Session has been routed to the other bot or surface | `active`, `returned`, `closed` | `to_bot`, `handoff_reason`, `context_ref` | Handoff record | Route selection rules missing |
| `active` | Receiving bot now owns the current turn | `returned`, `closed` | `active_bot`, `payload_hash`, `trace_id` | Active ownership record | No active ownership indicator |
| `returned` | Ownership came back to Playbot or the prior bot | `closed`, `claimed` | `return_reason`, `resume_context` | Return record | Resume contract missing |
| `closed` | The handoff transaction is complete | none | `close_reason`, `final_owner` | Close record | Close criteria not formalized |

### Minimum Payload Contract

Every handoff payload should include:

- `session_id`
- `correlation_id`
- `surface_id`
- `surface_branch`
- `from_bot`
- `to_bot`
- `intent_summary`
- `handoff_reason`
- `context_ref`
- `citation_ref` when the handoff is grounded in a specific anchor or section
- `trace_id`
- `payload_hash`
- `boundary_truth`
- `runtime_truth_label`
- `approval_state`
- `publication_state`

### Payload Rules

- Payloads must be small enough to be replayed in logs and support tools.
- A payload must never depend on hidden conversational memory alone.
- If the handoff changes surface, the payload must state the source surface and destination surface explicitly.
- If the handoff changes bot ownership, the payload must name both sides and the reason for the switch.
- If context is incomplete, the payload must say so instead of fabricating continuity.
- If the handoff crosses the PBS server-session store and the ops local-storage session store, `correlation_id` must be present.

## Validation Checks

| Check | Pass / Fail | Measurement | Evidence | Current Gap |
| --- | --- | --- | --- | --- |
| Header branches are deterministic | Pass when the same intent lands on the same branch | Route smoke on landing entry points | `docs/integration/` blueprint set | No executable route test yet |
| Landing preserves scope | Pass when OCP entry keeps order scope visible after navigation | Visual / metadata smoke | `docs/integration/` blueprint set | Scope marker not implemented |
| Bot ownership is singular | Pass when only one bot owns the turn at a time | State transition audit | Handoff payload logs | No ownership ledger exists yet |
| Handoff payload is complete | Pass when all minimum payload fields are present | Schema check on emitted payload | Handoff payload logs | Schema not codified in code |
| Return path is reversible | Pass when a returned session can resume without context loss | Replay a routed session and confirm resume context | Handoff payload logs | Resume contract missing |
| Citation context survives handoff | Pass when citation_ref and context_ref are preserved across the switch | Compare before/after payloads | Handoff payload logs | No explicit citation retention check |
| Cross-store audit replay works | Pass when PBS chat trace and Ops chat trace can be correlated through one id | Compare server audit log and ops session trace | Correlated trace pair | No shared correlation id yet |

## Current Gaps

- No committed route contract yet for landing/header branching.
- No shared handoff schema yet for Playbot and OCP Ops bot transitions.
- No explicit ownership ledger or transition audit surface yet.
- No stable resume contract yet for returned sessions.
- No validated payload replay test yet for the handoff path.
- No code-level scope marker yet for the OpenShift landing branch.
- PBS server sessions and Ops local-storage sessions are still separate stores without a shared correlation id.
- Current labels still drift between `Playbot`, `OCP PlayBook 챗봇`, and `Copilot workspace`.

## Next Decision Gate

This blueprint is ready to be converted into implementation work once the route map, ownership ledger, and handoff schema are each pinned to a concrete runtime surface.
