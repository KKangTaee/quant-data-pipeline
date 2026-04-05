# Phase 12 Current Chapter TODO

## 상태 기준

- `pending`
- `in_progress`
- `completed`

## 1. Chapter Setup

- `completed` Phase 12 상위 계획 문서 작성
  - `PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md`
- `completed` Phase 12 active phase 전환
  - 실전 전략 승격을 다음 최우선 workstream으로 고정
- `completed` current strategy family 재분류 방향 고정
  - production-priority
  - baseline/reference
  - research-only

## 2. Strategy Production Audit

- `completed` 전략군 audit matrix first pass 작성
  - `PHASE12_STRATEGY_PRODUCTION_AUDIT_MATRIX.md`
- `completed` promotion 우선순위 first pass 고정
  - ETF 전략군 먼저
  - strict annual family 다음
  - quarterly family hold
- `completed` quarterly family hold rule 명시
  - prototype / research-only 유지

## 3. Real-Money Promotion Contract

- `completed` 공통 promotion contract 초안 작성
  - `PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md`
- `completed` 공통 hardening 축 고정
  - universe / data contract
  - investability filter
  - turnover / transaction cost
  - portfolio guardrail
  - validation surface
- `completed` promotion status language first pass 고정
  - `research-only`
  - `production candidate`
  - `real-money candidate`

## 4. ETF Strategy Hardening

- `completed` ETF 전략군 real-money hardening scope 구체화
  - `GTAA`
  - `Dual Momentum`
  - `Risk Parity Trend`
- `completed` ETF 전략 공통 investability / cost / turnover contract first pass 구현
  - `Minimum Price`
  - `Transaction Cost (bps)`
  - turnover / gross-vs-net result surface
- `completed` ETF 전략 benchmark / turnover readout first pass 보강
  - single-strategy `Real-Money` 탭
  - compare highlight / focused strategy 보강
- `completed` ETF 전략 history / prefill / compare override contract 연결
  - `Load Into Form`
  - `Run Again`
  - compare override
  - saved portfolio compare context
- `completed` ETF 전략 구현 요약 문서 작성
  - `PHASE12_ETF_REAL_MONEY_HARDENING_FIRST_PASS.md`
- `completed` GTAA commodity sleeve comparative analysis
  - `DBC`
  - `PDBC`
  - `No Commodity Sleeve`
  - `PHASE12_GTAA_DBC_PDBC_NO_COMMODITY_ANALYSIS.md`
- `completed` GTAA commodity alternative candidate comparative analysis
  - `CMDY`
  - `BCI`
  - `COMT`
  - `PHASE12_GTAA_COMMODITY_ALTERNATIVE_CANDIDATE_ANALYSIS.md`
- `completed` GTAA interval-1 universe variation search
  - 10 backtests with current and added ETFs
  - `TIP`, `QUAL`, `USMV`, `VEA` backfill included
  - `PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md`
- `completed` GTAA no-DBC interval-1 variation search
  - 10 backtests excluding `DBC`
  - `PDBC`, `COMT`, `CMDY`, `BCI`, `No Commodity` plus `QUAL` / `USMV`
  - `PHASE12_GTAA_NO_DBC_INTERVAL1_VARIATION_SEARCH.md`
- `completed` GTAA preset-refresh UX fix
  - `Preset` 변경 시 `Selected tickers` preview가 바로 갱신되도록
    universe selector를 submit form 밖으로 이동
- `completed` GTAA DB ETF group search under the current default contract
  - DB-backed ETF를 주제별로 묶어 `18`개 조합을 비교
  - 현재 `interval = 2`, `top = 3`, `month_end`, `10 bps` 계약에서
    `QQQ + IAU + XLE` 축이 가장 강한 개선 방향으로 확인됨
  - `PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md`
- `completed` GTAA default signal interval rebase to `1`
  - `Single Strategy`, `Compare`, `History`, `saved portfolio prefill`, sample/runtime fallback 모두 `1`로 정렬
  - interval-1 normalized rerun 기준으로도 `QQQ + IAU + XLE` 축이 가장 강한 additive direction으로 유지됨
  - `PHASE12_GTAA_INTERVAL1_DEFAULT_REBASE_ANALYSIS.md`
- `completed` GTAA preset surface simplification
  - 실험용 preset을 모두 유지하지 않고,
    current default + Phase 12 top-3 candidate preset만 남기도록 정리
  - 유지 preset:
    - `GTAA Universe`
    - `GTAA Universe (No Commodity + QUAL + USMV)`
    - `GTAA Universe (QQQ + XLE + IAU + TIP)`
    - `GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)`
- `completed` GTAA score weight / risk-off contract first pass
  - `1M / 3M / 6M / 12M` score weight를 UI에서 조절 가능
  - `Trend Filter Window`, `Fallback Mode`, `Defensive Tickers`, `Market Regime`, `Crash Guardrail`을 UI에서 조절 가능
  - single / compare / history / prefill 경로까지 왕복 연결
  - `PHASE12_GTAA_SCORE_WEIGHT_AND_RISK_OFF_FIRST_PASS.md`
- `completed` GTAA vs SPY dominance search
  - 목표:
    `SPY`보다 CAGR은 높고 MDD는 더 낮은 GTAA 후보가 존재하는지 확인
  - current Phase 12 tested range에서는 winner `0`
  - closest offensive candidate:
    - `GTAA Universe (QQQ + XLE + IAU + TIP)`
    - `GTAA Universe (QQQ + XLE + IAU)`
    - `Score Horizons = 1/3/6`
  - closest defensive candidate:
    - `GTAA Universe (No Commodity + QUAL + USMV)`
  - `PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md`
- `completed` GTAA practical floor search
  - 목표:
    `CAGR >= 9%` and `MDD >= -16%` 를 동시에 만족하는 GTAA candidate 탐색
  - best candidate:
    - `QQQ|VUG|RSP|VTV|QUAL|USMV|XLE|IAU|TIP|TLT|LQD|ACWV|SPY`
    - `top=2`
    - `interval=2`
    - `Score Horizons = 1/3`
    - `risk-off = cash_only`
  - result:
    - `CAGR 12.90%`
    - `MDD -11.10%`
  - `PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md`
- `completed` GTAA cadence-expanded floor search
  - 목표:
    `CAGR >= 9%` and `MDD >= -16%` 를 만족하는 후보를 더 넓게 찾고
    rebalance cadence 민감도까지 같이 확인
  - total search:
    `180` runs
  - verified preset additions:
    - `GTAA Universe (U3 Commodity Candidate Base)`
    - `GTAA Universe (U1 Offensive Candidate Base)`
    - `GTAA Universe (U5 Smallcap Value Candidate Base)`
  - target hits:
    `88`
  - best offensive candidate:
    - `U3_commodity`
    - `interval=3`
    - `top=2`
    - `horizons=1/3/6`
  - best balanced candidate:
    - `U1_offensive`
    - `interval=3`
    - `top=2`
    - `horizons=1/3/6/12`
  - best defensive candidate:
    - `U5_smallcap_value`
    - `interval=3`
    - `top=3`
    - `horizons=1/3/6/12`
  - `PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md`
- `pending` ETF 전략 second-pass guardrail / underperformance contract
  - rolling underperformance
  - stronger investability proxy
  - richer benchmark contract

## 5. Strict Annual Family Promotion

- `completed` strict annual family hardening scope 확정
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- `completed` strict annual real-money hardening first pass 구현
  - `Minimum Price`
  - `Transaction Cost (bps)`
  - `Benchmark Ticker`
  - single / compare / history prefill contract
  - `PHASE12_STRICT_ANNUAL_REAL_MONEY_HARDENING_FIRST_PASS.md`
- `completed` dynamic PIT 기반 real-money caution / promotion contract first pass 연결
  - annual strict dynamic PIT run도 같은 real-money readout으로 읽을 수 있게 정렬
- `completed` strict annual validation surface second pass 구현
  - benchmark-relative drawdown / rolling underperformance 진단
  - `validation_status = normal / watch / caution`
  - `promotion_decision = real_money_candidate / production_candidate / hold`
  - single / compare / meta surface 반영
  - `PHASE12_STRICT_ANNUAL_VALIDATION_SURFACE_SECOND_PASS.md`
- `completed` strict annual underperformance guardrail first pass 구현
  - optional benchmark-relative trailing excess return rule을 실제 전략 규칙으로 연결
  - trailing excess return이 임계치 아래로 내려가면 해당 rebalance는 cash로 유지
  - single / compare / history / real-money surface까지 contract 연결
  - `PHASE12_STRICT_ANNUAL_UNDERPERFORMANCE_GUARDRAIL_FIRST_PASS.md`
- `completed` strict annual investability / benchmark reinforcement first pass 구현
  - `Minimum History (Months)` 추가
  - `Benchmark CAGR`
  - `Net CAGR Spread`
  - `Benchmark Coverage`
  - single / compare / history / meta surface까지 contract 연결
  - `PHASE12_STRICT_ANNUAL_INVESTABILITY_AND_BENCHMARK_REINFORCEMENT_FIRST_PASS.md`
- `completed` strict annual liquidity proxy later-pass first pass 구현
  - `Min Avg Dollar Volume 20D ($M)` 추가
  - DB 일봉 `close * volume` 기준 trailing 20-day average dollar volume filter
  - single / compare / history / meta surface까지 contract 연결
  - `PHASE12_STRICT_ANNUAL_LIQUIDITY_PROXY_FIRST_PASS.md`
- `completed` strict annual richer benchmark policy / stricter promotion reinforcement later pass 구현
  - `Min Benchmark Coverage (%)`
  - `Min Net CAGR Spread (%)`
  - `benchmark_policy_status = normal / watch / caution / unavailable`
  - promotion decision이 benchmark policy 상태를 함께 반영
  - single / compare / history / meta surface까지 contract 연결
  - `PHASE12_STRICT_ANNUAL_BENCHMARK_POLICY_AND_PROMOTION_REINFORCEMENT_LATER_PASS.md`
- `completed` strict annual liquidity policy / later-pass investability reinforcement 구현
  - `Min Liquidity Clean Coverage (%)`
  - `liquidity_clean_coverage`
  - `liquidity_policy_status = normal / watch / caution / unavailable`
  - promotion decision이 liquidity policy 상태를 함께 반영
  - single / compare / history / meta surface까지 contract 연결
  - `PHASE12_STRICT_ANNUAL_LIQUIDITY_POLICY_AND_PROMOTION_REINFORCEMENT_LATER_PASS.md`
- `completed` backtest strategy surface consolidation first pass 구현
  - 새 `app/web/pages/backtest_strategy_catalog.py`에 family / variant / concrete strategy key 매핑 분리
  - `Single Strategy` top-level 목록을
    - `Quality`
    - `Value`
    - `Quality + Value`
    family 중심으로 정리
  - `Compare & Portfolio Builder`도 같은 family surface를 사용하도록 정리
  - history / `Load Into Form`는 기존 concrete strategy key를 유지하면서 family + variant UI로 복원
  - `PHASE12_BACKTEST_STRATEGY_SURFACE_CONSOLIDATION_FIRST_PASS.md`
- `in_progress` investability / turnover / benchmark / guardrail 보강
  - investability / turnover / benchmark는 first pass 완료
  - validation surface second pass 완료
  - promotion decision reinforcement surface 완료
  - underperformance guardrail actual-rule first pass 완료
  - minimum-history investability proxy와 benchmark spread/coverage first pass도 now 완료
  - 20D average dollar volume liquidity proxy first pass도 now 완료
  - richer benchmark policy / stricter promotion reinforcement later pass도 now 완료
  - liquidity policy / later-pass investability reinforcement도 now 완료
  - broader benchmark contract / broader promotion robustness는 still later pass
- `completed` annual strict promotion checklist baseline refresh
  - `PHASE12_TEST_CHECKLIST.md`에 strict annual real-money surface 항목 반영

## 6. Documentation And Validation

- `completed` Phase 12 test checklist 초안 작성
  - `PHASE12_TEST_CHECKLIST.md`
- `completed` roadmap / index / logs에 Phase 12 반영
- `completed` ETF-first implementation 이후 checklist current code 기준 refresh

## 현재 메모

- Phase 12는 새 전략을 대량 추가하는 phase가 아니다.
- 목적은
  **기존 전략군을 실전 투자 판단에 가까운 계약으로 승격하는 것**
  이다.
- first implementation target은 ETF 전략군이 맞다.
- strict annual family는 Phase 10 dynamic PIT contract 위에서 다음 승격 대상이다.
- quarterly strict prototype family는 current phase에서 여전히 hold가 맞다.
- ETF 전략군은 now `real-money hardening first pass completed` 상태이고,
  strict annual family도 now `real-money hardening first pass completed` 상태다.
- GTAA는 이번 턴에서 더 밀지 않고, 이후 다시 다루기로 정리했다.
- quality/value 전략의 실제 계산 로직은 계속
  - `finance/strategy.py`
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
  에 있고,
  이번 턴에서 정리한 것은 주로 `app/web/pages/backtest.py`의 strategy surface / orchestration 구조다.
- next active implementation target은
  strict annual broader benchmark contract / broader promotion robustness 쪽이다.
- GTAA 쪽에서는 current default contract 기준으로
  `QQQ`, `IAU`, `XLE`가 가장 강한 additive direction으로 보이며,
  `QUAL`, `USMV`는 보조 broadener로 해석하는 편이 맞다.
- 현재 GTAA UI 기본 `Signal Interval`은 `1`로 rebased 되었지만,
  기본 `PDBC` preset 자체의 우위까지 확정된 것은 아니다.
- current Phase 12 tested range 안에서는
  GTAA가 `SPY`를 `CAGR`와 `MDD` 두 축에서 동시에 이기는 dominance candidate를
  아직 찾지 못했다.
- additional targeted search later found a GTAA candidate meeting the practical floor:
  - `CAGR >= 9%`
  - `MDD >= -16%`
- and the strongest verified candidate families are now available as GTAA preset bases in the UI:
  - `U3_commodity`
  - `U1_offensive`
  - `U5_smallcap_value`
- GTAA compare surface also now supports the same universe contract:
  - `Preset` / `Manual`
  - immediate ticker preview refresh
  - history / saved-portfolio prefill restoration
