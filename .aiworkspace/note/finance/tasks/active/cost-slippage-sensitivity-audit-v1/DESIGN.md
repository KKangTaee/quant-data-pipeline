# Cost / Slippage Sensitivity Audit V1 Design

Status: Active
Created: 2026-05-29

## Read Model Contract

`cost_slippage_sensitivity_contract_v1`은 기존 validation payload 안의 compact evidence만 읽는다.

주요 입력 후보:

- `cost_slippage_sensitivity`
- `cost_slippage_sensitivity_snapshot`
- `sensitivity_interpretation`
- `robustness_validation.robustness_lab_board`
- `robustness_validation.sensitivity_rows`
- `diagnostic_results[*]`의 `robustness_sensitivity_overfit`
- cost / turnover / net cost curve metadata

## Decision Rules

| Evidence | Contract strength | Audit row |
| --- | --- | --- |
| explicit cost / slippage sensitivity computed and PASS | `explicit_cost_slippage_sensitivity` | PASS |
| explicit cost / slippage sensitivity exists but REVIEW / NOT_RUN / follow-up remains | `explicit_cost_slippage_review` | REVIEW |
| generic robustness sensitivity exists without cost / slippage axis | `generic_sensitivity_only` | REVIEW |
| cost / net curve input missing | `missing_cost_or_net_curve_input` | NEEDS_INPUT |
| no sensitivity evidence but cost baseline exists | `missing_sensitivity_evidence` | REVIEW |

## Storage Boundary

This task only adds read-only contract interpretation.
It must not append to registries, create saved setup, write run artifacts, or persist user comments.
