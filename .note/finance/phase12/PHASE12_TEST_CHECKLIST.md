# Phase 12 Test Checklist

## 목적

- Phase 12에서 hardening한 전략들이
  단순 prototype / runnable surface를 넘어서
  real-money candidate contract로 읽히는지 확인한다.
- 이 checklist는 immediate smoke가 아니라
  **Phase 12 구현 이후 manual review용** 문서다.

## 1. Strategy Classification Disclosure

- 문서와 UI 설명에서 현재 전략군이
  - production-priority
  - baseline / reference
  - research-only
  로 혼동 없이 읽히는지 확인
- quarterly strict prototype family가 여전히 hold / research-only로 읽히는지 확인

## 2. ETF Strategy Real-Money Contract

- `GTAA`, `Dual Momentum`, `Risk Parity Trend`에 대해
  아래가 current surface에 반영되는지 확인
  - universe/data contract
  - investability filter
  - turnover / cost assumption
  - benchmark / drawdown readout
  - caution wording

구체 확인:
- `Single Strategy` form에
  - `Minimum Price`
  - `Transaction Cost (bps)`
  - `Benchmark Ticker`
  가 보이는지
- `GTAA` form에 추가로
  - `Score Horizons`
  - 기본 선택 `1M / 3M / 6M / 12M`
  - 가중치 입력 없이 선택된 horizon이 동일 비중으로 처리되는지
  - `Trend Filter Window`
  - `Fallback Mode`
  - `Defensive Tickers`
  - `Market Regime Overlay`
  - `Crash Guardrail`
  가 보이는지
- `Compare`의 `GTAA` block에도 같은 계약 값들이 override 가능하게 보이는지
- 실행 후 `Real-Money` 탭에서
  - gross / net / turnover / cost
  - strategy net vs benchmark overlay
  를 읽을 수 있는지
- `Result Table`에
  - `Gross Total Balance`
  - `Gross Total Return`
  - `Turnover`
  - `Estimated Cost`
  - `Cumulative Estimated Cost`
  - `Net Total Balance`
  - `Net Total Return`
  이 보이는지
- `GTAA` 실행 결과의 `Result Table`에
  - `Defensive Fallback Count`
  - `Regime State`
  - `Crash Guardrail Triggered`
  - `Risk-Off Reason`
  이 보여서
  "왜 그 달에 현금 또는 방어자산 쪽으로 움직였는지"를 읽을 수 있는지
- `Meta`에
  - `Minimum Price`
  - `Transaction Cost`
  - `Benchmark`
  - `Average Turnover`
  - `Estimated Cost Total`
  이 보이는지
- `GTAA`의 `Meta` 또는 `Runtime Metadata`에
  - `score_weights`
  - `risk_off_mode`
  - `defensive_tickers`
  - `market_regime_enabled`
  - `market_regime_window`
  - `market_regime_benchmark`
  - `crash_guardrail_enabled`
  - `crash_guardrail_drawdown_threshold`
  - `crash_guardrail_lookback_months`
  이 남는지

## 3. Strict Annual Family Promotion Surface

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

에 대해 아래가 확인되는지 본다.

- dynamic PIT contract를 실전형 validation 기준으로 읽을 수 있는지
- investability / stale / delisted handling rule이 읽히는지
- turnover / cost surface가 추가되었는지
- benchmark / drawdown / guardrail 정보가 보이는지

현재 상태 설명:
- 이 항목은 **이번 ETF first pass에서 아직 구현되지 않은 다음 작업 대상**이다.
- 그래서 지금 테스트 시점에 strict annual 화면에서
  - turnover / cost
  - benchmark
  - guardrail
  정보가 안 보이는 것은 현재로서는 **정상**이다.
- 여기서는 "이미 구현됐는지"를 확인하는 항목이 아니라,
  다음 strict annual hardening 작업 전에 baseline을 확인하는 항목으로 읽는 편이 맞다.

## 4. Static vs Dynamic Contract Boundary

- `Static Managed Research Universe`와
  `Historical Dynamic PIT Universe`가 혼동되지 않는지 확인
- 실전 판단은 dynamic contract 쪽을 우선해야 한다는 방향이
  과장 없이 읽히는지 확인

## 5. Quarterly Hold Rule

- quarterly strict prototype family가
  실전형으로 승격된 것처럼 보이지 않는지 확인
- hold rule과 future promotion 조건이 문서와 충돌하지 않는지 확인

## 6. Cost / Turnover / Guardrail Readout

- real-money candidate로 승격되는 전략들에 대해
  - turnover
  - cost assumption
  - rebalance impact
  - portfolio guardrail
  이 결과 표면에서 읽히는지 확인

현재 구현 범위:
- turnover / cost / rebalance impact는 ETF 전략군 first pass에서 구현됨
- stronger portfolio guardrail은 아직 later pass

## 7. Benchmark / Drawdown Validation

- 수익률 외에도
  - benchmark 비교
  - max drawdown
  - rolling underperformance
  가 전략 판단에 충분한 수준으로 보이는지 확인

현재 구현 범위:
- benchmark 비교는 ETF 전략군 first pass에서 구현됨
- drawdown은 기존 summary / compare surface로 읽음
- rolling underperformance는 아직 later pass

## 8. History / Metadata / Handoff

- real-money candidate 관련 실행이 history에 남을 때
  universe/data contract와 hardening context를 다시 읽을 수 있는지 확인
- history / meta / documentation이 promotion 상태와 충돌하지 않는지 확인

구체 확인:
- `Load Into Form`
- `Run Again`
- compare override
- saved portfolio compare context

에서 아래 값이 유지되는지 확인
- `min_price_filter`
- `transaction_cost_bps`
- `benchmark_ticker`
- `score_weights`
- `risk_off_mode`
- `defensive_tickers`
- `market_regime_enabled`
- `market_regime_window`
- `market_regime_benchmark`
- `crash_guardrail_enabled`
- `crash_guardrail_drawdown_threshold`
- `crash_guardrail_lookback_months`

## closeout 판단 기준

아래가 만족되면 Phase 12는 practical closeout 후보로 볼 수 있다.

1. production-priority 전략군이 명확하다
2. ETF 전략군이 first hardening을 통과했다
3. strict annual family가 next-level candidate로 읽힌다
4. quarterly hold rule이 유지된다
5. 결과 surface가 “실전형 전략 판단”에 필요한 최소 계약을 보여준다
