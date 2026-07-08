# Risks

- The 1차 mode label is still `Return Rank`; 2차 must replace this with explicit exploration modes such as Top Gainers / Top Losers / Most Active / Unusual Volume / Sector Leaders.
- `pytest` is not installed in the current venv, so requested pytest verification may require fallback to `unittest` unless the environment is updated.
- Browser QA confirmed the narrow viewport keeps controls / command strip / empty state available, but 2차 mode controls may need a tighter mobile treatment once more modes are added.
- Existing untracked/generated files are present in the worktree and must not be staged.
