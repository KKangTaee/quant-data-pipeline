# Status

Status: Completed
Date: 2026-07-06

## Completed

- `app/services/backtest_practical_validation_workspace.py`
  - Flow 4 `criteria_detail_groups`를 `Source & Replay`, `Data Quality / Bias Control`, `Comparison Validity`, `Realism / Tradability`, `Validation Strength / Robustness`, `Portfolio Construction`, `Conditional Evidence` category로 재구성했다.
  - `selected_route_preflight`는 `handoff_summary_groups`로 분리해 검증 category count에서 제외했다.
- `app/services/backtest_practical_validation_modules.py`
  - stress / robustness `NOT_RUN` 또는 `NEEDS_INPUT`은 기본적으로 Final Review review로 낮췄다. `BLOCKED`만 차단한다.
  - construction risk는 ETF-like 또는 weighted mix 후보에만 적용한다.
  - sentiment risk-on/off overlay는 macro gate status에 반영하지 않고 context 상태로만 남긴다.
- `app/web/backtest_practical_validation/page.py`
  - Flow 4 보드 제목을 `카테고리별 검증 결과`로 바꿨다.
  - Final Review 이동 가능성은 `Final Review 이동 요약`으로 분리했다.
- `app/web/components/practical_validation_fix_queue/frontend/src/PracticalValidationFixQueue.tsx`
  - React Fix Queue summary / criteria preview 문구를 category-first wording으로 변경했다.
  - Streamlit이 로드하는 `frontend/build` 산출물도 rebuild하고, build artifact copy 회귀 테스트를 추가했다.
- `tests/test_service_contracts.py`
  - category-first grouping, selected-route preflight 분리, stress review downgrade, construction non-applicability, sentiment context-only behavior를 회귀 테스트로 고정했다.

## Result

Flow 3은 Final Review 이동 결론과 먼저 해결할 일을 계속 보여준다.

Flow 4는 이제 검증 category별 pass / blocker / review 상태와 실패 항목을 먼저 보여주며, Final Review 이동 가능성은 파생 요약으로 낮춘다.

## Verification

- `unittest tests.test_service_contracts.PracticalValidationServiceContractTests`: pass
- `unittest` Flow 3 / Flow 4 selected contract tests: pass
- `unittest tests.test_backtest_refactor_boundaries`: pass
- `py_compile` changed Python modules: pass
- `git diff --check`: pass
- Browser QA: `http://localhost:8509/backtest`에서 Practical Validation pill 클릭 후 Flow 4 `카테고리별 검증 결과`와 별도 `Final Review 이동 요약` 렌더링 확인
