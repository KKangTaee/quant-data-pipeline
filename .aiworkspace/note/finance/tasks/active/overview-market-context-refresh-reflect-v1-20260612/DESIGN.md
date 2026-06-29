# Overview Market Context Refresh Reflect V1 Design

## Root Cause

`_render_overview_market_context_tab()`은 상단 cockpit을 먼저 그리고, `_render_overview_market_context_refresh_bar()`는 그 아래에서 버튼을 실행한다.
현재 버튼 handler는 일부 cache를 clear하지만 `st.rerun()`을 호출하지 않아, 같은 Streamlit 실행 cycle에서 이미 렌더된 상단 brief가 그대로 보일 수 있다.

## Implementation Direction

- cache clear 대상을 Market Context read model 계층 전체로 명시한다.
  - composite cockpit cache
  - group leadership cache
  - sentiment cache
  - futures macro cache
  - market movers / events / collection ops는 현재 uncached direct read path라 rerun 시 새로 읽힌다.
- refresh result를 session state에 저장하고, success / partial success일 때 cache clear 후 `st.rerun()`한다.
- failure / error는 새 snapshot 반영 상태로 말하지 않는다. 다만 rerun해서 상단에 작은 실패 안내를 보이고, 기존 snapshot을 계속 읽고 있음을 표시한다.
- 상단 안내는 `방금 갱신을 반영했습니다`, `일부 자료만 반영했습니다`, `갱신 실패 - 기존 자료를 계속 표시합니다` 수준의 작은 보조 copy로 둔다.
- 기존 result expander는 접힌 상태의 보조 결과로 유지한다.

## Boundary

이 task는 Streamlit UI state / cache / rerender 흐름만 다룬다.
새 provider, DB schema, registry / saved JSONL, CPI/Event collector coverage, Macro Calendar 수집 정책, Data Health 전체 개편, Backtest / Operations / Validation 화면은 변경하지 않는다.
