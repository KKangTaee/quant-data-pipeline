# Backtest Handoff UI Integrated V1 Plan

## 이걸 하는 이유?

`Run Backtest` 이후의 `2차 실전성 검증 Handoff`가 custom 카드와 별도 Streamlit container로 나뉘어 같은 행동을 두 번 설명한다.
사용자는 검증으로 보낼 수 있는지, 막는 이유가 무엇인지, 버튼이 왜 활성 / 비활성인지 한 곳에서 읽어야 한다.

## Scope

- `app/web/backtest_result_display.py`의 Latest Backtest Run handoff UI만 수정한다.
- `_build_practical_validation_handoff_state`와 `_build_next_step_readiness_evaluation`의 gate 의미는 바꾸지 않는다.
- Practical Validation source 저장 경로, registry / saved JSONL, strategy runtime, result bundle format은 변경하지 않는다.

## Steps

1. RED: handoff가 단일 통합 action surface를 쓰는 service contract test를 추가한다.
2. GREEN: 중복 `st.container(border=True)`와 중복 heading을 제거하고, custom handoff panel + 단일 action row로 합친다.
3. QA: focused handoff tests, py_compile, diff check, Streamlit Browser QA를 실행한다.
4. Closeout: Backtest UI flow doc, root handoff logs, task records를 정리하고 commit한다.

## Done Criteria

- `2차 실전성 검증 Handoff` 제목은 결과 화면에서 중복되지 않는다.
- 버튼 활성 / 비활성 판정은 기존 promotion / execution / validation source checks를 그대로 따른다.
- Handoff 영역은 blocker / review reason, source 등록 boundary, 다음 Practical Validation 확인 범위를 한 곳에서 보여준다.
