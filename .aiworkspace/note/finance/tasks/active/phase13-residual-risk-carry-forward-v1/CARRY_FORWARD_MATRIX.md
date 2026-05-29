# Phase 13 Residual Risk / Carry-Forward Matrix V1

Status: Complete
Created: 2026-05-30

## Summary

Triage result: `QA_PASS`

The first hardening cycle can be closed as an investability evidence workflow improvement.
It should not be described as a broker-grade trading, account reconciliation, optimizer, or production monitoring system.

## Current Product Limitations

These limitations remain true after Phase 8~12 and should be stated in final closeout.

| Area | Current limitation | Why it matters | Current guardrail |
| --- | --- | --- | --- |
| Historical membership / survivorship | No complete free historical membership feed is implemented. Nasdaq Daily List remains parked because it is subscription / approval based. | Current / partial evidence cannot prove all historical investability by itself. | Data Coverage Audit separates current snapshot, SEC identity, computed partial, actual coverage, and delisting actual; survivorship PASS requires actual requested-period coverage. |
| Lifecycle evidence | SEC Form 25 is delisting evidence, not full membership history. Computed snapshot rows remain partial. | Delisting evidence improves survivorship control but does not fully reconstruct index / exchange membership. | Lifecycle proof class and `coverage_status` keep partial evidence from becoming PASS. |
| Cost / slippage / liquidity | No broker-grade execution simulator or market impact model exists. | Backtest Realism can flag missing / weak evidence but cannot forecast real execution quality at broker level. | Backtest Realism Audit separates cost source, net cost proof, turnover, liquidity / capacity, sensitivity, and execution boundary. |
| Weighted / saved mix realism | Component-level cost / turnover aggregation for weighted / saved mixes is still shallow. | Multi-component portfolios may understate aggregate friction. | Missing or weak cost / turnover evidence stays `REVIEW` or `NEEDS_INPUT`; selected-route gate surfaces non-PASS rows. |
| Temporal validation | Walk-forward / OOS / regime checks are compact evidence heuristics, not a formal statistical significance framework. | Good-looking full-period results may still be overfit. | Validation Efficacy Audit surfaces temporal / OOS / regime non-PASS rows into Final Review gate evidence. |
| Threshold tuning | Cost, liquidity, temporal, construction, and selected monitoring thresholds are not fully profile-specific. | A defensive portfolio and aggressive portfolio may need different tolerance. | Existing profile-aware gates block or require review for critical non-PASS evidence. |
| Construction risk model | No full optimizer, issuer / sector taxonomy engine, covariance model, or broker-grade construction platform exists. | Concentration / overlap / correlation risk may need richer modeling before allocation sizing. | Construction Risk, Risk Contribution, and Component Role / Weight audits expose compact evidence and selected-route blockers. |
| Provider evidence quality | Provider holdings / exposure / operability quality depends on DB-backed snapshots collected separately. | Missing, stale, partial, bridge, or proxy evidence can weaken investability claims. | Provider evidence is downgraded to `REVIEW` / `NEEDS_INPUT`; UI does not treat stale provider data as PASS. |
| Selected recheck | Recheck conclusions depend on selected replay contracts and DB market data coverage. | A selected portfolio may become stale or unreplayable after selection. | Recheck Operations Preflight, Readiness, Symbol Freshness, and Recheck Comparison expose missing / stale / breached evidence. |
| Actual allocation | Actual Allocation is manual / session-only evidence and does not prove real brokerage holdings. | Drift review cannot be treated as account reconciliation. | Allocation evidence boundary disables raw input persistence, alert persistence, account sync, order, and auto rebalance. |
| Storage model | Some V2 JSONL paths are runtime-defined and may not exist until first write; legacy registries remain for compatibility. | Future agents could confuse absent files or legacy files with current source-of-truth. | Storage Governance and Phase Closeout QA runbook clarify DB / JSONL / saved / generated artifact boundaries. |
| Waiver policy | Structured waiver policy exists as policy only; no waiver UI / persistence is implemented. | Review-required gaps cannot yet be formally waived in-product. | `BLOCK` remains non-waivable; future waiver must be scoped and compact if approved. |

## Second-Cycle Candidates

These are good candidates for a future phase only after user approval.

| Candidate | Source risk | Candidate goal | Suggested owner / skill | Priority |
| --- | --- | --- | --- | --- |
| Historical membership coverage expansion | Phase 8 residual | Find and integrate a stronger free / approved historical membership source, or explicitly evaluate paid / approval-based options without committing to them. | `finance-db-pipeline` + product research if source selection is needed | High |
| Lifecycle actual coverage scoring v2 | Phase 8 residual | Improve period coverage scoring, archive continuity assumptions, and actual / partial promotion rules. | `finance-db-pipeline` + `finance-backtest-web-workflow` | Medium |
| Broker-grade execution realism design | Phase 9 residual | Design a broker-aware execution / market impact realism layer before any implementation. | product research first, then `finance-strategy-implementation` / `finance-backtest-web-workflow` | High |
| Weighted mix cost / turnover aggregation | Phase 9 residual | Aggregate component-level cost, turnover, liquidity, and capacity evidence for weighted / saved mixes. | `finance-strategy-implementation` + `finance-backtest-web-workflow` | High |
| Profile-specific threshold policy | Phase 9~12 residual | Define profile-specific thresholds for liquidity, temporal validation, construction risk, and monitoring signals. | `finance-backtest-web-workflow` | High |
| Formal validation statistics layer | Phase 10 residual | Add significance / confidence / overfit indicators around walk-forward, OOS, and regime evidence. | `finance-strategy-implementation` | Medium |
| Construction taxonomy / covariance model | Phase 11 residual | Add issuer / sector taxonomy, covariance / risk model, and richer component diversification checks. | `finance-db-pipeline` + `finance-backtest-web-workflow` | Medium |
| Provider snapshot operations hardening | Phase 11~12 residual | Make provider snapshot collection health, stale coverage, and source map gaps more operationally visible. | `finance-db-pipeline` + `finance-backtest-web-workflow` | Medium |
| Selected replay contract hardening | Phase 12 residual | Reduce fallback dependency on legacy Current Candidate Registry by strengthening Final Decision V2 replay contract completeness. | `finance-backtest-web-workflow` | High |
| Production monitoring design | Phase 12 residual | Design notification / alerting policy without auto-trading or memo storage. | product research first, then `finance-backtest-web-workflow` | Low |
| Structured waiver implementation review | Policy residual | Decide whether limited `REVIEW_REQUIRED` waiver UI / compact final decision snapshot is worth implementing. | `finance-backtest-web-workflow` + `finance-doc-sync` | Low |

## Explicit Out Of Scope For The First Cycle

These items must not be claimed as complete in 13-6.

| Item | Boundary |
| --- | --- |
| Live approval system | Final Review selection is a decision record, not a trade approval workflow. |
| Broker order generation | No order draft, order ticket, execution routing, or broker API integration exists. |
| Account synchronization | Selected Dashboard does not connect to brokerage accounts or prove holdings. |
| Tax-lot handling | No tax-lot, wash-sale, realized gain, or tax-aware rebalance engine exists. |
| Automatic rebalance | Allocation drift can show a review signal, but it does not generate or execute rebalance orders. |
| Broker-grade construction platform | Construction audits are evidence surfaces, not a full portfolio optimizer / OMS. |
| Production alerting | Review Signals are read-only evidence, not notification infrastructure. |
| Paid / premium data source adoption | Nasdaq Daily List and other paid / approval sources are not adopted in this cycle. |
| User memo / preset expansion | Phase 13 does not add memo, preset, or closeout-comment persistence. |
| Automatic monitoring log append | Selected monitoring logs remain explicit-user-action only. |

## Safe Final Closeout Statements

13-6 may say:

- The first hardening cycle improved investability evidence from lifecycle / survivorship through selected monitoring.
- Critical missing / stale / partial / blocked evidence is now more visible across Practical Validation, Final Review, and Selected Dashboard.
- Final Review and Selected Dashboard remain non-trading, non-order, non-auto-rebalance workflows.
- Storage boundaries were rechecked and no new memo / preset / auto monitoring log behavior was introduced.

13-6 should not say:

- The product is broker-grade ready.
- The product can place or approve trades.
- Historical membership coverage is complete.
- Backtest realism fully models market impact.
- Walk-forward / OOS / regime checks are statistically conclusive.
- Selected Dashboard proves real account holdings or performs rebalance.

## Next Step

Phase 13 final closeout is complete.
Use this matrix as the input to Phase 14:

- active phase: `.aiworkspace/note/finance/phases/active/phase14-second-cycle-prioritization/`
- next task: `phase14-candidate-prioritization-v1`

Use this matrix with:

- `phase13-cycle-inventory-v1/INVENTORY.md`
- `phase13-gate-validation-qa-matrix-v1/QA_MATRIX.md`
- `phase13-storage-data-boundary-audit-v1/STORAGE_AUDIT.md`
- `phase13-docs-runbook-alignment-v1/DOC_ALIGNMENT.md`
- `docs/runbooks/PHASE_CLOSEOUT_QA.md`
