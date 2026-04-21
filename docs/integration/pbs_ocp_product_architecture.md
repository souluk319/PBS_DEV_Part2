---
status: active
doc_type: integration_plan
artifact_id: pbs_ocp_product_architecture
owner: worker-contracts-gates
last_updated: 2026-04-21
---

# PBS + OCP Ops Product Architecture

## Goal

Lock the integrated product architecture for the OpenShift operator order inside PBS. The delivery must feel like one enterprise program while preserving two distinct expert surfaces: the Playbook-first PBS surface and the advanced Studio Ops surface.

## Non-Goals

- Do not redefine PBS product doctrine or surface model.
- Do not create a new top-level OCP product line, runtime, or brand.
- Do not rename existing reader surfaces unless a traced product decision requires it.
- Do not solve source ingestion, corpus rebuild, or runtime implementation in this document.
- Do not add new CTA, badge, or decorative UI language here.
- Do not merge Playbot and OCP Ops bot into one shared chat thread.

## Product Positioning

PBS remains the parent product. The OpenShift delivery is best read as a productized PBS edition:

- Parent brand: `PlayBook Studio`
- Delivery descriptor: `PlayBook Studio for OpenShift`
- Main story: `Playbook`
- Advanced operational surface: `Studio Ops`
- Internal workstream shorthand: `OCP Ops`

The customer-facing reading should be:

`PlayBook Studio is the enterprise knowledge and operating shell.`

`Playbook` is the main narrative and default entry for document-grounded work.

`Studio Ops` is the advanced operational branch for live OpenShift work, cluster state, resources, actions, and operator-specific assistance.

This keeps the delivery aligned with PBS renewal doctrine while still acknowledging that the OCP order has a deeper operational surface than a pure document product.

## Surface Map

| Surface | Role | OCP-specific role | Ownership | Notes |
| --- | --- | --- | --- | --- |
| `Landing` | Shared brand shell and fast entry hub | Explains the OpenShift edition and branches users by intent | PBS shell | Keep existing landing and strengthen branching instead of replacing it |
| `Playbook Library` | Main entry, index, package state, delivery status | Default starting point for OCP operator knowledge work | PBS | `Control Tower` remains a library view, not a separate product shell |
| `Wiki Runtime Viewer` | Reading and anchor navigation | Canonical document-reading surface for OpenShift playbooks | PBS | Viewer namespaces stay reserved and anchor-first |
| `Chat Workspace / Playbot` | Grounded answer, citation, next play | Default conversational orchestrator for documentation and procedure | PBS | Playbot stays separate from Ops bot |
| `Studio Ops / OCP Ops bot` | Advanced operations surface | Live cluster/resource/YAML/action assistance | Ops under PBS shell | Lives inside the shared product shell, not as a separate brand |
| `Release/Readiness packet` | Evidence and export | Delivery snapshot, validation evidence, package summary | Derived from PBS truth + Ops evidence | Supporting surface only, never the truth owner |

## Navigation Model

The navigation model should stay landing-first, header-branch-aware, and anchor-first once the user is inside a surface.

### Shared shell

1. User enters through `/`, the shared landing shell.
2. The landing hero and header expose two primary fast-entry branches:
   - `Playbook`
   - `Studio Ops`
3. The header also exposes a stable `Control Tower` path for operational status and package state.

### Playbook branch

1. User enters `Playbook Library` as the default knowledge-first branch.
2. Library opens the relevant playbook or book in `Wiki Runtime Viewer`.
3. Viewer resolves section, figure, and anchor jumps with stable IDs.
4. `Chat Workspace / Playbot` reuses the same anchors for grounded answers and follow-up navigation.

### Studio Ops branch

1. User enters `Studio Ops` from the landing header or landing card.
2. Studio Ops keeps its own advanced operational context and chat surface.
3. When an ops issue needs official procedure or reading depth, it hands the user back to Playbook surfaces through a grounded handoff.

Navigation rules:

- The shared landing shell chooses the branch; the branch chooses the surface.
- `Playbook` remains the default narrative branch and primary landing card.
- `Studio Ops` remains a high-power branch, not the default story.
- Every citation should land on a viewer anchor or a structured section ID.
- Every chat answer should be able to return the user to the originating library or viewer context.
- Studio Ops transitions should preserve enough payload to reopen the relevant playbook or citation context.
- The package must not create dead-end pages that cannot be reached from the library or return to it.

## Branding / Naming Recommendation

Keep `PlayBook Studio` as the parent brand and use `PlayBook Studio for OpenShift` as the delivery descriptor when customer-facing differentiation is needed.

Recommended naming stance:

- Keep `PlayBook Studio` as the visible parent brand.
- Use `PlayBook Studio for OpenShift` for edition-level positioning, release material, and enterprise delivery language.
- Keep `Playbook Library`, `Wiki Runtime Viewer`, and `Chat Workspace` as PBS surface names.
- Keep `Studio Ops` as the visible advanced surface label.
- Use `OCP Ops` only as an execution shorthand, not as the main external product name.
- Prefer short, literal labels over over-branded surface names.

Rationale:

- It preserves the current product doctrine.
- It lets the OpenShift order read like a first-class enterprise edition instead of a bolt-on.
- It reduces surface churn while still giving the operational surface a strong identity.

## Phased Execution Plan

### Phase 0: Architecture Lock

Lock the parent brand, package descriptor, surface map, and navigation model in tracked documentation.

- Output: this planning doc, the surface/handoff blueprint, and the execution program.
- Exit condition: no remaining ambiguity about product boundary, surface ownership, or branch identity.

### Phase 1: Shared Shell and Branching Lock

Keep the landing page and strengthen branching through the header and landing cards.

- Output: landing/header contract, branch labels, route map.
- Exit condition: `Playbook` and `Studio Ops` are both explicit entry paths inside one shell.

### Phase 2: Handoff and Bot Separation Lock

Keep Playbot and OCP Ops bot separate while formalizing their handoff contract.

- Output: handoff schema, ownership rules, replay/audit plan.
- Exit condition: cross-handoff is explicit, reversible, and traceable.

### Phase 3: Package and Truth Mapping

Bind OpenShift operator content to the existing PBS truth bundle and preserve the document=PBS / operations=Ops split.

- Output: ownership map, package manifest, shared context contract.
- Exit condition: no divergent truth owner exists for the same customer flow.

### Phase 4: Navigation and Runtime Hardening

Verify anchor landing, viewer return paths, citation reuse, and ops-to-playbook handoff reopening.

- Output: route smoke, anchor map, citation checks, handoff replay checks.
- Exit condition: navigation is stable and bidirectional across the product branches.

### Phase 5: Release and Readiness

Connect the OpenShift edition to release evidence and readiness reporting without changing truth ownership.

- Output: readiness packet, validation snapshot, linked evidence bundle.
- Exit condition: the edition can be released and reviewed from the same PBS contract.

## Acceptance Criteria

| Item | Pass / Fail | Measurement | Evidence | Current Gap |
| --- | --- | --- | --- | --- |
| Single parent product is preserved | Pass when every OpenShift/Ops reference is nested under PBS and no separate product shell appears | Review document titles, package labels, and surface names for standalone branding | This planning doc, release packet naming, package manifest | No release artifact yet reflects the final edition naming |
| Shared landing with explicit branching exists | Pass when the landing and header expose `Playbook` and `Studio Ops` as primary branches | Review route map and header/landing contract | Surface/handoff blueprint, route map | Landing/header contract not yet implemented in full |
| Surface map is complete | Pass when landing, Playbook surfaces, Studio Ops, and release/readiness are all mapped with one owning role each | Compare the surface map against the execution plan | This planning doc, route manifest, readiness packet template | No runtime route manifest exists for the full edition yet |
| Bot separation is preserved | Pass when Playbot and OCP Ops bot remain separate surfaces with explicit ownership rules | Review handoff contract and surface labels | Surface/handoff blueprint, audit contract | No first-class handoff API exists yet |
| Navigation is anchor-first and reversible | Pass when every viewer/chat/handoff transition resolves to a stable anchor or return path | Check route links, citation landing targets, and handoff replay | Citation map, viewer route checks, handoff replay evidence | OCP-specific handoff replay checks are not yet linked |
| Document truth and operational truth stay split | Pass when documentation truth remains under PBS and live operations remain under Ops | Compare ownership map against runtime and ops contracts | Corpus truth contract, backend absorption order, ownership map | Shared context contract is documented but not yet coded |
| Release/readiness output is evidence-backed | Pass when the release packet includes validation snapshots and links back to source anchors and ops evidence | Verify packet existence and link integrity | Release/readiness packet, validation reports | Only the planning structure exists, not the final packet |

## Decision Log

| Date | Decision | Why | Impact |
| --- | --- | --- | --- |
| 2026-04-21 | Keep `PlayBook Studio` as the parent brand | Prevents a doctrine reset and avoids a duplicate product shell | OpenShift delivery remains an edition/package, not a separate product |
| 2026-04-21 | Keep the landing page and strengthen branching instead of replacing it | Preserves the strongest shared shell while allowing fast intent-based entry | The product can feel unified without collapsing surfaces |
| 2026-04-21 | Make `Playbook` the main narrative branch and `Studio Ops` the advanced branch | Matches customer intent and preserves PBS doctrine | The user’s first story remains knowledge-first while ops stays powerful |
| 2026-04-21 | Keep Playbot and OCP Ops bot separate | Their truth scopes and working styles are different | Cross-handoff becomes a core capability instead of a hidden swap |
| 2026-04-21 | Use anchor-first navigation and reversible handoff | Keeps chat, viewer, and ops transitions grounded to the same evidence | Citation and context drift become easier to detect and fix |
| 2026-04-21 | Treat release/readiness as a supporting surface | Keeps truth ownership in the library, viewer, and ops evidence flows | Evidence stays derivative instead of becoming a competing source |
