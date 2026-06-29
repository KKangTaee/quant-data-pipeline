# Feature Candidates

Status: Active
Last Verified: 2026-06-08

Scoring: 1 low, 5 high.

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Now | Strategy Evidence Inventory / Direction Panel | 5 | 2 | 2 | 5 | 5 | 3차 첫 구현 후보 |
| Now | Strict Annual + GTAA / EW Portfolio Bridge Handoff | 5 | 3 | 3 | 4 | 5 | 첫 구현 범위에 포함 가능 |
| Next | Risk-On Momentum 5D Governance Design | 5 | 4 | 4 | 4 | 5 | 별도 승인 scope |
| Next | ETF Strategy Evidence Expansion | 4 | 3 | 3 | 3 | 4 | GRS / Risk Parity / Dual Momentum 순차 보강 |
| Later | Quarterly Prototype Maturation | 3 | 4 | 4 | 3 | 3 | replay / validation maturity 이후 |
| Parking | New Strategy Discovery Engine | 3 | 5 | 5 | 2 | 2 | 현재는 보류 |

## Now. Strategy Evidence Inventory / Direction Panel

Goal:

- Backtest 전략별 성숙도, evidence 상태, next action을 한 화면 또는 report로 보여준다.
- 후보 사용자가 "실행 가능"과 "검증 / monitoring 가능"을 구분하게 한다.

Evidence:

- Audit: strategy catalog와 dispatch는 넓지만 후보 evidence는 uneven하다.
- Internal benchmark: strict annual / GTAA / EW는 current anchor가 있고, GRS / quarterly / Risk-On은 maturity gap이 남아 있다.

Dependencies:

- `app/web/backtest_strategy_catalog.py`
- `app/services/backtest_result_read_model.py` 또는 별도 Streamlit-free read model
- 기존 strategy report / docs 링크

Success criteria:

- 전략별 runtime / replay / validation / monitoring readiness가 표로 보인다.
- Risk-On Momentum과 quarterly prototype이 Final Review-ready처럼 보이지 않는다.
- 새 registry / saved JSONL write 없이 read-only로 동작한다.

## Now. Strict Annual + GTAA / EW Portfolio Bridge Handoff

Goal:

- 현재 가장 evidence가 강한 strict annual 3종과 GTAA / Equal Weight ETF sleeve를 다음 development session의 첫 portfolio bridge 후보로 고정한다.
- 단일 strategy winner가 아니라 component role / weakness / required validation을 같이 보여준다.

Evidence:

- Audit: strict annual family는 current candidate one-pager와 integrated validation rerun 기록이 있다.
- Internal benchmark: GTAA와 Equal Weight는 단독보다 mix / sleeve 관점에서 의미가 크다.

Dependencies:

- weighted portfolio replay evidence
- Practical Validation source builder
- component role / weight audit

Success criteria:

- 3차 세션이 "어떤 전략부터 구현하나"를 다시 묻지 않고 strict annual + GTAA/EW bridge를 열 수 있다.
- component role, target weight, expected evidence gap이 명확하다.

## Next. Risk-On Momentum 5D Governance Design

Goal:

- Risk-On Momentum 5D를 Backtest Analysis research lane에서 Practical Validation / Final Review / Portfolio Monitoring으로 넘길지 설계한다.

Evidence:

- Roadmap: Risk-On Momentum governance는 deferred decision.
- Code: `finance/swing.py`, `finance/swing_analysis.py`, `app/runtime/backtest_risk_on_momentum.py`가 already mature research evidence를 만든다.

Dependencies:

- Daily Swing Practical Validation module definition
- daily signal review cadence
- artifact / trade log storage boundary

Success criteria:

- daily swing result가 monthly/annual candidate와 같은 gate를 억지로 공유하지 않는다.
- monitoring signal이 아니라 review evidence로 시작한다.

## Next. ETF Strategy Evidence Expansion

Goal:

- Global Relative Strength, Risk Parity Trend, Dual Momentum의 current candidate / weakness / replay gap을 GTAA 수준에 가깝게 정리한다.

Evidence:

- GRS는 core/runtime/UI replay smoke가 있지만 current candidate hub가 부족하다.
- Risk Parity / Dual Momentum은 strategy catalog에 있으나 durable report가 부족하다.

Dependencies:

- DB-backed smoke / rerun matrix
- strategy hub and report index update
- ETF operability / cost evidence

Success criteria:

- 세 전략 각각에 "current anchor / near miss / not ready reason"이 생긴다.

## Later. Quarterly Prototype Maturation

Goal:

- quarterly strict family를 prototype에서 candidate lifecycle으로 올릴 수 있는지 판단한다.

Evidence:

- quarterly runtime smoke는 contract meta 보존만 확인했다.
- Candidate Library replay는 strict annual 중심이다.

Dependencies:

- quarterly replay support
- history / saved replay manual QA
- PIT / filing lag evidence review

Success criteria:

- quarterly strategy가 prototype label 없이 후보로 읽혀도 되는지 판단할 수 있다.

## Parking Lot

- New strategy discovery engine
- live allocation / broker integration
- auto rebalance
- external commercial product benchmarking
- AI-generated investment recommendation

## Decision Checkpoint

3차 구현 세션을 열기 전 사용자가 결정할 항목:

- 첫 scope를 `Strategy Evidence Inventory / Direction Panel`로 할지
- 아니면 바로 `Strict Annual + GTAA/EW Portfolio Bridge` 구현으로 들어갈지
- Risk-On Momentum governance를 이번 cycle에 포함할지 별도 cycle로 둘지
