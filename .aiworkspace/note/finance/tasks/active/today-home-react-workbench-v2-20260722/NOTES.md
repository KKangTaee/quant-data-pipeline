# Today Home React Workbench V2 Notes

## Confirmed Decisions

- React 전환 범위는 Streamlit 상단 page navigation을 제외한 Today 본문 전체다.
- 기존 경제사이클·S&P 내부 기능은 변경하지 않는다.
- 시각 방향은 A안 Market Context Workbench다.
- 판단 근거는 좌측 색상선을 쓰지 않고 text label과 color를 함께 쓴다.
- 모든 typography role은 승인된 최초 A안보다 1px 확대한다.
- chart는 일별 저장 종가 기반 누적 수익률이며 주봉·장중으로 표현하지 않는다.
- X축은 실제 관측일, Y축은 현금흐름 조정 누적 수익률(%), tooltip은 당시 평가액을 보조 정보로 표시한다.

## Evidence

- `app/services/today.py::_portfolio_curve`는 active curve의 마지막 60개 `unit_value`를 투영한다.
- `app/services/portfolio_monitoring/read_model.py::align_group_value_lanes`는 저장 일별 lane date를 공통 timeline으로 정렬하고 `daily_flow_adjusted_return`, `unit_value`를 계산한다.
- 현재 V1 sparkline은 axis와 주기/기간 label 없이 unit value만 연결한다.
- `day_return`은 최신 두 unit-value 관측의 비율이므로 실제 달력상의 오늘 장중 수익률이 아니다.
