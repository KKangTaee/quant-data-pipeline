# Design

## Files

- `app/web/overview_ui_components.py`
  - 기존 `_analog_outcome_matrix_html` / `_macro_result_delta_html`는 이미 `is-positive`, `is-negative`, `--ov-analog-cell-strength`를 출력한다.
  - CSS 색상 혼합 방식을 더 선명한 green / red gradient로 바꿔 화면상 가시성을 높인다.
  - `_macro_backdrop_*` helper에 value bucket의 해석 문장을 추가해 `조건에는 쓰지 않은 Macro 배경` 카드 안에 표시한다.

- `tests/test_service_contracts.py`
  - Macro backdrop HTML test에 금리곡선 / 변동성 / 신용스프레드 상태 의미 문장 기대값을 추가한다.
  - Matrix gradient test에 positive / negative gradient class와 CSS token을 확인한다.

## Boundaries

- `app/services/overview_market_context_analog.py`의 bucket 기준은 이번 차수에서 변경하지 않는다.
- Macro reference values are context-only. They do not narrow anchor samples and do not create a trade, validation, final-review, or monitoring signal.
- UI에서 FRED / provider를 직접 fetch하지 않는다.
