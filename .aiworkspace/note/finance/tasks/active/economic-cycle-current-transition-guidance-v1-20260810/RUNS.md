# Runs

- 2026-08-10: 실제 DB read model과 Browser UI를 read-only 진단해 presentation mismatch를 재현했다.
- 2026-08-10: service TDD RED/GREEN 후 `tests/test_economic_cycle_service.py` 38 passed.
- 2026-08-10: React component 13 passed, TypeScript `--noEmit` 통과, Vite production build 완료.
- 2026-08-10: `tests/test_economic_cycle_*.py tests/test_market_context_economic_cycle.py` 219 passed, 3 dependency deprecation warnings.
- 2026-08-10: 실제 Browser QA에서 `위축 → 회복`, 조건 실제값/임계값, legacy anchor 보조 표시, DGS2/DGS10/DFII10/T10YIE 노출을 확인했다.
- 2026-08-10: QA screenshot `economic-cycle-current-transition-guidance-qa.jpg` 생성(커밋 제외).
- 2026-08-10: repository-wide `.venv/bin/python -m pytest -q`는 2090 passed, 336 failed, 4 warnings, 158 subtests passed. 기존 Streamlit 재import 순서에서 `DeltaGeneratorSingleton instance already exists`가 연쇄 발생해 전체 suite baseline은 non-green.
