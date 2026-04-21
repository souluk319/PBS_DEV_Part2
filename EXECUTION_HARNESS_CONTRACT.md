---
status: active
doc_type: execution_contract
audience:
  - codex
  - engineer
precedence: 4
supersedes:
  - EXECUTION_HARNESS_CONTRACT.md (legacy version)
  - CODEX_OPERATING_CHARTER.md
  - HARNESS_ENGINEERING_CONTRACT.md
last_updated: 2026-04-21
---

# EXECUTION HARNESS CONTRACT

## Purpose

이 문서는 Codex 가 milestone 을 헛돌지 않고 끝까지 닫기 위한 실행 계약을 고정한다.

핵심 원칙은 하나다.

`중간 진행은 harness 에 쌓고, 사용자에게는 검증된 closeout packet 으로만 보고한다.`

## Renewal Default

PBS 는 이미 검증된 제품이므로, renewal 기간의 기본 packet 목표는 아래다.

- `refine existing surfaces`
- `harden runtime / retrieval / citation`
- `validate deliverables`
- `execute customer orders inside the current architecture`

기본적으로 허용하지 않는 것은 아래다.

- `reinvention-only rename or doctrine reset without order/quality reason`
- `temporary demo fork used as delivery path`

## Current Order Override

`2026-04-21` 기준 현재 order priority 는 아래다.

- `integrate PlayBook Studio and OCP Ops into one service inside PBS architecture`
- `retain landing and strengthen header branching`
- `keep Playbook as the main branch and Studio Ops as the advanced operational branch`
- `keep dual assistants separate and implement cross-handoff as a first-class capability`
- `lock document truth to PBS and operational truth to Ops`

따라서 현재 packet 판단은 아래 기준을 따른다.

- `PBS-only enhancement`, `general polish`, `standalone PBS hardening backlog` 는 기본 packet 목표가 아니다
- 위 항목들은 `service integration blocker`, `handoff blocker`, `validation blocker` 일 때만 현재 milestone 범위에 포함한다
- closeout verdict 는 `서비스가 하나처럼 느껴지는지`, `branching 과 handoff 가 고정됐는지`, `runtime ownership 이 설명 가능한지` 를 우선 근거로 삼는다

## Packet Modes

기본 packet 모드는 아래 셋 중 하나다.

- `micro packet`
- `default packet`
- `major task`

micro packet 이 아니면 default packet 으로 본다.  
major task 는 default packet 위에 병렬 lane 요구가 추가된 형태다.

작업 중 범위가 커지면 아래 순서로 즉시 승격한다.

- `micro packet -> default packet`
- `default packet -> major task`

## Harness Package

`default packet` 과 `major task` 는 아래 하네스 자산을 가진다.

- `reports/execution_harness/<task_id>/<lane_id>/manifest.json`
- `reports/execution_harness/<task_id>/<lane_id>/worklog.md`
- `reports/execution_harness/<task_id>/<lane_id>/final_report.json`

`micro packet` 은 이 세 파일이 선택이다.

## Manifest Minimum

`default packet` 과 `major task` 의 manifest 에는 시작 전에 아래를 고정한다.

- `task_id`
- `lane_id`
- `role`
- `cwd`
- `python_path`
- `worktree_path`
- `write_scope`
- `target_outputs`
- `validation_commands`
- `git_ref_snapshot`
- `status`

validation commands 는 구현 전에 먼저 잠근다.

`git_ref_snapshot` 은 최소 아래를 포함한다.

- `head_ref`
- `head_sha`
- `upstream_ref`
- `upstream_sha`
- `origin_main_sha`

## Micro Packet Exception

작업 범위가 작고 단일 surface 또는 단일 기능 조정에 머물면 `micro packet` 으로 처리할 수 있다.

### Conditions

아래를 모두 만족해야 한다.

- subsystem 두 개 이상 동시 수정 아님
- corpus / retrieval / viewer / runtime contract 재정의 아님
- cleanup / archive / release gate 작업 아님
- 병렬 lane 필수 작업 아님

### Kickoff Lock

micro packet 은 시작 전에 아래 네 개만 잠근다.

- `goal`
- `change_scope`
- `non_goals`
- `validation_commands`

### Micro Rules

- `main` 단독 실행 가능
- focused validation 을 `1개 이상` 수행한다
- manifest / worklog / final_report 는 선택이다
- closeout 은 `결과 + validation` 위주로 짧게 보고한다
- 검증 없는 closeout 은 허용하지 않는다

### Promotion Rule

아래 중 하나라도 발생하면 즉시 `default packet` 또는 `major task` 로 승격한다.

- 수정 subsystem 이 두 개 이상으로 늘어남
- corpus / retrieval / viewer / runtime contract 판단이 새로 걸림
- cleanup / archive / release gate 성격으로 커짐
- 병렬 탐색/구현/검증이 필요해짐

## Lane Model

기본 규칙은 아래다.

- `micro packet` 은 `main` 단독 가능
- `default packet` 의 작은 단일 파일 수정은 `main` 단독 가능
- subsystem 두 개 이상을 건드리거나, 탐색/구현/검증이 분리되면 병렬 lane 사용
- 병렬 기준 기본형:
  - `main`
  - `explorer`
  - `worker` or `reviewer`

Main lane 은 통합과 최종 verdict 를 맡는다.

## Major Task Rule

아래 중 하나라도 해당하면 `주요작업` 으로 본다.

- subsystem 두 개 이상 동시 수정
- corpus / retrieval / citation / viewer / runtime contract 변경
- cleanup / archive / ref-cut / regression verification packet
- 사용자가 병렬 특공대 투입을 명시한 경우

주요작업은 harness 시작 시점부터 병렬 lane 을 기록한다.

- `main` manifest 는 `major_task=true` 와 `parallel_execution_required=true` 를 가진다.
- `main` manifest 는 companion lane 계획을 포함한다.
- 최소 companion lane 구성은 아래다.
  - `explorer` 1개
  - `worker` 또는 `reviewer` 1개
- lane skeleton 이 준비되지 않은 major task 는 closeout 하지 않는다.

## Bootstrap Order

`default packet` 과 `major task` 는 아래 순서로 시작한다.

1. `task scope 잠금`
2. `prepare_execution_harness`
3. `manifest 작성`
4. `validation_commands 확정`
5. `구현`
6. `검증`
7. `final_report 작성`
8. `closeout`

`micro packet` 은 아래 순서로 시작한다.

1. `goal / change_scope / non_goals / validation_commands 잠금`
2. `구현`
3. `focused validation`
4. `짧은 closeout`

## Validation Loop

검증은 `작업 종류에 맞는 최소 세트`로 고정한다.

### A. Contract / Docs Only

- frontmatter or metadata sanity check
- broken reference / broken file path check
- changed docs 존재 여부 확인

### B. UI / Frontend

- build or type/lint if available
- route smoke for touched surface
- critical rendering check for touched page
- changed artifact path 기록

### C. Backend / Pipeline / Runtime

- focused unit or integration test if available
- pipeline smoke for touched stage
- output artifact existence
- manifest / runtime path / relation refresh evidence

### D. Retrieval / Chat / Corpus

- retrieval regression subset
- citation anchor resolution check
- touched evaluator test via `pytest` if suite exists
- `ragas` or equivalent metric subset if the repo already supports it
- failure case 저장 when the bug is reproducible
- buyer/demo/release packet or rehearsal metric 은 supporting evidence 로만 쓰고, core reader/runtime/retrieval gate 를 대체하지 않는다

검증이 없다면 closeout 도 없다.

## Change Discipline

실행 중 아래 원칙을 추가로 고정한다.

- `명시 요구 외 변경 0개`를 기본값으로 본다.
- UI packet 에서 사용자가 요청하지 않은 제목, 라벨, 버튼, badge, 설명 문구 추가는 실패로 본다.
- 관측/trace/audit packet 은 `실제 로그와 runtime data를 드러내는 것`만 허용하고, 없는 단계나 과장된 상태 표현을 만들지 않는다.
- 사용자가 특정 결과를 거부하면 다음 시도는 `축소`, `제거`, `원형 복구` 중 하나로만 간다.
- 실패한 packet 의 복구안으로 `지침서 수정`, `메타 원칙 설명`, `프로세스 제안`만 내놓는 것은 허용하지 않는다.
- renewal packet 에서 surface 재정의나 product framing 변경은 `active contract` 또는 `delivery quality` 근거가 없으면 금지한다.
- milestone 초반에는 `토큰 절약`보다 `이해 정확도`를 우선한다.
- 구현 전에 `무엇을 바꾸는지`, `무엇을 안 바꾸는지`, `무엇으로 검증하는지`를 충분히 잠근다.
- 이해가 얕은 상태에서 빨리 코드를 쓰는 것은 실패 패턴으로 간주한다.
- closeout 품질은 `적은 토큰`이 아니라 `정확한 결과와 검증`으로 평가한다.
- official lane 에서 영어 본문이 보이면 복구 기본값은 `translation completion packet` 이다.
- `영어라서 제외`, `불완전하니 삭제` 같은 조치는 최종 선택지가 아니며, 번역 완료 경로를 먼저 검토하지 않으면 closeout 하지 않는다.
- 공식 문서 rebuild 에서 `repo/AsciiDoc` 가 실패하면 기본 동작은 `fail-close` 다.
- `published HTML/PDF` fallback 은 명시적 사용자 승인 없이는 자동 사용하지 않는다.

## Reporting Model

사용자에게 보이는 보고는 아래 두 번뿐이다.

1. `milestone kickoff`
2. `milestone closeout`

closeout 에는 아래를 포함한다.

- `현재 판단`
- `핵심 근거`
- `ref 기준`
- `산출물 경로`
- `검증 결과`
- `다음 행동`

중간 시도, 복구, 실험 메모는 worklog 로만 남긴다.

`micro packet` 은 closeout 을 더 짧게 할 수 있다.

- `결과`
- `검증`
- 필요 시 `다음 행동`

## Escalation Rules

아래 경우만 사용자 판단을 요청한다.

- 제품 방향 변경
- 파괴적 삭제
- 외부 비용 또는 보안 판단
- active contract 충돌
- validation target 자체가 비어 있어서 작업 기준을 새로 정해야 하는 경우

그 외는 lane 안에서 복구한다.

## Done Definition

아래를 모두 만족해야 milestone 을 닫을 수 있다.

1. 수정된 코드 또는 문서가 실제로 존재한다.
2. target output 이 생성 또는 갱신됐다.
3. validation command 결과가 남아 있다.
4. 필요한 smoke evidence 가 남아 있다.
5. `default packet` / `major task` 는 `final_report.json` 이 채워졌다.
6. `micro packet` 은 packet mode 에 맞는 짧은 closeout 이 남아 있다.
7. 사용자가 다음 행동을 바로 이해할 수 있다.

`거의 됐다`, `대충 된다`, `아마 맞다` 같은 문장은 closeout verdict 로 쓰지 않는다.
