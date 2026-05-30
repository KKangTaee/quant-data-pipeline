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
- `1. 선택 후보 확인`에 Backtest Analysis source snapshot의 Summary / Equity Curve / Result Table / Components 탭을 추가해 후보의 원래 백테스트 근거를 먼저 확인하게 함.

## 2026-05-31

- `저장하고 Final Review로 이동`에서 Practical Validation result 저장 시 DB coverage의 `Decimal` 값이 JSON 직렬화를 막는 문제를 재현하고 수정.
- Clean V2 registry append 경계에서 Decimal / date / datetime / numpy scalar / DataFrame fallback을 JSON-safe primitive로 정규화하도록 보강.
- `검증 결과 저장(기록용)`과 `저장하고 Final Review로 이동`의 의미를 분리. 저장-only row는 audit trail로 남지만 Final Review Gate를 통과하지 않으면 Final Review source picker에 표시하지 않도록 필터링.
- Practical Validation 탭 신규 진입 / source 변경 시 이전 runtime replay 표시 state를 비워, 현재 세션에서 사용자가 `전략 재검증 실행`을 누른 결과만 Step 3에 표시하도록 조정.
- 상용 visual overhaul에서 흐려진 step 경계를 보완하기 위해 Step 1~7 본문을 bordered surface로 다시 묶고, 상단 7-step rail을 추가.
