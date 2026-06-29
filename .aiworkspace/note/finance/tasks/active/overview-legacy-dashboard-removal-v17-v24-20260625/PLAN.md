# Overview Legacy Dashboard Removal V17-V24 Plan

## 이걸 하는 이유?

`app/web/overview/legacy_dashboard.py` is no longer the active page or tab owner, but it still holds lower-level helper bodies and is re-exported by `app/web/overview_dashboard.py`. The goal of V17-V24 is to remove that file rather than keep a hidden legacy hub behind the new tab helpers.

## Roadmap

| Step | Goal | Main files |
|---|---|---|
| V17 | Audit remaining direct dependencies and add deletion guards | tests, task docs |
| V18 | Move market session/banner helpers out of legacy | `page.py`, `session_helpers.py` |
| V19 | Move Market Context refresh helpers out of legacy | `market_context_helpers.py` |
| V20 | Move Events helpers out of legacy | `events_helpers.py` |
| V21 | Move Sentiment helpers out of legacy | `sentiment_helpers.py` |
| V22 | Move Market Movers helpers out of legacy | `market_movers_helpers.py` |
| V23 | Move Futures Macro / remaining futures helpers out of legacy | `futures_macro_helpers.py` |
| V24 | Remove wrapper re-export and delete `legacy_dashboard.py` | `overview_dashboard.py`, tests, docs |

## Completion Criteria

- `app/web/overview/legacy_dashboard.py` is deleted.
- `app/web/overview_dashboard.py` no longer imports or re-exports legacy symbols.
- Active Overview UI still renders the five primary tabs.
- Contract tests, py_compile, diff check, and Browser QA pass.

