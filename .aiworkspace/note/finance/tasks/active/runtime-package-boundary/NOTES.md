# Runtime Package Boundary Notes

## Findings

- `app/web/runtime/backtest.py` is the largest module at about 5,100 lines.
- Registry / saved setup helpers under `app/web/runtime` are small JSONL repository modules and are not Streamlit renderers.
- Existing boundary lint reports `app.services -> app.web.runtime` as advisory transition debt.
- After 5-01, boundary lint exposed one runtime-to-web helper dependency in Selected Portfolio Dashboard replay.
- `app/web/backtest_candidate_library_helpers.py` was also Streamlit-free, so 5-02 moved it to `app/runtime/candidate_library.py`.
