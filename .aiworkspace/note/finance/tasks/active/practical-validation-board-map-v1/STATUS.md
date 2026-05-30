# Status

## 2026-05-30

- 사용자 승인에 따라 Practical Validation 보드 / 모듈 구분 개선 작업 시작.
- 기존 module planner와 UI render 위치 확인 완료.
- `backtest_practical_validation_board_registry.py`를 추가해 화면 board와 validation module 연결을 Streamlit-free service로 분리.
- module planner가 module type, applicability reason, evidence boards, board map을 반환하도록 확장.
- Practical Validation UI에 Applied Validation Map과 board context badge를 추가.
- 단일 component 후보에서는 Risk Contribution / Component Role / Weight board를 collapsed `Not applicable` 보드로 낮춤.
- 상단 Practical Validation route panel도 legacy diagnostic route가 아니라 Final Review Gate route를 표시하도록 맞춤.
