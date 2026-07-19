# Backtest Component Static Distribution V1 Risks

## Known Baseline Failures

이번 변경 전후 focused service contract에는 동일한 기존 실패 2건이 남아 있다.

1. `test_final_review_investment_report_react_component_emits_intent_only`
   - test가 `is_final_review_investment_report_available`을 기대하지만 current wrapper는 `is_final_review_decision_workspace_available`을 제공한다.
2. `test_practical_validation_fix_queue_react_component_is_ui_only`
   - test가 제거된 `render_practical_validation_workspace_overview`을 기대한다.

둘 다 component static path와 무관하며 사용자 승인에 따라 이번 task에서 수정하지 않았다.

## Ongoing Artifact Drift Risk

- frontend source만 수정하고 build를 빠뜨리면 committed JS/CSS가 stale해질 수 있다.
- 완화책은 `tests/test_component_static_distribution.py`, `emptyOutDir: true`, source와 generated bundle의 동일 commit 원칙이다.

## Generated Artifacts

- `backtest-component-static-distribution-qa.png`는 로컬 QA 증거이며 커밋하지 않는다.
- 기존 institutional QA 이미지와 `.superpowers/`는 사용자/다른 작업 소유로 그대로 보존했다.
