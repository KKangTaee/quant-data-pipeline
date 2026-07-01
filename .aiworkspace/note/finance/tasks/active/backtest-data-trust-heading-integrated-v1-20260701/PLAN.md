# Plan

## 이걸 하는 이유?

Run Backtest 결과 상단은 커스텀 result KPI band와 커스텀 Data Trust panel이 이어지는 구조인데, 그 사이에 기본 Streamlit heading인 `데이터 기준 요약`이 별도 제목으로 끼어 있어 시각적 흐름이 끊겼다.
사용자는 `데이터 기준 요약`을 별도 섹션 제목으로 크게 보기보다, Data Trust panel 자체의 제목으로 읽는 편이 자연스럽다.

## Scope

- `app/web/backtest_result_display.py`
  - `_render_data_trust_summary`의 standalone `st.markdown("#### 데이터 기준 요약")`를 제거한다.
  - Data Trust custom panel 내부에 `데이터 기준 요약` title과 `먼저 볼 결론` kicker를 함께 표시한다.
- `tests/test_service_contracts.py`
  - Data Trust title이 custom panel 내부에 있고 standalone heading으로 렌더되지 않는 계약을 고정한다.

## Non-Scope

- Data Trust 계산 모델, warning queue, strategy runtime, result bundle, registry / saved / validation persistence는 변경하지 않는다.
