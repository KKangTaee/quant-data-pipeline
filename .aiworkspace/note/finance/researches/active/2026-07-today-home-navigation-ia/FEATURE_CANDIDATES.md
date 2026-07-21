# Feature Candidates

Status: Design Approved; Implementation Not Started
Last Updated: 2026-07-22

## Summary

현재 Finance Console의 최상위 분류는 `Workspace / Operations / Reference`라는 서로 다른 기준을 섞고 있다.
사용자가 앱을 열 때 가장 먼저 끝내려는 일은 `오늘의 시장 판단`이며, 첫 화면에는 시장 브리프와 사용자가 대표로 둔 포트폴리오 한 개의 현재 상태가 함께 필요하다.

이번 후보 비교는 기존 각 화면을 전면 개편하지 않고 새 기본 진입 화면과 상위 내비게이션만 정리하는 범위를 우선한다.

## Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
|---|---|---:|---:|---:|---:|---:|---|
| Today Home + Purpose-Based Navigation | Now | 5 | 3 | 2 | 5 | 5 | Finance app shell / Overview read models / Portfolio Monitoring read model |
| Overview를 Market / Equity Research로 실제 분리 | Next | 4 | 4 | 3 | 4 | 4 | Overview UI / routing |
| 전체 workflow를 Build / Validate / Decide / Monitor 독립 페이지로 분리 | Later | 3 | 5 | 5 | 3 | 3 | Backtest routing / app shell |
| First Screen Operations Diagnostics | Parking Lot | 1 | 3 | 3 | 5 | 1 | Ingestion / internal operations |

## Candidates

### Today Home + Purpose-Based Navigation

- Bucket: Now
- Problem: 현재 기본 `Overview`는 시장·종목 기능을 모두 품고 있지만 오늘의 시장 판단을 하나의 진입 결과로 완결하지 못한다. `Workspace` 안에는 사용자 리서치 화면과 내부 데이터 운영 화면도 함께 있다.
- User workflow change: 앱을 열면 `Today`에서 시장 상태, 핵심 근거, 오늘 일정과 대표 포트폴리오 영향을 읽고 기존 상세 화면으로 이동한다.
- Evidence: 현재 제품은 이미 경제 사이클, S&P 500, Futures Macro, Sentiment, Events, Portfolio Monitoring DB-backed read model을 갖고 있다. 사용자는 첫 업무를 `오늘의 시장 판단`으로, 첫 화면 포트폴리오 범위를 대표 포트폴리오 한 개로 선택했다.
- Required code/data/doc areas: `app/web/streamlit_app.py`, 신규 Today page/service/component, existing Overview loader/service boundaries, Portfolio Monitoring default-group read model, Reference destination copy, finance flow/product docs.
- Dependencies: 기존 Overview와 Portfolio Monitoring read model의 compact aggregation contract. 대표 포트폴리오는 기존 `monitoring_portfolio_group.is_default`를 기준으로 선택한다.
- Risks: 여러 무거운 UI renderer를 Today에서 직접 호출하면 초기 로딩과 결합도가 커진다. 시장 정보를 단일 점수나 매매 신호로 과장할 위험이 있다.
- Validation idea: pure read-model unit tests, no-provider-fetch boundary tests, route/deep-link regression, desktop/760px/420px Browser QA.
- Owner skill: `finance-task-intake` 후 app shell과 Portfolio Monitoring 연결은 `finance-backtest-web-workflow`, 최종 cross-surface 검토는 `finance-integration-review`.
- Priority rationale: `5 + 5 + 5 - 3 - 2 = 10`. 핵심 첫 업무를 직접 개선하고 기존 화면을 보존해 위험을 제한한다.

### Overview를 Market / Equity Research로 실제 분리

- Bucket: Next
- Problem: 현재 `Market Context` 안에 경제 사이클·S&P 500·미국 개별주식이 함께 있고, Market Movers와 개별주식 조사도 서로 다른 navigation depth에 있다.
- User workflow change: 시장 전체 판단과 종목 조사를 별도 페이지에서 수행한다.
- Evidence: 현재 Overview의 두 단계 selector가 market-level과 security-level 질문을 섞고 있다.
- Required code/data/doc areas: Overview navigation, query parameters, session state, Reference deep links, page routes.
- Dependencies: Today Home 실제 사용 후에도 Overview 과적재가 주요 병목인지 확인해야 한다.
- Risks: 기존 deep link와 session state를 이동하면서 회귀가 생길 수 있다.
- Validation idea: 기존 Overview query parameter compatibility와 각 tab actual-data Browser QA.
- Owner skill: 해당 후속 scope를 다시 `finance-task-intake`로 분류한다.
- Priority rationale: 가치가 높지만 승인된 1차 범위를 넘어가므로 후속 선택사항이다.

### 전체 workflow 독립 페이지화

- Bucket: Later
- Problem: Backtest라는 한 페이지가 후보 분석·실전 검증·최종 판단을 모두 소유한다.
- User workflow change: 각 단계가 독립 URL과 페이지를 갖는다.
- Evidence: Backtest workflow shell은 이미 Level 1~3 의미를 구분한다.
- Required code/data/doc areas: Backtest route/state, Reference destinations, saved replay and validation handoff.
- Dependencies: 현재 3-stage shell의 state handoff를 독립 route에서도 보존할 설계가 필요하다.
- Risks: 높은 회귀 위험에 비해 Today Home 목표에는 직접 필요하지 않다.
- Validation idea: full stage transition, replay, candidate handoff, deep-link regression.
- Owner skill: `finance-backtest-web-workflow`.
- Priority rationale: 1차 IA를 검증하기 전에는 과도한 구조 변경이다.

## Parking Lot

- Today에 ingestion job count, failure rows, raw logs, registry status를 주요 카드로 표시하는 안
- live broker holding, 주문, auto rebalance를 Today에 연결하는 안
- 시장 맥락을 Practical Validation PASS/BLOCKER 또는 자동 매매 신호로 바꾸는 안

## Rejected Ideas

- 기존 탭 전체를 동시에 재설계: 사용자가 승인한 범위를 벗어나고 회귀 범위가 너무 크다.
- 현재 Overview에 포트폴리오 카드만 덧붙이는 최소안: 변경 비용은 낮지만 `Workspace` 분류 문제와 첫 화면의 목적 불명확성을 해결하지 못한다.
- Build / Validate / Decide / Monitor 전면 workflow안: 구조는 명확하지만 현재 작업의 핵심인 오늘의 시장 판단보다 migration 비용이 앞선다.
