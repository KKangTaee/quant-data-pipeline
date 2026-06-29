# Overview Market Context UX V3 Design

## User Flow

1. 사용자는 Overview 첫 탭에서 시장 맥락 한 줄 요약을 먼저 읽는다.
2. 바로 아래에서 자료 상태가 정상인지, 일부 자료 확인이 필요한지, 어디로 가야 하는지 본다.
3. 핵심 카드 3개로 시장 움직임 / 폭과 집중도 / futures 배경을 빠르게 확인한다.
4. 보조 카드 3개로 심리 / 이벤트 / 자료 상태를 해석 전 확인한다.
5. `다음 확인 순서`에서 필요한 deep tab으로 이동한다.
6. 자료가 오래됐거나 부족하면 보조 갱신 영역 또는 Data Health / Ingestion handoff를 따른다.

## Copy Principles

- Market Context 상태와 자료 상태를 분리한다.
- 사용자에게 보이는 상태/설명 문구는 한국어 중심으로 쓴다.
- source, owner, DB-backed 같은 경계 정보는 숨기지 않되 보조 근거로 둔다.
- `Freshness: -`, `Source REVIEW`, `in 1 days`처럼 의미를 바로 알기 어려운 표시는 `자료 기준`, `일부 자료 확인 필요`, `1일 후`처럼 바꾼다.

## Structure

- `render_overview_dashboard()`의 page title/caption은 한국어로 정리한다.
- `_render_overview_market_context_tab()`은 heading/caption 중복을 줄이고 cockpit을 먼저 렌더링한다.
- `_render_overview_market_context_refresh_bar()`는 보조 유지관리 영역으로 낮춘다.
- `render_macro_context_cockpit()`은 핵심/보조 섹션 heading과 `다음 확인 순서`를 렌더링한다.
- `build_overview_macro_context_cockpit()`은 카드 group / priority / Korean labels를 제공한다.

## Boundary

기존 `Ingestion -> DB -> Loader -> UI` 흐름을 유지한다.
이번 작업은 read model과 Streamlit render copy/IA만 바꾸며 provider fetch, schema, persistence, registry/saved write를 추가하지 않는다.
