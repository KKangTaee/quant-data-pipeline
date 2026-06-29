# Strategy Weakness Matrix

Status: Active
Last Verified: 2026-06-08

## Purpose

이 문서는 전략별 장점, 단점, 약점, 개선 방향을 한 번에 보기 위한 2차 산출물이다.
여기서 말하는 개선은 투자 추천이 아니라 제품 evidence와 workflow maturity 개선이다.

## Matrix

| Strategy | Strength | Weakness | Data / validation risk | Improvement direction | Priority |
| --- | --- | --- | --- | --- | --- |
| Equal Weight | 이해 쉽고 portfolio sleeve로 유용 | 단독 alpha / low-MDD gate가 약함 | ETF operability / cost / concentration evidence 필요 | GTAA와 mix role로 명확화, standalone winner처럼 표현하지 않기 | Medium |
| GTAA | ETF 계열 중 evidence와 후보가 가장 성숙 | universe / interval / score horizon 민감, paper_only 성격 | sampled benchmark 해석, cadence alignment | strict annual과 함께 defensive/tactical sleeve로 bridge | High |
| Global Relative Strength | price-only relative strength로 명확하고 replay 연결됨 | current candidate / strategy hub 부족 | price freshness, excluded ticker, cash proxy handling | ETF evidence expansion 1순위 후보 | Medium |
| Risk Parity Trend | defensive allocation concept가 뚜렷함 | current anchor와 report 부족, low-vol overweight 가능 | volatility window, correlation regime, stale ETF data | rerun matrix와 strategy hub 먼저 작성 | Medium-low |
| Dual Momentum | 단순하고 설명 쉬운 tactical switch | top-1 집중, whipsaw, trend 전환 취약 | cash proxy / benchmark / guardrail evidence | concentrated momentum risk를 explicit evidence로 만들기 | Medium-low |
| Risk-On Momentum 5D | research evidence, trade log, macro comparison이 강함 | validation / final review / monitoring governance 없음 | generated artifact boundary, daily signal interpretation, survivorship / universe assumptions | Daily Swing governance design을 별도 scope로 열기 | High but separate |
| Quality Strict Annual | quality-only reference family, 구조 조정으로 rescue됨 | factor만으로는 약하고 benchmark / overlay 의존 | PIT statement, liquidity, benchmark contract | quality role을 reference / stabilizer로 명확화 | High |
| Value Strict Annual | raw return 가장 강한 축 | MDD 부담, lower-MDD rescue는 gate 약화 | drawdown, underperformance, liquidity, concentration | current anchor 유지 + downside alternative를 open review로 관리 | High |
| Quality + Value Strict Annual | blended practical family 중 가장 잘 정리됨 | still review_required / small_capital_trial | capacity, concentration, factor overlap, drawdown | first portfolio bridge core candidate로 사용 | High |
| Strict Quarterly Prototypes | runtime contract와 meta 보존 확인 | investment evidence / replay / validation maturity 부족 | filing lag, PIT quarterly rows, candidate lifecycle | prototype label 유지, later maturation task로 분리 | Later |

## Cross-Strategy Weaknesses

### 1. Evidence maturity mismatch

전략 실행 가능성과 후보 maturity가 일치하지 않는다.
따라서 3차 첫 구현은 strategy maturity를 제품 표면에 보이게 해야 한다.

### 2. Report depth mismatch

Strict annual / GTAA / Equal Weight는 durable reports가 있지만 GRS / Risk Parity / Dual Momentum은 부족하다.
ETF family 확장은 "실행 기능"이 아니라 "current candidate evidence"를 만드는 일부터 시작해야 한다.

### 3. Governance mismatch

Risk-On Momentum 5D는 daily swing 전략이라 monthly / annual candidate workflow와 다르다.
Practical Validation / Final Review에 붙이려면 별도 module과 daily review policy가 필요하다.

### 4. Prototype labeling risk

Quarterly prototype은 실행된다는 이유만으로 annual strict와 같은 신뢰도로 보여주면 안 된다.
UI / report에서 prototype label과 missing evidence를 유지해야 한다.

## Improvement Guide

| 개선 방향 | 먼저 할 일 | 하지 말 일 |
| --- | --- | --- |
| Strategy maturity 정렬 | read-only inventory / direction panel | registry rewrite |
| Strict annual + ETF bridge | component role / weight / validation gap 표시 | winner-only ranking |
| Risk-On governance | Daily Swing validation module 설계 | 바로 monitoring signal화 |
| ETF evidence expansion | GRS, Risk Parity, Dual Momentum current anchor search | 새 ETF strategy 추가 |
| Quarterly maturation | replay / PIT / filing lag evidence 확인 | prototype label 제거 |
