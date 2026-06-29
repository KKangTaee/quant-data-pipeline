# Overview Market Context Brief Flow V1 Design

## User Flow

1. 사용자는 `현재 맥락:` 한 줄 요약을 먼저 읽는다.
2. `시장 브리프`에서 무엇이 움직였는지, 그 움직임이 넓은지/집중인지, futures/macro 배경이 무엇인지 순서대로 읽는다.
3. `해석할 때 같이 볼 변수`에서 가까운 이벤트, 심리 배경, 자료 상태 주의점만 작게 확인한다.
4. 필요하면 각 행에 녹아 있는 확인 위치를 따라 Market Movers, Sector / Industry, Futures Monitor, Events, Sentiment, Data Health로 이동한다.
5. 자료 상세와 갱신은 접힌 보조 영역으로 남긴다.

## Structure

- `build_overview_macro_context_cockpit()`은 기존 cards를 유지하되 `brief_rows`, `interpretation_cues`를 추가해 시장 브리프 read model을 명시한다.
- `render_macro_context_cockpit()`은 standalone `다음 확인 순서`와 guide-style next-check grid를 렌더링하지 않는다.
- `render_overview_dashboard()`의 Market Context caption은 다음 순서 안내가 아니라 브리프 읽기 흐름을 설명한다.
- Deep Tab / Overview Map disclosure는 Market Context 첫 화면에서 제거하고, 탭 이동 정보는 각 브리프/변수 행의 `확인 위치`로 자연스럽게 둔다.

## Boundary

기존 `Ingestion -> DB -> Loader -> UI` 흐름을 유지한다.
이번 1차는 저장된 snapshot을 읽는 UI/read-model 재구성이며 provider fetch, schema, registry/saved write, validation/monitoring/trading semantics를 만들지 않는다.
