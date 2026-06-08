# Robustness Experiment Registry Design

Status: Active
Created: 2026-06-08

## Minimal Run-Set Contract

`robustness_run_set` is a compact read model, not a new full experiment storage table.

Minimum fields:

| Field | Meaning |
|---|---|
| `schema_version` | Contract version for the run-set summary |
| `robustness_run_set_id` | Stable-ish id derived from validation/source/strategy inputs |
| `strategy_family` / `strategy_key` | Candidate strategy identity |
| `source_id` / `selection_source_id` | Product workflow source reference |
| `promotion_contract_reference` | Optional Strategy Promotion Contract or report reference |
| `frozen_parameter_set` | Compact parameter snapshot used by this evidence |
| `experiment_types` | Which evidence classes are present |
| `is_oos_window` | In-sample / OOS or holdout compact window summary |
| `walk_forward_summary` | Walk-forward status, rows/windows, key metric, next action |
| `regime_split_summary` | Regime status and compact macro split summary |
| `cost_slippage_sensitivity_summary` | Cost / slippage status and summary from realism/robustness evidence |
| `parameter_perturbation_summary` | Parameter or runtime follow-up sensitivity status |
| `not_run_review_blocked_evidence` | Compact non-pass evidence rows; `NOT_RUN` is never pass |
| `generated_artifact_references` | Paths/references only; no full artifact payload |
| `decision_effect` | How Practical Validation / Final Review should treat this run-set |
| `storage_boundary` | Explicit no full logs / no raw provider / no live action boundary |

## Implementation Shape

- Create a Streamlit-free service helper under `app/services/`.
- Reuse existing Practical Validation result fields; do not execute strategy variants.
- Attach the run-set summary beside `robustness_validation` so existing Robustness Lab renderers can stay as display/evidence surfaces.
- Let Final Review packet and saved decision evidence rows read the same summary as provenance.
- Keep the first suite small: one validation/source payload at a time, based on existing compact evidence.

## Non-Pass Handling

- `BLOCKED` dominates the run-set status.
- `NEEDS_INPUT` and `NOT_RUN` are missing evidence, not pass.
- `REVIEW` remains open review unless policy marks it as selected-route blocker.
- A mixed `PASS` plus `NOT_RUN` set is `REVIEW`, not `PASS`.
