# Phase 12 Completion Summary

## 목적

- Phase 12 `Real-Money Strategy Promotion`을 practical closeout 기준으로 정리한다.
- 이번 phase에서 실제로 무엇이 구현되었고,
  어디까지를 "실전형 승격 준비 완료"로 읽어야 하는지,
  무엇을 다음 phase backlog로 넘기는지 명확히 남긴다.

## 이번 phase에서 실제로 완료된 것

### 1. 전략군 역할 재분류와 promotion contract 고정

- current strategy family를 아래처럼 다시 분류했다.
  - `production-priority`
  - `baseline / reference`
  - `research-only`
- quarterly strict prototype family는 현재도 `research-only hold`로 유지한다.
- 실전형 승격 판단에 필요한 공통 계약을 문서로 고정했다.
  - universe / data contract
  - investability filter
  - turnover / transaction cost
  - portfolio guardrail
  - validation surface

쉬운 뜻:
- 이제 "전략이 있다"와 "실전형 후보다"를 같은 뜻으로 보지 않는다.
- 전략을 실전에 가깝게 해석하려면 어떤 조건이 필요한지 기준이 먼저 생겼다.

### 2. ETF 전략군 real-money hardening first pass

대상:
- `GTAA`
- `Dual Momentum`
- `Risk Parity Trend`

구현 범위:
- `Minimum Price`
- `Transaction Cost (bps)`
- `Benchmark Ticker`
- turnover / gross-vs-net result surface
- compare override / history / prefill / saved strategy context

추가 보강:
- GTAA preset 탐색과 candidate search
- GTAA risk-off / score horizon 조정 surface
- GTAA candidate preset 정리
- ETF current-operability policy first pass
  - `Min ETF AUM ($B)`
  - `Max Bid-Ask Spread (%)`
  - `etf_operability_status = normal / watch / caution / unavailable`

쉬운 뜻:
- ETF 전략군은 이제 단순히 "수익률 곡선이 나온다"를 넘어서,
  비용, 기준선, 현재 ETF 규모/스프레드까지 같이 읽는 전략이 되었다.

### 3. Strict Annual family real-money hardening와 promotion reinforcement

대상:
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

구현 범위:
- `Minimum Price`
- `Minimum History (Months)`
- `Min Avg Dollar Volume 20D ($M)`
- `Transaction Cost (bps)`
- `Benchmark Contract`
- `Benchmark Ticker`
- benchmark-relative validation surface
- underperformance guardrail actual rule
- drawdown guardrail actual rule
- broader benchmark contract
- benchmark / liquidity / validation / guardrail policy statuses
- promotion decision surface

쉬운 뜻:
- strict annual family는 이제 단순 research candidate가 아니라,
  실전 승격 판단에 필요한 review surface를 거의 다 갖춘 상태다.

### 4. Backtest strategy surface 정리

- `Single Strategy`
- `Compare & Portfolio Builder`

의 top-level strategy 목록을 아래 family 중심으로 정리했다.

- `Quality`
- `Value`
- `Quality + Value`

그리고 family 안에서
- `Research`
- `Strict Annual`
- `Strict Quarterly Prototype`

variant를 고르게 만들었다.

쉬운 뜻:
- 사용자는 더 이상 같은 quality/value 전략을 여러 이름으로 찾아다닐 필요가 줄었다.
- 계산 로직을 무리하게 뜯지 않고, surface만 안전하게 정리했다.

## 이번 phase를 practical closeout으로 보는 이유

- ETF 전략군은 first-pass real-money hardening 목표를 달성했다.
- strict annual family는 실전 승격 review에 필요한 validation / guardrail / promotion surface를 갖췄다.
- quarterly family는 무리하게 승격하지 않고 `research-only hold`로 명확히 남겼다.
- strategy surface와 documentation도 현재 구현 상태에 맞춰 정리되었다.

즉 Phase 12의 핵심 목표였던
**"현재 전략군을 실전 투자 판단에 더 가까운 계약으로 승격시키는 일"**
은 practical 기준으로 달성되었다고 보는 것이 맞다.

## 아직 남아 있지만 closeout blocker는 아닌 것

다음 항목들은 가치가 있지만,
현재 Phase 12 closeout을 막는 수준의 blocker는 아니다.

- ETF 전략군 second-pass underperformance / stronger guardrail
- ETF operability point-in-time later pass
- ETF actual trade-blocking rule 여부 검토
- richer benchmark / execution-readiness policy later pass
- strict annual 이후 실제 live/paper deployment 전 probation workflow

쉬운 뜻:
- 더 할 수 있는 일은 남아 있다.
- 하지만 지금은 "승격 기준을 세우고 first-pass를 끝내는 phase"였기 때문에,
  이 항목들은 다음 phase로 넘기는 것이 더 자연스럽다.

## guidance / reference review 결과

Phase closeout 시점에 아래를 다시 확인했다.

- `AGENTS.md`
- finance skill 운용 기준
- `.note/finance/FINANCE_DOC_INDEX.md`
- `.note/finance/MASTER_PHASE_ROADMAP.md`
- Phase 12 문서 세트

결론:
- 이번 closeout에서 추가 workflow 지침 변경은 필요하지 않았다.
- 대신 roadmap / index / progress / analysis log는 현재 상태에 맞게 동기화한다.

## closeout 판단

현재 기준으로:

- code:
  - `completed`
- docs / checklist / roadmap sync:
  - `completed`
- strategy promotion first pass:
  - `completed`
- remaining second-pass hardening:
  - `deferred backlog`

즉 Phase 12는
**practical completion 상태로 닫는 것이 맞다.**
