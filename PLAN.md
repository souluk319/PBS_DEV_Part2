# 랜딩 헤더 메뉴 + CTA 분기 정리 계획

## 요약
루트 랜딩(`/`)은 네가 만든 랜딩을 그대로 유지한다.  
여기에만 최소한의 분기 UI를 추가한다.

- 랜딩 헤더에 `메뉴 버튼` 추가
- 메뉴 팝오버 안에 ` /studio `, ` /aiops ` 두 항목만 둠
- 히어로 CTA를 `Launch Studio | AI Ops | Demo 영상` 3버튼으로 변경
- `/studio` 와 `/aiops` 는 서로 다른 페이지로 유지
- 랜딩 상단에는 엔지니어링 설명, lane, compat 같은 내부 문구를 두지 않음

## 구현 변경
### 1. 랜딩 헤더
- 현재 `Hero.tsx` 상단 헤더 영역에 `메뉴 버튼`을 둔다.
- 메뉴 버튼 클릭 시 작은 팝오버/드롭다운이 열린다.
- 팝오버 항목은 딱 두 개만 둔다.
  - `Studio` -> `/studio`
  - `AI Ops` -> `/aiops`
- 기존 헤더의 `Control Tower`, `Studio Ops` 직접 링크는 제거한다.
- 언어 버튼(`KOR`)은 그대로 유지한다.

### 2. 히어로 CTA
- 현재 `Launch Studio | Watch Demo` 구조를 아래처럼 바꾼다.
  - `Launch Studio` -> `/studio`
  - `AI Ops` -> `/aiops`
  - `Demo 영상` -> 기존 demo 버튼 역할 유지
- 버튼 순서는 네가 말한 그대로 고정한다.
- `AI Ops` 버튼은 `Launch Studio` 와 같은 레벨의 정식 CTA로 둔다.

### 3. 라우트
- `ROUTES.aiOps = '/aiops'` 추가
- `/studio` 는 기존 PBS 화면 유지
- `/aiops` 는 현재 J 쪽 OCP OPS surface가 들어갈 별도 route로 둔다
- 이번 패킷에서는 진입 구조를 먼저 맞추고, `/aiops` 본문은 현재 연결 가능한 ops surface를 그대로 사용한다

### 4. 랜딩 유지 원칙
- 랜딩 본문(Hero, 기존 소개 섹션)은 유지
- 랜딩에 shared shell, branch 설명, compatibility 설명 같은 내부 작업 문구는 올리지 않음
- 목적은 “설명”이 아니라 “바로 들어가는 진입점” 제공

## 테스트
- `/` 접속 시 랜딩 상단에 메뉴 버튼이 보여야 함
- 메뉴 버튼 클릭 시 `/studio`, `/aiops` 두 항목만 보여야 함
- `Launch Studio` 클릭 시 `/studio` 이동
- `AI Ops` 클릭 시 `/aiops` 이동
- `Demo 영상` 버튼은 기존 동작 유지
- 랜딩에 `Shared Service Shell`, `lane`, `compatibility` 같은 문구가 없어야 함
- `presentation-ui` 빌드와 기존 랜딩/라우트 테스트는 다시 통과해야 함

## 기본 가정
- 메뉴 버튼은 랜딩 히어로 상단 헤더에만 추가한다
- `/aiops` 는 별도 정식 페이지 경로로 둔다
- 이번 변경의 목적은 UI 진입 구조 정리이며, 두 서비스의 내부 기능 고도화는 별도 패킷으로 이어간다
