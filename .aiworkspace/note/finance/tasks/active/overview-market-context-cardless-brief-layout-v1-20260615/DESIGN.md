# Overview Market Context Cardless Brief Layout V1 Design

## Problem Interpretation

현재 UI는 `ov-macro-cockpit`이라는 큰 패널 안에 rail card, brief row card, cue card, historical analog card, source confidence card grid가 들어간다.
이 구조는 기능 추가에는 편했지만, 사용자가 시장 맥락을 한 흐름으로 읽는 데 방해가 된다.

## Design Direction

- 큰 외곽 cockpit 배경은 유지하되 카드처럼 보이는 개별 박스 수를 줄인다.
- 상단은 headline + 작고 평평한 status strip으로 둔다.
- `시장 브리프`는 numbered card list가 아니라 3줄 briefing table처럼 보이게 한다.
- `해석할 때 같이 볼 변수`는 3개 card grid가 아니라 compact cue list로 둔다.
- `과거 유사 맥락 참고`는 별도 bordered card가 아니라 얇은 note row와 필요 시 table로 둔다.
- `자료 기준 / 출처 상태`는 접힌 disclosure로 유지하지만 내부 card grid를 dense list로 낮춘다.

## Implementation Plan

1. Add failing tests that inspect generated HTML/CSS for cardless structure.
2. Refactor CSS class semantics:
   - keep public function names
   - replace grid/card visual rules with row/list visual rules
   - remove `ov-historical-analog` bordered panel style
3. Refactor HTML helpers:
   - `_macro_cockpit_rail_html` returns compact status strip
   - `_macro_cockpit_brief_rows_html` returns row table/list
   - `_macro_cockpit_interpretation_cues_html` returns cue list
   - `_macro_cockpit_historical_analog_html` returns inline note/table section
4. Keep read model untouched unless tests reveal display-only field needs.

## Boundary

This task changes only `Overview > Market Context` rendering and tests.
It does not change data fetch, DB meaning, analog math, validation gates, trading semantics, registry/saved files, or operations monitoring.
