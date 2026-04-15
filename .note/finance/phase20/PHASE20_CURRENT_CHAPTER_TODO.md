# Phase 20 Current Chapter TODO

## 상태
- `practical closeout / manual_validation_pending`

## 1. Candidate Inventory And Bundle Organization

- `completed` phase20 kickoff plan 문서 생성
- `completed` current candidate / workflow inventory first pass
  - strongest / near-miss candidate를 다시 보는 현재 경로 정리
  - compare / weighted / saved portfolio 전환 시 불편 지점 정리
- `completed` candidate bundle surface shortlist
  - current candidate를 UI에서 다시 쓰기 위한 묶음 단위 정의
- `completed` current candidate compare re-entry first work unit
  - `Compare & Portfolio Builder` 안에서 current anchor / near-miss를 바로 compare로 다시 보내는 surface 추가
  - current candidate registry를 quick action과 custom bundle selection에 연결
  - QA feedback 기준으로 quick action 의미, registry source, load 이후 무엇이 바뀌는지 더 직접적으로 설명하도록 보강

## 2. Compare And Portfolio Workflow Hardening

- `completed` compare-to-weighted bridge friction cleanup
  - compare 결과가 어떤 후보 묶음에서 왔는지 `Current Compare Bundle`로 바로 보이게 정리
  - weighted portfolio builder가 compare source context를 같이 들고 가도록 보강
- `completed` weighted result re-entry flow 정리
  - weighted portfolio meta와 history context에 compare source context가 남도록 연결
  - compare -> weighted -> saved 흐름이 같은 작업 맥락으로 이어지게 정리
- `completed` saved portfolio usability hardening shortlist
  - 저장된 포트폴리오에 source context를 같이 남기도록 보강
  - `Edit In Compare`, `Replay Saved Portfolio`, `Source & Next Step` 탭으로 다음 행동이 더 직접적으로 보이게 정리

## 3. Validation

- `completed` `py_compile`
- `completed` `.venv` import smoke
- `completed` current candidate registry helper smoke
  - registry row가 compare prefill contract로 변환되는지 확인
- `completed` compare source context helper smoke
  - current candidate / saved portfolio source context가 weighted/saved workflow와 연결되는지 확인
- `completed` current candidate re-entry UX clarification fix
  - `Load Current Anchors`, `Load Lower-MDD Near Misses` 의미 설명 추가
  - current candidate list가 자동 누적이 아니라 curated registry라는 설명 추가
  - load 직후 `What Changed In Compare` 요약 카드가 보이도록 보강
- `completed` current candidate re-entry layout cleanup
  - compare 화면의 기본 흐름이 먼저 보이도록 `Strategies` 선택을 상단에 유지
  - current candidate 재진입은 secondary expander로 내려서 보조 도구처럼 읽히게 정리
  - 긴 설명은 `What This Does` expander 안으로 접어 compare 첫 화면의 혼잡도를 줄임
- `completed` compare surface divider cleanup and saved-portfolio placement review
  - compare / weighted / saved portfolio 사이의 top-level divider를 제거해 line 과밀도를 낮춤
  - `Saved Portfolios`는 별도 top-level 탭으로 분리하지 않고, 같은 operator workflow의 마지막 단계로 유지
- `completed` family-variant compare layout unification
  - compare `Strategy-Specific Advanced Inputs`에서 `Quality / Value / Quality + Value`를 GTAA처럼 한 섹션으로 읽히게 정리
  - family variant selector와 선택된 variant 세부 설정을 같은 expander 안에 이어서 보이게 보강
- `completed` strict annual benchmark tooltip clarification
  - `Benchmark Contract` tooltip에서 `Ticker Benchmark`와 `Candidate Universe Equal-Weight`가 각각 무엇을 비교하는지 plain language로 설명
  - `Candidate Universe Equal-Weight` 선택 시 의미를 화면 안에서 바로 이해할 수 있도록 상태 캡션 보강
- `completed` benchmark contract vs reference ticker display disambiguation
  - `Candidate Universe Equal-Weight / SPY`가 하나의 benchmark처럼 읽히지 않도록 compare summary와 current candidate contract summary에서 contract와 reference ticker를 분리 표기
  - equal-weight benchmark일 때 `SPY`가 benchmark 자체가 아니라 reference ticker일 수 있다는 설명을 compare 카드 안에서도 보강
- `completed` benchmark ticker와 guardrail/reference ticker 역할 분리
  - strict annual UI에서 `Benchmark Ticker`와 `Guardrail / Reference Ticker`의 역할을 분리
  - equal-weight benchmark와 SPY reference를 같은 값으로 오해하지 않도록 정리
- `completed` benchmark contract별 입력 강조 UX 정리
  - `Ticker Benchmark`일 때는 `Benchmark Ticker`를 중심으로, `Guardrail / Reference Ticker`는 optional 분리 입력으로 읽히게 정리
  - `Candidate Universe Equal-Weight`일 때는 benchmark ticker가 직접 baseline 계산에는 쓰이지 않는다는 설명을 함께 보여주도록 정리
- `completed` benchmark / guardrail 설명 중심 UX로 최종 정리
  - form 제약 때문에 contract별 hide/show나 별도 레이아웃 반영 버튼은 최종안에서 제거
  - `Real-Money Contract`에는 benchmark baseline 관련 입력만 남기고,
    `Guardrail / Reference Ticker (Optional)`는 `Guardrails` 탭으로 옮겨 실제 역할과 같은 위치에서 읽히게 정리
- `completed` current candidate re-entry plain-language labeling cleanup
  - `Load Current Anchors` / `Load Lower-MDD Near Misses` 같은 내부자 표현을 더 직접적인 버튼 이름으로 정리
  - 빠른 버튼 2개와 직접 선택 1개의 차이를 각 버튼 아래 설명으로 바로 읽히게 보강
- `completed` current candidate re-entry tabbed layout and registry-source clarification
  - 재진입 surface를 `Quick Bundles` / `Pick Manually` 두 탭으로 분리
  - 문서 생성이나 새 백테스트만으로 자동 노출되는 구조가 아니라 registry 기반이라는 점을 UI에서 바로 설명
- `completed` compare prefill confirmation card plain-language cleanup
  - `What Changed In Compare`의 추상적 용어를 더 직접적인 문장으로 정리
  - 무엇이 불러와졌는지 / 어디서 확인하는지 / 다음에 무엇을 누르는지 중심으로 다시 구성
- `completed` current candidate compare-prefill contract audit and summary expansion
  - registry -> compare prefill 경로에서 핵심 strict-annual 값이 어긋나지 않는지 점검
  - summary table에 `Weighting Contract`, `Risk-Off Contract`를 추가해 loaded contract를 더 직접적으로 보이게 정리
- `completed` strict annual shadow sample contract parity bugfix
  - manual validation 중 `rejected_slot_handling_mode` 인자 mismatch를 발견
  - quality / value / quality+value strict annual shadow sample entrypoint가 explicit contract argument를 받도록 정리
- `pending` targeted UI validation
  - current candidate re-entry -> compare
  - compare -> weighted portfolio
  - weighted -> saved portfolio
  - saved portfolio -> replay / edit-in-compare / compare re-entry

## 4. Documentation Sync

- `completed` phase20 kickoff plan 문서 생성
- `completed` phase20 current chapter TODO 문서 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` phase20 first work-unit 문서 생성
  - `PHASE20_CURRENT_CANDIDATE_COMPARE_REENTRY_FIRST_WORK_UNIT.md`
- `completed` phase20 second work-unit 문서 생성
  - `PHASE20_COMPARE_WEIGHTED_AND_SAVED_REENTRY_HARDENING_SECOND_WORK_UNIT.md`
- `completed` phase20 closeout 문서 생성
  - completion summary
  - next phase preparation
  - test checklist
