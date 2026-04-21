---
status: active
doc_type: security_contract
audience:
  - codex
  - engineer
precedence: special_override_for_customer_private
supersedes:
  - SECURITY_BOUNDARY_CONTRACT.md (legacy version)
last_updated: 2026-04-17
---

# SECURITY BOUNDARY CONTRACT

## Purpose

이 문서는 customer/private 문서가 제품 안으로 들어올 때 지켜야 할 hard boundary 를 고정한다.

핵심은 하나다.

`customer/private runtime 은 official runtime 과 연결될 수는 있어도, tenant/workspace/pack 경계를 절대 잃지 않는다.`

## Renewal Delivery Clarification

현재 `official-source OCP operator package order` 는 customer/private source 가 들어오지 않는 한
이 계약의 hard boundary 대상이 아니다.

private/customer source 가 들어오는 순간부터는 이 계약이 override 로 적용된다.

추가로, private/customer source 에 영어 본문이 포함되어도 기본 제품 행위는 삭제가 아니라
`boundary 유지 + translation completion` 이다.

## When This Contract Applies

아래 중 하나라도 해당되면 이 문서를 반드시 적용한다.

- customer/private source ingest
- pack runtime
- official/private mixed answer
- remote provider egress
- tenant/workspace/pack scoped retrieval or viewer output

## Required Security Envelope

모든 private 또는 mixed 자산은 최소 아래 필드를 가진다.

- `tenant_id`
- `workspace_id`
- `pack_id`
- `pack_version`
- `classification`
- `access_groups`
- `provider_egress_policy`
- `approval_state`
- `publication_state`
- `redaction_state`

## Boundary Rules

1. 현재 PoC retrieval 은 최소 `selected_draft_ids`, `restrict_uploaded_sources`, pack-scoped citation/viewer truth 와 같은 pack selector 를 유지한다.
2. published multi-tenant runtime 으로 승격할 때는 retrieval boundary 를 `tenant_id + workspace_id + pack_version` hard scope 로 올린다.
3. citation, viewer_path, related navigation 은 같은 pack 또는 허용된 official bridge 만 가리킨다.
4. `unreviewed` 자산은 runtime surface 에 올리지 않는다.
5. `restricted` 또는 `high_risk` 는 human approval 없이 published 로 이동하지 않는다.
6. `redaction_state = raw` 인 private 자산은 remote provider egress 를 열지 않는다.

## Official Bridge Rules

customer/private pack 이 official runtime 과 연결될 수 있는 방식은 아래뿐이다.

- official entity hub 참조
- official book 참조
- official section 참조

bridge output 은 항상 truth label 을 유지한다.

- display truth label:
  - `official`
  - `private`
  - `mixed`
- runtime system truth:
  - `official_validated_runtime`
  - `official_candidate_runtime`
  - `private_customer_pack_runtime`
  - `mixed_runtime_bridge`

boundary label 없이 private text 를 official surface 에 섞으면 안 된다.

## Audit And Debug Rules

- audit trail 은 boundary 안에서 유지한다.
- debug payload 는 raw private dump 대신 trace 와 metadata 를 남긴다.
- cross-pack raw dump 는 만들지 않는다.

## Promotion Gate

customer/private pack runtime publication 은 아래가 모두 맞을 때만 열린다.

- security envelope complete
- approval state present
- publication state present
- pack identity present
- egress policy present

## Hard Fail

아래는 즉시 fail 이다.

1. cross-tenant citation
2. cross-workspace exposure
3. unreviewed asset exposure
4. unspecified egress 로 remote provider 호출
5. restricted or high_risk 자산을 approval 없이 published 처리
