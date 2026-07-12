# Practical Validation Flow5 CTA Integration V1 Plan

## 이걸 하는 이유?

Flow5는 새 검증 단계라기보다 Practical Validation 결론을 저장하고 Final Review로 넘기는 실행부다.
사용자는 Flow3에서 이미 이동 가능 여부를 읽고 있으므로, 별도 Flow5 container를 계속 보여주면 `검증 결론`과 `다음 행동`이 떨어져 보인다.
이번 작업은 Flow3 결론 카드 안에서 다음 행동을 바로 수행하게 하되, 저장 / handoff / gate / registry write는 기존 Python service 경계에 남기는 것이 목적이다.

## Scope

- `app/services/backtest_practical_validation_workspace.py`
- `app/web/backtest_practical_validation/workspace_panel.py`
- `app/web/backtest_practical_validation/page.py`
- `app/web/components/practical_validation_fix_queue/`
- focused contract tests in `tests/test_service_contracts.py`
- durable flow docs and root handoff logs

## Non-goals

- 새 provider / FRED / API / DB fetch path 생성 없음
- validation gate 계산 변경 없음
- Final Review selected-route policy 변경 없음
- registry / saved JSONL rewrite 없음
- live approval / broker order / auto rebalance 의미 추가 없음

## 단계별 개발

1. Contract / TDD: Flow3 CTA, intent-only React action, visible Flow5 제거, raw JSON 이동 계약을 실패 테스트로 고정한다.
2. Read model: workspace에 `next_stage_action`을 추가해 Flow3가 CTA 상태를 읽게 한다.
3. React UI: `practical_validation_fix_queue`에 primary / secondary CTA를 추가하고 클릭 intent만 Streamlit에 전달한다.
4. Streamlit wiring: Python이 React intent를 소비해 기존 save / Final Review handoff service를 실행하고, 별도 Flow5 container를 제거한다.
5. Docs: BACKTEST_UI_FLOW / PORTFOLIO_SELECTION_FLOW / ROADMAP / INDEX / root logs를 필요한 만큼 갱신한다.
6. QA / Commit: focused unittest, py_compile, git diff check, Browser QA screenshot 후 generated artifact 제외 commit을 만든다.

## 완료 조건

- Practical Validation user-facing UI에 `Flow 5` / `저장 / Final Review 이동` 별도 단계가 보이지 않는다.
- Flow3 `검증 결론`에서 이동 가능 여부와 저장 / 이동 CTA를 한 번에 읽고 실행할 수 있다.
- React는 intent만 전달하고, 저장 / handoff / rerun / session state 변경은 Python이 담당한다.
- Gate 미통과 시 Final Review 이동 CTA는 비활성화되고 audit-only 저장은 명확히 구분된다.
- raw source/result JSON은 `상세 근거 / 원자료` 보조 영역으로 낮아진다.
