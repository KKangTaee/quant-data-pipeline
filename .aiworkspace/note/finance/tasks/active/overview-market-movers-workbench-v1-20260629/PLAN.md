# Overview Market Movers Workbench V1

Status: Active
Owner: sub-dev
Started: 2026-06-29

## 이걸 하는 이유?

`Overview > Market Movers`는 사용자가 변동종목을 빠르게 발견하고, 어떤 coverage / period / freshness 기준으로 보고 있는지 즉시 판단해야 하는 화면이다. 기존 화면은 차트, 표, 진단, Why It Moved가 병렬로 보여 prototype처럼 읽히므로, 기존 snapshot/read model과 action facade 경계는 유지하되 실사용 작업대 흐름으로 단계적으로 정리한다.

## 전체 Roadmap

| 차수 | 목적 | 화면 / 파일 범위 | 완료 조건 | 다음 차수 연결 |
|---|---|---|---|---|
| 1차 | Market Movers UX 골격 재설계 | `app/web/overview/market_movers_helpers.py`, `app/web/overview/components/market_movers.py`, 공통 style, focused tests | command strip, 상위 목록, 핵심 차트/섹터 요약, 보조 진단, empty state가 보인다 | 2차 탐색 mode/read model의 자리 마련 |
| 2차 | 탐색 모드와 ranking read model 정리 | service/read model + UI mode selector | Top Gainers / Losers / Volume / Unusual Volume / Sector 흐름 전환 | 3차 선택 종목 detail의 rank context |
| 3차 | 선택 종목 detail pane과 Why It Moved 통합 | Market Movers selection + `why_it_moved` service boundary | 선택 종목 조사 시작점이 workflow 안에 들어온다 | 4차 sector/peer context 강화 |
| 4차 | 섹터/히트맵/시장 확산 맥락 개선 | Sector Pulse visual/read model | 섹터 집중/확산을 context-only로 확인 | 5차 data trust wording 통합 |
| 5차 | Coverage/Data Quality UX 정리 | coverage trust strip/drawer + diagnostics grouping | 신뢰 상태와 누락 이유를 덜 헷갈리게 판단 | 필요 시 durable docs alignment |

## 1차 Scope

- 기존 snapshot/read model, DB schema, provider, action facade 경계를 유지한다.
- command strip 모델을 추가해 coverage, period, effective timestamp, freshness, universe count, returnable count, missing count, current mode를 요약한다.
- 기존 Return Rank / Volume Rank / Sector Pulse / Return Table / Volume Table을 작업대 흐름으로 재배치한다.
- Coverage Diagnostics는 보조 expander로 남긴다.
- Why It Moved는 기능 확장 없이 `선택 종목 조사` 자리로 낮춰 연결한다.
- Nasdaq / stale / no-row 상태는 empty state로 설명한다.

## Non-Goals

- 새 DB schema, 새 provider, UI 직접 외부 fetch.
- 자동 원인 판정, AI 요약, trade signal, buy/sell recommendation.
- Practical Validation PASS/BLOCKER, Final Review decision, Operations monitoring signal 연결.
- Coverage Diagnostics 또는 run/job/status table을 메인 UX로 승격.
