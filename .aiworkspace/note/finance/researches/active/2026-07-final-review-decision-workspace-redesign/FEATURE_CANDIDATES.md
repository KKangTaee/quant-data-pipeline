# Feature Candidates

Status: Approved build decomposition
Last Updated: 2026-07-16

Scoring: 1 low, 5 high.

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P0 | Decision Brief pure service와 schema | 5 | 4 | 3 | 5 | 5 | 1차 구현 |
| P0 | Portfolio behavior board와 strength/weakness projection | 5 | 4 | 3 | 4 | 5 | 2차 구현 |
| P0 | React-first Decision Workspace | 5 | 5 | 3 | 5 | 5 | 3차 구현 |
| P1 | 저장 route 호환, fallback, Browser QA, docs | 4 | 3 | 2 | 5 | 5 | 4차 구현 |

## P0. Decision Brief Contract

Goal:

- Final Review가 필요한 정보만 만드는 `decision_brief_v1` pure read model을 도입한다.
- 기존 Gate, root dedup, canonical route, append-only persistence를 보존한다.

Evidence:

- Audit: 현재 read model은 validation contract inspector 역할과 decision report 역할을 함께 맡는다.
- Benchmark: Market Context는 하나의 질문을 위한 React-first projection으로 정보량을 제어한다.

Dependencies:

- stored Practical Validation result
- evidence closure / investability packet
- backtest performance, benchmark, drawdown, construction, realism observations

Success criteria:

- eligible 후보의 unresolved actionable / critical engineering / missing contract는 0이다.
- overall investment score와 3종 headline score를 새 payload에서 제거한다.
- 같은 root issue 또는 measured observation을 strength, weakness, trigger에 중복 반영하지 않는다.

## P0. Portfolio Behavior Board

Goal:

- 누적 net performance와 benchmark, underwater drawdown, 집중도·turnover·비용을 실제 투자 행동으로 해석한다.
- 관측값 기반 포트폴리오 성격 지도를 보조 visual로 제공한다.

Success criteria:

- 강점과 약점마다 `evidence_refs`가 있다.
- chart 또는 trait axis는 measured observation 없이 생성되지 않는다.
- trait map은 우열 점수나 overall score를 만들지 않는다.

## P0. React Decision Workspace

Goal:

- 후보 선택부터 최종 판단 intent까지 하나의 React surface로 통합한다.
- `결론 -> 행동 근거 -> 강점/약점 -> 변화 조건 -> 판단` 순서를 유지한다.

Success criteria:

- Streamlit Decision Desk와 React report가 별도 화면처럼 중복되지 않는다.
- Level2 종결 근거와 provenance는 접힌 disclosure에서만 보인다.
- desktop과 narrow viewport에서 primary decision이 같은 순서로 읽힌다.

## P1. Persistence And QA Closure

Goal:

- 새 한글 label을 기존 canonical route에 매핑하고 save-and-move guard, current-session guard, Monitoring handoff를 보존한다.

Success criteria:

- 기존 registry row를 재작성하지 않는다.
- stale candidate, duplicate decision, payload mismatch는 Python save gate에서 차단한다.
- focused tests, GRS runtime regression, React production build, Browser QA, docs sync를 통과한다.

## Parking Lot

- 현재 시점의 실제 투자 적합성 또는 매수 타이밍 판단
- account-specific tax / minimum order / allocation approval
- live broker order, account sync, auto rebalance
- 신규 historical universe / delisting provider
- React에서 Gate, classification, trait normalization 또는 persistence 계산
