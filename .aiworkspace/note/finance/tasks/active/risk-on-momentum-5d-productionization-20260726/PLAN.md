# Risk-On Momentum 5D Productionization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

State: active
Last Updated: 2026-07-26

## Goal

`Risk-On Momentum 5D`를 계산 정확성, 2년 실행 성능, Daily Swing 검증 계약,
Level2 / Final Review / Portfolio Monitoring 경계까지 단계적으로 마무리해
Backtest catalog의 `개발 중` 상태를 근거 있게 종료한다.

## 이걸 하는 이유?

현재 전략 V1/V2의 scanner, D+1 execution, exit, macro mode, comparison, history와
Swing Detail은 구현되어 있다. 그러나 기본 Top1000 2년 실행은 같은 전체 시뮬레이션을
최대 57회 반복하고, 각 실행이 전체 일별 universe row를 Python 객체로 다시 변환해
실사용이 어렵다. 또한 Daily Swing 전용 validation, selected-route, monitoring
governance가 deferred라 catalog가 Level2 인계를 차단한다.

## 전체 Roadmap

### 1차 — Core runtime productionization

- 목적: 결과 의미를 보존하면서 2년 실행을 실사용 가능한 시간으로 줄인다.
- 주요 범위:
  - `finance/swing.py`
  - `finance/swing_analysis.py`
  - `app/runtime/backtest/runners/risk_on_momentum.py`
  - Single Strategy settings schema와 focused tests
- 완료 조건:
  - 기존 synthetic 거래 / 잔고 결과 parity
  - full-universe per-day `iterrows()` 제거
  - prepared date/index data 재사용
  - 중복 variant 실행 제거
  - 빠른 / 표준 / 정밀 검증 강도와 실제 실행 횟수 계약
  - 같은 장비 Top1000 2년 기본 실행 60초 이내

### 2차 — Daily Swing validation handoff

- 목적: raw artifact를 그대로 승격하지 않고 Level2가 읽을 compact evidence를 만든다.
- 주요 범위:
  - Daily Swing validation service/read model
  - Backtest result metadata와 candidate source handoff
  - Practical Validation module / focused tests
- 완료 조건:
  - trade count, holding period, turnover, cost/slippage, macro mode,
    failed-trade quality, benchmark/random comparison을 compact evidence로 전달
  - current-universe / PIT membership / delisting 한계를 명시적으로 판정
  - insufficient evidence는 fail-closed
  - 사용자의 명시적 action 전에는 registry를 쓰지 않음

### 3차 — Maturity and downstream governance closeout

- 목적: Daily Swing에 맞는 수동 검토 정책을 연결한 뒤 `개발 중`을 종료한다.
- 주요 범위:
  - strategy catalog maturity
  - Final Review selected-route policy
  - Portfolio Monitoring daily review / stale signal policy
  - durable docs와 Browser QA
- 완료 조건:
  - Level2 / Final Review 경로가 Daily Swing evidence를 해석
  - monitoring은 수동 review, expiry/stale, no-auto-order 경계를 유지
  - production 분류와 visible copy가 실제 gate 상태와 일치
  - focused/full feasible tests, browser interaction QA, docs sync, coherent commit

## Global Constraints

- 현재 사용자 요청은 위 1차~3차 전체다. 1차만 끝내고 전체 완료로 말하지 않는다.
- point-in-time correctness, look-ahead bias, survivorship bias를 숨기지 않는다.
- current-universe historical result는 PIT membership 근거와 같은 것으로 취급하지 않는다.
- UI에서 provider를 직접 조회하지 않는다.
- raw trade/scanner artifact를 registry payload로 복제하지 않는다.
- Final Review와 Portfolio Monitoring은 live approval, broker order, auto rebalance가 아니다.
- 기존 registry / saved / run history / generated QA artifact는 명시 요청 없이 stage하지 않는다.
- 사용자가 만든 dirty worktree 파일은 수정하거나 되돌리지 않는다.

## Implementation Tasks

### Task 1 — Prepared simulation contract와 결과 parity

**Files**

- Modify: `finance/swing.py`
- Test: `tests/test_service_contracts.py` (`RiskOnMomentumSwingContractTests`)

**Red**

1. 동일 fixture를 기존 `prepared_features` 경로와 새 prepared simulation 경로로 실행한다.
2. `result_df`, `trade_log_df`, `scanner_df`, `metrics`가 동일한지 검증한다.
3. prepared object의 날짜별 frame이 `symbol` index와 거래일 position map을 갖는지 검증한다.

**Green**

1. `PreparedSwingSimulationData` dataclass와
   `prepare_swing_simulation_data(features, config)`를 추가한다.
2. 날짜 정규화, ATR column, 날짜별 symbol-indexed frame, date position을 한 번만 만든다.
3. `run_risk_on_momentum_backtest(..., prepared_simulation=None)`가 새 object를 재사용한다.
4. 보유 거래일 수 계산을 전체 날짜 scan에서 date-position 차이로 바꾼다.
5. 일별 전체 universe `iterrows() -> dict(row)` 변환을 제거하고,
   보유/주문 symbol만 indexed frame에서 조회한다.

**Verify**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.RiskOnMomentumSwingContractTests
```

### Task 2 — Variant cache와 분석 강도 계약

**Files**

- Modify: `finance/swing_analysis.py`
- Modify: `app/runtime/backtest/runners/risk_on_momentum.py`
- Modify: `app/services/backtest_execution.py`
- Test: `tests/test_service_contracts.py`

**Red**

1. `quick`, `standard`, `deep`, `custom_legacy`의 해석 결과를 검증한다.
2. standard가 random 10 / comparison on / sensitivity off인지 검증한다.
3. 같은 config를 macro-off와 comparison이 요청할 때 simulation runner가 한 번만 호출되는지 검증한다.
4. random seed가 다른 random run은 cache에서 합쳐지지 않는지 검증한다.

**Green**

1. `SwingAnalysisControls`와 `resolve_swing_analysis_controls()`를 추가한다.
2. runner에 `analysis_intensity: str | None`을 추가한다.
3. 새 UI payload의 기본은 `standard`; field가 없는 history/replay payload는
   기존 explicit random/comparison/sensitivity 값을 보존하는 `custom_legacy`로 해석한다.
4. 한 runtime run 안에서 prepared simulation을 공유하고,
   config fingerprint 기반 variant result cache를 사용한다.
5. macro-off 결과를 comparison suite가 재사용하고 primary와 동일한 variant도 재사용한다.
6. meta에 intensity, planned/executed/cache-hit simulation count를 기록한다.

**Verify**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.RiskOnMomentumSwingContractTests
```

### Task 3 — Single Strategy 설정과 history 호환

**Files**

- Modify: `app/services/backtest_single_settings_workspace.py`
- Modify: `app/web/backtest_single_forms/risk_on_momentum.py`
- Modify: `app/web/backtest_history_helpers.py`
- Test: `tests/test_service_contracts.py`
- Test: `tests/test_backtest_single_settings_workspace.py`

**Red**

1. 현재 Single Strategy schema가 `analysis_intensity=standard`를 기본 전송하는지 검증한다.
2. Quick / Standard / Deep option 설명에 실제 실행 범위가 표시되는지 검증한다.
3. legacy history payload의 explicit controls와 새 intensity가 모두 복원되는지 검증한다.

**Green**

1. 현재 schema의 세 고급 진단 control을 하나의 `분석 강도` single-select로 교체한다.
2. scanner 저장 수는 독립 control로 유지한다.
3. legacy form도 같은 preset을 전송하되, history에 intensity가 없으면 기존 세 값을 보존한다.
4. execution dispatcher가 `analysis_intensity`를 runtime으로 전달한다.

**Verify**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.RiskOnMomentumSwingContractTests
```

### Task 4 — Compact Daily Swing evidence packet

**Files**

- Create: `app/runtime/backtest/runners/risk_on_momentum_evidence.py`
- Modify: `app/runtime/backtest/runners/risk_on_momentum.py`
- Test: `tests/test_backtest_risk_on_governance.py`

**Red**

1. packet이 JSON-safe이며 DataFrame/raw trade/scanner를 포함하지 않는지 검증한다.
2. 전략/기간/universe, trade count, holding, turnover, cost/slippage,
   macro, benchmark/random, quality warning, PIT/survivorship limitation을 검증한다.
3. current membership universe가 `pit_membership_verified=false`와 review blocker를 내는지 검증한다.

**Green**

1. `build_daily_swing_evidence_packet()` pure helper를 추가한다.
2. runner artifact 생성 뒤 bundle top-level과 meta에 compact packet을 연결한다.
3. raw trade/scanner는 기존 generated artifact에만 유지한다.

**Verify**

```bash
.venv/bin/python -m unittest tests.test_backtest_risk_on_governance
```

### Task 5 — Candidate source와 actual replay handoff

**Files**

- Modify: `app/services/backtest_practical_validation_source.py`
- Modify: `app/services/backtest_practical_validation_replay.py`
- Test: `tests/test_backtest_risk_on_governance.py`

**Red**

1. candidate source가 compact packet을 top-level/replay contract에 보존하는지 검증한다.
2. Risk-On replay가 기존 runtime으로 실행되고 Daily Swing evidence를 반환하는지 검증한다.
3. replay는 명시적 사용자 action 전 registry write를 수행하지 않는지 boundary를 검증한다.

**Green**

1. source builder에 `daily_swing_evidence_snapshot`을 추가한다.
2. replay dispatcher에 `risk_on_momentum_5d` branch를 추가한다.
3. replay preview에 universe, holding/exit, macro, intensity를 포함한다.
4. PV replay는 `quick` intensity로 primary curve/evidence만 새로 계산하고,
   저장 source의 deep research evidence를 원본 snapshot으로 구분한다.

**Verify**

```bash
.venv/bin/python -m unittest tests.test_backtest_risk_on_governance
```

### Task 6 — Daily Swing Practical Validation module

**Files**

- Create: `app/services/backtest_daily_swing_validation.py`
- Modify: `app/services/backtest_practical_validation_diagnostics.py`
- Modify: `app/services/backtest_practical_validation_modules.py`
- Test: `tests/test_backtest_risk_on_governance.py`

**Red**

1. Risk-On source trait가 `is_daily_swing=true`, `is_etf_like=false`인지 검증한다.
2. evidence 없음은 `NOT_RUN/NEEDS_INPUT`, current membership는 `REVIEW`,
   PIT membership 확인 evidence는 `PASS`가 되는지 검증한다.
3. Daily Swing module이 required이며 missing evidence에서 fail-closed인지 검증한다.

**Green**

1. compact packet을 trade execution / cost / robustness /
   universe bias / artifact boundary row로 판정하는 pure service를 추가한다.
2. diagnostics result에 `daily_swing_validation`과 display rows를 연결한다.
3. module plan에 strategy-specific required module을 추가하고 Final Review gate에 포함한다.
4. ETF provider module은 Daily Swing stock universe에 적용하지 않는다.

**Verify**

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_risk_on_governance \
  tests.test_service_contracts.PracticalValidationServiceContractTests
```

### Task 7 — Final Review selected-route와 Monitoring policy

**Files**

- Create: `app/services/backtest_daily_swing_policy.py`
- Modify: `app/services/backtest_final_review_policy.py`
- Modify: `app/services/backtest_evidence_read_model.py`
- Modify: `app/services/portfolio_monitoring/catalog.py`
- Test: `tests/test_backtest_risk_on_governance.py`

**Red**

1. Daily Swing validation missing/block 상태에서 selected route가 차단되는지 검증한다.
2. REVIEW limitation은 operator acknowledgement/monitoring condition으로 전달되는지 검증한다.
3. monitoring candidate에 daily review cadence, stale-after 1 market day,
   manual recheck, no-auto-order/no-auto-rebalance가 포함되는지 검증한다.

**Green**

1. validation에서 Daily Swing selected-route/monitoring policy snapshot을 만드는 pure helper를 추가한다.
2. Practical Validation selected-route preflight와 Final Review packet 해석에 해당 policy를 합성한다.
3. Monitoring catalog row에 policy metadata를 노출하되 자동 signal/order를 만들지 않는다.

**Verify**

```bash
.venv/bin/python -m unittest tests.test_backtest_risk_on_governance
```

### Task 8 — Maturity 승격과 governance closeout

**Files**

- Modify: `app/services/backtest_risk_on_governance.py`
- Modify: `app/services/backtest_strategy_catalog.py`
- Modify: `app/services/backtest_analysis_result_workspace.py` if gate copy requires alignment
- Test: `tests/test_backtest_risk_on_governance.py`
- Test: `tests/test_service_contracts.py`

**Red**

1. governance required modules가 모두 implemented/available인지 검증한다.
2. catalog maturity가 production이고 Level2 handoff가 허용되는지 검증한다.
3. catalog visible copy가 더 이상 개발 중으로 표시되지 않는지 검증한다.

**Green**

1. governance read model을 구현된 Daily Swing contract로 갱신한다.
2. maturity를 production으로 승격한다.
3. 정적 maturity gate와 visible label/copy를 실제 상태에 맞춘다.

**Verify**

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_risk_on_governance \
  tests.test_service_contracts.RiskOnMomentumSwingContractTests
```

### Task 9 — 성능, Browser QA, 문서 동기화

**Files**

- Modify: active task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: applicable durable Backtest architecture/flow docs selected by `finance-doc-sync`
- Do not commit: generated browser screenshot and runtime artifacts

**Verify**

1. focused unit/contract tests와 `git diff --check`를 실행한다.
2. 동일 DB/장비 Top1000 2년 Standard를 두 번 실행하고 warm run wall-clock,
   planned/executed/cache-hit count, 결과 요약을 기록한다.
3. 목표 60초를 넘으면 profile을 재실행하고 남은 병목을 해결하거나
   정확한 blocker/restart condition을 남긴다.
4. Backtest 탭에서 Risk-On 선택 → Standard 확인 → 2년 실행 →
   결과/Swing Detail → Level2 handoff를 Browser QA하고 스크린샷 1장을 남긴다.
5. production label, Daily Swing module, manual/stale/no-auto-order boundary를 확인한다.

```bash
.venv/bin/python -m unittest \
  tests.test_backtest_risk_on_governance \
  tests.test_service_contracts.RiskOnMomentumSwingContractTests \
  tests.test_service_contracts.PracticalValidationServiceContractTests
git diff --check
git status --short
```

**Closeout**

1. `finance-doc-sync`로 canonical doc trigger를 판정한다.
2. task status를 `complete` 또는 정확한 `blocked` 상태로 갱신한다.
3. dirty registry/saved/run history/generated artifacts를 제외하고 coherent commit을 만든다.

## Stop Condition

- 1차~3차 완료 조건을 모두 충족하고 검증 결과를 task 문서에 기록한다.
- 외부 데이터 또는 승인 정책 때문에 production 승격이 불가능하면 구현 가능한 범위를
  완료한 뒤 정확한 blocker와 재개 조건을 `RISKS.md` / `STATUS.md`에 남긴다.
