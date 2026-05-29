# Backtest Analysis UX Checkpoint V1 Risks

## Known Risks

- UI-only copy changes can still break service-contract tests if assertions depend on exact labels.
- Browser smoke should verify that the new CSS components render without overlapping Streamlit tabs.

## Residual

- Service contract tests were not executed because `pytest` is not installed in the active `.venv`.
- Browser smoke used an Equal Weight run; GTAA should still be checked by the user during manual UX review because Selection History availability differs by strategy.
