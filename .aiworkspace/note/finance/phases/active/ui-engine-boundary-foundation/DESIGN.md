# UI Engine Boundary Foundation Design

Status: Draft
Created: 2026-05-19

## Boundary Rules

| Layer | Owns | Must Avoid |
| --- | --- | --- |
| `app/web/*` | Streamlit render, forms, session state, navigation, user feedback | direct strategy internals, long business workflow logic, duplicated runtime dispatch |
| `app/services/*` | use-case orchestration, request/result contract, UI-independent execution boundary | `streamlit` import, widget/session state access, direct UI rendering |
| `app/web/runtime/*` | existing DB-backed runtime adapters and JSONL helpers | becoming a second UI layer or public API surface without contracts |
| `finance/loaders/*` | DB read path and PIT/freshness data access | UI state or Streamlit feedback |
| `finance/data/*` | ingestion, normalization, persistence | UI-triggered remote fetch outside jobs |
| `finance/engine.py`, `finance/strategy.py`, `finance/transform.py`, `finance/performance.py` | core strategy execution, transforms, simulation, metrics | UI payload parsing or Streamlit dependency |

## Current Coupling Map

| Area | Current Coupling | First Treatment |
| --- | --- | --- |
| Single Strategy | `backtest_single_runner.py` dispatches strategy runtime, handles Streamlit feedback, writes session state, appends history | Move dispatch/error normalization to `app/services/backtest_execution.py` |
| Compare | `backtest_compare.py` owns runner registry, execution, weighted portfolio, saved replay, chart render, session state | Audit first; split execution after Single Strategy pattern is stable |
| Practical Validation | UI renders diagnostics and provider gap actions; service now owns source/result append and handoff contract; helper builds source/profile/diagnostics without Streamlit | Later split provider gap job orchestration and possibly move the large diagnostic builder |
| Selected Dashboard | runtime read model is already mostly Streamlit-free, but imports a web helper for candidate replay | Audit dependency and move replay/read model toward service layer |
| Ingestion | `streamlit_app.py` triggers `app/jobs/ingestion_jobs.py` wrappers | Not in first implementation; keep job wrappers as engine-adjacent boundary |

## Service Contract Shape

Phase A does not require Pydantic or FastAPI.
Use plain Python dataclasses or typed dict-compatible dictionaries first, as long as outputs are JSON-compatible.

Candidate first contract:

```text
BacktestExecutionRequest
  payload: dict
  strategy_name: str

BacktestExecutionResult
  ok: bool
  bundle: dict | None
  error_kind: input | data | system | None
  error_message: str | None
  elapsed_seconds: float
```

The service may call existing `app/web/runtime/backtest.py` functions during the transition.
The important boundary is that it does not render UI and does not touch `st.session_state`.

## Migration Principles

- Move behavior before changing behavior.
- Preserve existing result bundle keys.
- Preserve existing Streamlit session keys until a later state cleanup task.
- Keep registry append-only semantics.
- Do not rewrite history or registry JSONL files.
- Do not move DB/loader logic into `app/services`.
- Do not make service layer depend on a future UI choice.

## Validation Principles

Minimum checks for each extraction:

- `python -m py_compile` for touched modules
- import smoke for new `app/services/*`
- no `streamlit` import under new service module
- focused behavior parity for error kind and result bundle handoff
- `git diff --check`

Manual UI validation is reserved for changes that alter render, form, state, or navigation behavior.
