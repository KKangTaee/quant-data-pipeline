# Runs

## 2026-06-20

- RED: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "source_confidence_catalog_surfaces_provider_caveats or does_not_mark_events_and_data_health_meta or groups_reference_and_meta or summarizes_existing_context_snapshots"`
  - Result: failed as expected. Events/Data Health still counted as unresolved review items; source confidence UI did not render reference/meta grouping; top Market Context summary still used raw Data Health review count.
- GREEN focused: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "source_confidence_catalog_surfaces_provider_caveats or does_not_mark_events_and_data_health_meta or groups_reference_and_meta or summarizes_existing_context_snapshots"`
  - Result: `4 passed, 367 deselected in 0.40s`.
- Verification before Browser QA:
  - `git diff --check`: passed.
  - `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/jobs/overview_actions.py`: passed.
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`: `371 passed, 3 warnings in 12.82s`.
- Browser QA: `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`, then `http://localhost:8525` > `Workspace > Overview > Market Context`.
  - Result: top status changed to `자료 보강 필요` / `보강 가능 자료 3개`; source confidence collapsed summary shows `보강 1`, `참고 2`, `부족 0`; expanded source ledger separates `브리프 자료` from `참고 / 관리 메타`.
  - Events visible state: `참고 제한`, not `자료 확인 필요`.
  - Data Health visible state: `관리 메타`, not `자료 확인 필요`.
  - Refresh assist still shows `현재 이슈만 보강`, `전체 Market Context 자료 보강`, and Events under `보강 제외`.
  - Screenshot artifact: `overview-market-context-source-actionability-v8-qa.png` (generated, do not stage).
- Final verification after Browser QA / cleanup / docs sync:
  - `git diff --check`: passed.
  - `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/jobs/overview_actions.py`: passed.
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`: `371 passed, 3 warnings in 13.64s`.
