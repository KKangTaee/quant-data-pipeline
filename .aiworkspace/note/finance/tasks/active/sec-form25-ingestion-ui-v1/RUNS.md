# SEC Form 25 Ingestion UI V1 Runs

## 2026-05-28

| Command | Result |
|---|---|
| `.venv/bin/python -m py_compile app/web/streamlit_app.py app/jobs/ingestion_jobs.py finance/data/sec_delisting.py` | PASS |
| `.venv/bin/python -m unittest tests.test_service_contracts.SecForm25DelistingCollectorContractTests` | PASS, 3 tests |
| `.venv/bin/python -m unittest tests.test_service_contracts` | PASS, 66 tests |
| `git diff --check` | PASS |
| `.venv/bin/streamlit run ... --server.port 8501` | Failed: stale shebang points at old `phase` worktree |
| `.venv/bin/python -m streamlit run ... --server.port 8501` | Failed: port 8501 unavailable |
| `.venv/bin/python -m streamlit run ... --server.port 8502` | PASS: app served at `http://localhost:8502` |
| Browser check | PASS: Ingestion page opens, `Delisting Evidence` tab / run button / Form 25 limitation copy visible |
