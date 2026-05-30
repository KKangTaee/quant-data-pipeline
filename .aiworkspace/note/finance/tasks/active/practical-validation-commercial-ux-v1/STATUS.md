# Status

## 2026-05-30

- 사용자 승인에 따라 Practical Validation 상용 UX 개편 작업 시작.
- 범위는 표시 계층 개선으로 제한하고, service/gate 계약은 유지하기로 결정.
- `app/web/backtest_ui_components.py`에 product section header, action card grid, stepper helper를 추가.
- Practical Validation profile preview, Control Center, Fix Queue, summary-first Evidence Workspace, Provider Action Center를 추가.
- raw module / evidence / provider table은 상세 expander 또는 탭 안으로 낮춤.
- durable flow / project map / roadmap 문서에 새 화면 구조를 반영.
- 1차 pass가 여전히 기본 Streamlit card 느낌을 벗어나지 못한다는 사용자 피드백을 반영해 전용 `backtest_practical_validation_components.py` product shell로 2차 visual overhaul을 진행.
- Practical Validation 상단, step section, Control Center, Gate, Evidence, Action, Save & Move 영역을 전용 dark workbench 컴포넌트로 교체하고 기존 `st.container(border=True)` 중심 구획을 제거.
