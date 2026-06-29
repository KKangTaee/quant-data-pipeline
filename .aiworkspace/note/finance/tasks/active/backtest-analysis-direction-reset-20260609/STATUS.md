# Backtest Analysis Direction Reset 4C Status

## 2026-06-09

- Started after user review found 3A~4B direction had drifted toward evidence/log/workbench panels.
- 4C promotion/provider work is paused.
- New 4C scope is Backtest Analysis execution-first UX recovery and advanced reference panel demotion.
- Existing untracked generated run history JSONL remains out of scope.
- Implemented `app/services/backtest_analysis_research_board.py` to classify Reference help and 3A~4B panels as hidden-by-default strategy development references.
- Reordered `app/web/backtest_analysis.py` so Single Strategy / Portfolio Mix Builder render before the reference / evidence panels.
- Browser QA verified old evidence panel titles are absent from the default body and the `전략 개발 참고 패널 열기` control reveals the panels when selected.
