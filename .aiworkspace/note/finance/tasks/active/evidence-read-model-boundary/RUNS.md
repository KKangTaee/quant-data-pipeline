# Evidence Read Model Boundary Runs

Commands and verification for this task.

## 2026-05-20

- Inspected phase board and current docs.
- Inspected Final Review helpers, Selected Dashboard helpers, and selected portfolio runtime read model.
- Added `app/services/backtest_evidence_read_model.py`.
- Updated Final Review helper and Selected Dashboard helper to consume the shared read model.
- Ran `py_compile` for the new service and affected Final Review / Selected Dashboard modules: pass.
- Ran service import smoke and confirmed `streamlit_loaded False`: pass.
- Ran no-Streamlit boundary check on the service: pass.
- Ran `git diff --check`: pass.
