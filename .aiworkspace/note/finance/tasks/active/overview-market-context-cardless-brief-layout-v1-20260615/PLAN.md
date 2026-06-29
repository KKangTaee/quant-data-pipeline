# Overview Market Context Cardless Brief Layout V1 Plan

## 이걸 하는 이유?

`Overview > Market Context`는 1차~4차 동안 시장 브리프, 갱신 반영, 이벤트 신뢰도, 과거 유사 맥락 기능이 붙으면서 정보는 풍부해졌지만 시각적으로는 카드와 패널이 중첩되어 한눈에 읽기 어려워졌다.
이번 5차는 새 기능을 추가하지 않고, 카드 중심 UI를 행/문서형 브리프 구조로 낮춰 사용자가 현재 시장 맥락을 더 빠르게 읽게 만드는 UX 정리다.

## 전체 흐름

- 1차 완료: guide/card 구조를 시장 브리프 흐름으로 바꿨다.
- 2차 완료: refresh 이후 상단 브리프가 새 snapshot을 다시 읽게 했다.
- 3차 완료: recent + upcoming macro event와 Data Health cue를 compact하게 정리했다.
- 4차 완료: sector ETF proxy 기반 `과거 유사 맥락 참고` MVP를 추가했다.
- 5차 현재: 중첩 카드 느낌을 제거하고 `현재 맥락 -> 핵심 브리프 행 -> 참고 변수 행 -> 과거 유사 맥락 얇은 행 -> 접힌 출처` 구조로 정리한다.

## Scope

- `app/web/overview_ui_components.py`의 Market Context CSS/HTML 구조를 card-heavy layout에서 document-like brief layout으로 전환한다.
- `render_macro_context_cockpit()` 내부에 중첩 패널 느낌을 줄이고, rail / brief / cue / analog를 row 중심으로 표시한다.
- `source_confidence`는 기본 접힘 disclosure로 유지하되 내부 card grid의 시각 무게를 낮춘다.
- `tests/test_service_contracts.py`에 UI contract tests를 추가해 card grid / nested panel 회귀를 막는다.

## Out Of Scope

- 새 market context 기능 추가.
- historical analog 계산식 변경.
- DB schema, provider, registry/saved JSONL 변경.
- Backtest / Practical Validation / Final Review / Operations 연결.
- Streamlit 플랫폼 전환.

## Completion Conditions

- Market Context 첫 화면이 카드 대시보드가 아니라 브리프 문서처럼 읽힌다.
- `과거 유사 맥락 참고`는 독립 카드가 아니라 얇은 참고 행 또는 compact table로 보인다.
- source confidence는 주인공이 아니라 접힌 보조 근거로 남는다.
- focused tests, compile, diff check, Browser QA screenshot, coherent commit을 완료한다.
