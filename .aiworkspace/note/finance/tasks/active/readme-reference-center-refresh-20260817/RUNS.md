# Runs

## 2026-08-17

- `git status --short`: tracked 변경 없음, 기존 untracked QA screenshots 4개만 확인.
- Read `README.md`, `app/services/reference_center.py`, `app/web/reference_center.py`, `tests/test_reference_center.py`.
- Read `app/web/overview/navigation.py`: current Market Research families are `시장 환경 / 지수 가치평가 / 종목 리서치`; views are `경기 국면`, `물가·정책`, `선물 매크로`, `심리`, `일정`, `S&P 500`, `변동 종목`, `개별 종목`.
- Read `app/web/streamlit_app.py`: current top navigation is `Research / Portfolio / Data / Help`.
- Stale-label scan over README / Reference Center code / test found only intended `FORBIDDEN_USER_LABELS` guard constants in `app/services/reference_center.py`.
- `.venv/bin/python -m py_compile app/services/reference_center.py app/web/reference_center.py`: pass.
- `.venv/bin/python -m unittest tests.test_reference_center`: 15 tests ran, OK.
- Reference Center drift report: `PASS`, 27 catalog items, missing surfaces `[]`, forbidden user labels `[]`.
- `git diff --check`: pass.
- Final hard-stale scan for old route/worktree-specific labels over README, Reference Center code/test, and this task: no matches.
- Final conflict marker scan over README, Reference Center code/test, and this task: no matches.
- Final `.venv/bin/python -m py_compile app/services/reference_center.py app/web/reference_center.py`: pass.
- Final `.venv/bin/python -m unittest tests.test_reference_center`: 15 tests ran, OK.
- Final Reference Center drift report: `PASS`, 27 catalog items, missing surfaces `[]`, forbidden user labels `[]`.
- Final `git diff --check`: pass.
