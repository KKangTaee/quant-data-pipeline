# Overview Futures Macro Tab Split V1 Plan

## Goal

`Workspace > Overview`의 첫 진입 화면인 `시장 맥락`을 빠른 시장 브리프 중심으로 경량화하고, 무거운 futures macro 진단 / historical validation은 새 `선물 매크로` primary tab에서 관리한다.

## 이걸 하는 이유?

현재 Overview 기본 진입은 `Market Context`를 즉시 렌더링하면서 movers, sector leadership, futures macro, sentiment, events, collection ops, historical analog를 한 번에 로드한다. 특히 futures macro historical validation은 약 7초 이상 걸려 첫 화면 체감 로딩을 크게 늦춘다. 사용자는 처음에는 오늘 시장 흐름을 빠르게 읽고, futures macro를 깊게 볼 때만 별도 탭에서 무거운 과거 점검을 여는 흐름이 더 자연스럽다.

## Scope

- Overview primary tab에 `Futures Macro` / `선물 매크로`를 추가한다.
- `Market Context` helper path는 futures macro snapshot / validation과 historical analog를 기본 로드하지 않는다.
- `Market Context`의 summary, rail, brief rows, interpretation cues에서 macro 진단을 제거하거나 별도 탭 이동 안내로 낮춘다.
- 기존 `_render_futures_macro_tab` 경로를 primary tab renderer로 연결한다.
- `nyse_price_history` 최신 raw date 조회를 첫 화면 병목이 덜한 방식으로 조정한다.
- 관련 task / durable docs / root handoff logs를 정렬한다.

## Out Of Scope

- futures validation 결과 DB 저장 테이블 추가.
- futures ingestion provider 변경.
- trading signal, recommendation, Practical Validation gate, monitoring signal, broker order, auto rebalance 의미 추가.
- registry / saved JSONL 변경.
- `Futures Monitor`를 다시 primary tab으로 복구.

## Stop Condition

- Overview tab options are `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events`.
- `Market Context` cold loader no longer calls `load_overview_futures_macro_snapshot` or `load_overview_market_context_historical_analog`.
- `Futures Macro` tab renders the existing futures macro panel with historical validation.
- Focused contract tests, compile, `git diff --check`, and Browser QA complete.

## Implementation Checklist

1. Add RED tests for tab order, slug/display contract, renderer dispatch, and light Market Context loader.
2. Update Overview constants and renderer map.
3. Add `include_futures_macro` / `include_historical_analog` support to the helper, defaulting the Market Context helper to lightweight loading.
4. Update cockpit summary / rail / brief rows to handle macro absence cleanly.
5. Keep full validation in `_render_futures_macro_tab`.
6. Rewrite latest raw date query to avoid full `MAX(date)` scan.
7. Update documentation and task logs.
8. Run focused verification and Browser QA.
