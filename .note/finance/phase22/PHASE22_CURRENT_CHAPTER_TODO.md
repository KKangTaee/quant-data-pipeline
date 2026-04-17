# Phase 22 Current Chapter TODO

## 상태

- `manual_validation_ready`

## 1. Portfolio-Level Candidate Semantics

- `completed` phase kickoff plan 작성
  - `Phase 21` portfolio bridge 결과를 이어받아
    왜 `Phase 22`가 portfolio-level candidate construction인지 정리
- `completed` 첫 번째 작업 단위 문서화
  - portfolio 후보의 정의
  - component strategy와 portfolio candidate의 차이
  - 후보로 인정하기 위한 최소 기록 항목
  - 유지 / 교체 / 보류 판단 기준
- `completed` glossary sync
  - `Portfolio-Level Candidate`
  - `Portfolio Bridge`
  - `Saved Portfolio Replay`
  - `Date Alignment`

## 2. Representative Portfolio Candidate Pack

- `completed` baseline portfolio candidate pack 확정
  - `Phase 21`의 `Value / Quality / Quality + Value` current anchor 3종을
    Phase 22 baseline portfolio candidate pack으로 다시 정의
- `completed` baseline weight policy 결정
  - saved portfolio definition 기준 `[33.33, 33.33, 33.33]`
  - normalized 기준 `[1/3, 1/3, 1/3]`
  - `Phase 21`의 `33 / 33 / 34` 표현은 near-equal shorthand로 정리하고,
    Phase 22에서는 `equal-third baseline`으로 부르기로 결정
- `completed` portfolio-level benchmark / guardrail interpretation 정리
  - single strategy benchmark와 portfolio benchmark가 어떻게 연결되는지 기록
  - Phase 22 primary portfolio benchmark는 `phase22_annual_strict_equal_third_baseline_v1`
  - `SPY`는 primary gate가 아니라 market context로만 유지
  - component benchmark는 component 품질 해석으로만 유지
  - portfolio-level guardrail은 actual trading rule이 아니라 report-level warning으로 고정

## 3. Portfolio-Level Validation Execution

- `completed` baseline portfolio candidate report 작성
  - `.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md`
  - `phase22_annual_strict_equal_third_baseline_v1`을 baseline 후보 pack으로 등록
- `completed` saved replay evidence 반영
  - `Phase 21` exact replay evidence를 Phase 22 baseline candidate pack의 재현성 근거로 연결
- `completed` weight alternative rerun
  - source bundle
  - date alignment
  - weight
  - result metrics
  - interpretation
- `completed` baseline metric reconciliation
  - `33 / 33 / 34` Phase 21 near-equal result와
    `[33.33, 33.33, 33.33]` Phase 22 official equal-third baseline 수치를 분리
  - Phase 22 weight alternative 비교 기준은
    `phase22_annual_strict_equal_third_baseline_v1` scripted rerun 값으로 고정
- `completed` weight alternative comparison scope 확정
  - `quality_value_tilt`: `25 / 25 / 50`
  - `value_quality_defensive_tilt`: `40 / 40 / 20`
  - broad brute-force search / risk parity / volatility targeting은 이번 work unit 밖으로 defer

## 4. Documentation And QA

- `completed` phase22 plan / TODO / checklist bundle 생성
- `completed` roadmap / doc index / work log / question log sync
- `completed` backtest report index sync
  - Phase 22 archive README와 baseline candidate report를 등록
- `completed` current candidate registry review
  - `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` validate 정상 확인
  - 이번 baseline은 portfolio-level candidate pack 초안이므로 기존 single-strategy registry에는 append하지 않음
  - portfolio-level registry schema가 필요하면 이후 별도 작업으로 정의
- `completed` phase22 checklist first report alignment
  - 실제 report 위치와 확인 항목을 checklist에 반영
- `completed` benchmark / guardrail / weight scope doc sync
  - `PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md`
  - `Portfolio-Level Benchmark`, `Portfolio-Level Guardrail`, `Weight Alternative` glossary 추가
- `completed` phase22 checklist finalization
  - weight alternative / benchmark policy 작업 이후 closeout용 checklist로 다시 정리

## 다음 작업

- `Phase 22`의 다음 작업은
  **사용자가 `PHASE22_TEST_CHECKLIST.md`를 기준으로 manual QA를 진행하고,
  모두 확인되면 Phase 22를 닫을지 diversified component 추가를 한 번 더 볼지 결정하는 것**이다.
