# Investability Decision Foundation Integration

Status: Active
Created: 2026-05-28

## Worktree Boundary

This phase belongs to `main-dev`.

| Work type | Preferred worktree |
| --- | --- |
| phase policy, task graph, integration sequencing | `main-dev` |
| candidate search / strategy discovery | `research` |
| phase-out-of-scope UX polish | `sub-dev` |
| Backtest / Practical / Final Review implementation | `main-dev` unless delegated as a scoped task |

## Conflict-Prone Files

| File / Area | Why |
| --- | --- |
| `app/services/backtest_evidence_read_model.py` | packet, gate, selected dashboard evidence read model share this service |
| `app/web/backtest_final_review.py` | visible Final Review packet and decision entry UI |
| `app/web/backtest_final_review_helpers.py` | final decision save evaluation and row construction |
| `app/services/backtest_practical_validation_provider_context.py` | provider / macro provenance and freshness read model share this service |
| `app/services/backtest_practical_validation_diagnostics.py` | Practical Validation result schema includes compact provider coverage summary |
| `app/services/backtest_practical_validation_stress_sensitivity.py` | stress / rolling / sensitivity / overfit evidence and Robustness Lab board share this helper |
| `app/web/backtest_practical_validation.py` | Provider Coverage, Look-through Board, Provider Data Gaps share the same visible validation area |
| `tests/test_service_contracts.py` | focused contract tests for read model / gate behavior |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | active work map |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | user-facing workflow semantics |
| `.aiworkspace/note/finance/docs/data/` | data source / DB / JSONL meaning when provenance work lands |

## Integration Order

1. Phase 0 policy docs and roadmap sync.
2. Gate hardening task.
3. Storage governance audit.
4. Data provenance and provider coverage contract.
5. Look-through board.
6. Robustness Lab.
7. Monitoring timeline.
8. Decision dossier / report.

## Verification Baseline

Documentation-only phase work:

```bash
find .aiworkspace/note/finance/phases/active/investability-decision-foundation -maxdepth 1 -type f | sort
git diff --check
```

Backtest / Final Review visible changes:

```bash
.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review_helpers.py app/web/backtest_final_review.py tests/test_service_contracts.py
.venv/bin/python -m unittest tests/test_service_contracts.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Use Browser smoke when visible Streamlit behavior changes.

## Commit Policy

- Commit coherent phase / task units.
- Do not stage `.DS_Store`, run history, run artifacts, temp CSV, registries, or saved setup unless explicitly requested.
- For phase docs, commit the phase bundle and minimal roadmap / root log sync together.
