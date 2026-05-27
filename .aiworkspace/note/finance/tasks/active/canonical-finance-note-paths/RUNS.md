# Runs

| Time | Command | Result |
|---|---|---|
| 2026-05-28 | `rg -n ".note/finance|.note|note/finance|registries|saved" app finance tests ...` | 여러 runtime/job/web 파일의 legacy `.note/finance` 직접 참조 확인 |
| 2026-05-28 | `find .aiworkspace/note/finance -maxdepth 3 -type f` | canonical `registries`, `saved`, `run_history`, stress window JSON 존재 확인 |
| 2026-05-28 | `.venv/bin/python -m py_compile ...` | 변경 모듈 컴파일 통과 |
| 2026-05-28 | `.venv/bin/python -m unittest tests.test_service_contracts` | 23 tests OK |
| 2026-05-28 | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | PASS, hard violations none |
| 2026-05-28 | Browser smoke `http://localhost:8501` | Overview가 canonical registry/saved/run_history 값을 읽어 핵심 카운트와 Top 3 후보를 표시 |
