# Notes

## 2026-05-30

- 리뷰 결과 치명적 gate 로직 결함은 발견하지 못했다.
- 주요 UX gap은 raw table 우선 노출, blocker action의 낮은 시각 우선순위, board map의 내부 구현 표식 느낌, Streamlit 기본 container 중심 레이아웃이다.
- 구현은 validation result contract를 바꾸지 않고 `app/web` 표시 계층만 변경했다.
- `Applied Validation Map`은 보조 `검증-근거 연결 지도`로 접어 두고, Final Review 이동 판단은 Control Center / Fix Queue가 먼저 설명한다.
- Provider Data Gaps는 action center 요약 카드가 먼저 나오고 상세 table / action plan은 접힘 영역으로 내려간다.
- 2차 visual overhaul은 검증 로직이나 저장 계약을 바꾸지 않고, `app/web/backtest_practical_validation_components.py`에 Practical Validation 전용 CSS / command center / section / card / step rail helper를 둔다.
- 새 shell은 검증 module, evidence board, action board가 같은 검증 목록처럼 보이지 않도록 section boundary와 tone을 더 강하게 분리한다.
- 선택 후보 확인의 backtest mini report는 기존 source의 `summary`, `result_curve`, `benchmark_curve`, `components` snapshot만 읽는다. 새 backtest 실행, registry rewrite, Final Review gate 계산 변경은 없다.

## 2026-05-31

- 저장 오류의 1차 원인은 `input_evidence.data_coverage_context.price_window_rows[].window_row_count`에 MySQL / pandas 경계에서 넘어온 `Decimal` 값이 포함되어 `json.dumps`가 실패한 것이다.
- 해결은 Practical Validation 전용 계산을 바꾸지 않고 `app/runtime/portfolio_selection_v2.py`의 append-only JSONL write 경계에서 JSON-safe 정규화를 적용하는 방식으로 제한했다.
