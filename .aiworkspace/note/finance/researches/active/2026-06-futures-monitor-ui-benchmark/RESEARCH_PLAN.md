# Futures Monitor UI Benchmark Research Plan

Status: Active
Last Updated: 2026-06-23

## Research Question

`Workspace > Overview > Futures Monitor`가 단순 한글화 / 카드 정렬 수준에 머무르지 않고, 사용자가 선물과 매크로 상태를 빠르게 읽고 다음 행동을 결정할 수 있는 제품 화면이 되려면 어떤 UX/UI 패턴을 가져와야 하는가?

## Scope

- 포함: TradingView / Koyfin, IBKR 계열 전문 트레이딩 워크스페이스, Datadog / Grafana, Stripe / Linear, 토스증권 UI/UX 벤치마킹.
- 포함: control bar, watchlist, refresh/data freshness, macro brief, evidence drilldown, chart layout, plain-language interpretation.
- 제외: live order, broker account 연결, auto rebalance, trading recommendation, validation gate, provider/schema 변경.

## Method

1. 현재 Futures Monitor screenshot과 직전 구현 결과의 문제를 제품 흐름 관점으로 정리한다.
2. 각 벤치마크에서 관찰 가능한 UI / workflow 패턴을 수집한다.
3. 이 프로젝트의 read-only Overview context boundary에 맞는 패턴만 추출한다.
4. immediate / next / later 후보로 나눠 개선 가이드라인을 작성한다.

## Output

- `CURRENT_PROJECT_AUDIT.md`
- `BENCHMARKS.md`
- `UI_PATTERNS.md`
- `FEATURE_CANDIDATES.md`
- `RECOMMENDATION.md`
- `SOURCES.md`
- `RISKS.md`

