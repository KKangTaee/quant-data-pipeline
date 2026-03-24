# Phase 4 Current Chapter TODO

## 목적
이 문서는 Phase 4 첫 실행 챕터를
전략 실행 UI의 구조 결정과 첫 구현 준비 관점에서 관리하기 위한 작업 보드다.

상위 계획 문서:
- `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md`

선행 문서:
- `.note/finance/phase3/PHASE3_UI_RUNTIME_FUNCTION_CANDIDATES.md`
- `.note/finance/phase3/PHASE3_UI_USER_INPUT_SET_DRAFT.md`
- `.note/finance/phase3/PHASE3_UI_RESULT_BUNDLE_DRAFT.md`

---

## 현재 챕터 범위

현재 챕터의 목표:

1. 백테스트 UI 구조를 사용자와 합의해 결정한다
2. 첫 UI 구현에 필요한 공개 runtime 경계를 구체화한다
3. 첫 전략 실행 화면의 최소 뼈대를 구현할 준비를 마친다

---

## 큰 TODO 보드

### A. UI Structure Decision
상태:
- `completed`

세부 작업:
- `[completed]` UI 구조 선택지 정리
  - 기존 수집 앱 통합 / 별도 앱 / multipage 재편 중 현실적인 선택지와 트레이드오프 정리
- `[completed]` 사용자 선택 확정
  - 구조상 중요한 갈림길은 사용자 선택 후에만 구현 시작
- `[completed]` 선택 결과를 기준 문서에 반영
  - 구조 결정 내용을 계획 문서와 TODO 보드에 반영

완료 기준:
- 백테스트 UI의 첫 구현 위치와 구조가 합의되어 있어야 함

---

### B. Runtime Public Boundary
상태:
- `completed`

세부 작업:
- `[completed]` wrapper 함수 시그니처 구체화
  - UI가 직접 호출할 runtime wrapper 입력을 코드 수준으로 좁힘
- `[completed]` result bundle builder 책임 구체화
  - summary / chart / meta 생성 책임을 명확히 정의
- `[completed]` 에러/빈 결과 반환 규칙 초안 정리
  - UI가 빈 결과나 잘못된 입력을 일관되게 처리하도록 계약 정리

완료 기준:
- UI가 호출할 함수와 반환 형식이 구현 가능한 수준으로 고정되어 있어야 함

---

### C. First Screen Scope
상태:
- `completed`

세부 작업:
- `[completed]` 첫 화면 범위 확정
  - single strategy execution 화면만 먼저 구현할지 범위를 고정
- `[completed]` 결과 레이아웃 초안 정리
  - summary / chart / result table / meta 배치 초안 정리
- `[completed]` advanced input 노출 범위 정리
  - 처음 숨길 항목과 나중에 열 항목 구분

완료 기준:
- 첫 UI 구현 범위가 좁고 명확해야 함

---

## 현재 작업 중 항목

현재 `in_progress`:
- `없음`

바로 다음 체크 대상:
- `Phase 4 factor / fundamental entry chapter 진행`

---

## 현재 진척도

- Phase 4 first chapter:
  - 약 `65%`

판단 근거:
- Phase 4는 공식 진입을 마쳤고
- UI 구조 선택과 사용자 합의가 완료되었고
- 메인 앱 + 탭 구조 방향이 확정되었고
- `Equal Weight` first public wrapper가 코드/문서에 반영되었고
- `Equal Weight` first-pass form이 Backtest 탭에 반영되었고
- form submit이 실제 DB-backed wrapper 실행까지 연결되었고
- first-pass 결과 레이아웃도 KPI / chart / table / meta 구조로 정리되었고
- 입력 오류 / 데이터 부재 / 일반 실행 오류 구분도 first-pass 수준으로 반영되었고
- `GTAA`가 두 번째 공개 전략으로 추가되었고
- `Risk Parity Trend`가 세 번째 공개 전략으로 추가되었고
- `Dual Momentum`이 네 번째 공개 전략으로 추가되었고
- 현재 공개 DB-backed price-only 전략 4종이 UI에서 모두 선택 가능하며,
  `Backtest` 탭은 `Single Strategy` / `Compare & Portfolio Builder` 2단 구조로 확장되었고
- 다중 전략 비교와 weighted portfolio builder가 first-pass 수준으로 열렸으며,
  persistent backtest history도 first-pass 수준으로 추가되었으며,
  이후 filter / search / drilldown,
  recorded date range / metric sort / single-strategy rerun까지 열렸으며,
  metric threshold filter,
  single-strategy `Load Into Form`,
  current form prefill까지 지원하게 되었고,
  single-strategy / compare 시각화 강화도 first-pass 수준으로 반영되었고,
  compare 결과에도 focused strategy drilldown이 추가되었고,
  weighted portfolio 결과도 동일한 marker / balance-extremes / period-extremes 읽기 흐름으로 정리되었으며,
  첫 UI 실행 챕터는 실질적으로 완료 상태로 보고,
  다음 활성 챕터는 factor / fundamental 전략 진입 준비로 넘어가는 것이 자연스럽다
