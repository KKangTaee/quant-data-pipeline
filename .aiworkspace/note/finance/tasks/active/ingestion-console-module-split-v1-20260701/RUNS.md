# Runs

작업 중 실행한 QA 명령과 결과를 기록한다.

## 1차

- RED: `.venv/bin/python -m unittest tests.test_ingestion_module_split_contracts -v`
  - Result: expected failure. `app.web.ingestion` package did not exist and legacy console was still the full implementation file.
- GREEN: `.venv/bin/python -m unittest tests.test_ingestion_module_split_contracts -v`
  - Result: PASS, 2 tests.
- Compile: `.venv/bin/python -m py_compile app/web/ingestion_console.py app/web/ingestion/__init__.py app/web/ingestion/page.py`
  - Result: PASS.

## 2차

- RED: `.venv/bin/python -m unittest tests.test_ingestion_module_split_contracts -v`
  - Result: expected failure. `app.web.ingestion.registry` was not importable.
- GREEN: `.venv/bin/python -m unittest tests.test_ingestion_module_split_contracts -v`
  - Result: PASS, 3 tests.
- Compile: `.venv/bin/python -m py_compile app/web/ingestion/page.py app/web/ingestion/registry.py app/web/ingestion_console.py`
  - Result: PASS.
