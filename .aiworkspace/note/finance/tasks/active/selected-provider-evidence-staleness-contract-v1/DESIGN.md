# Selected Provider Evidence Staleness Contract V1 Design

Status: Complete
Created: 2026-05-29

## Contract

Runtime contract:

- Existing parent: `selected_provider_evidence_v1`
- Nested staleness contract: `selected_provider_evidence_staleness_contract_v1`
- Required provider areas:
  - `ETF Operability`
  - `ETF Holdings`
  - `ETF Exposure`

## Status Policy

Provider row status is the maximum severity of:

- diagnostic status
- coverage source
- coverage weight
- freshness

Policy mapping:

| Evidence | Selected Monitoring Status |
|---|---|
| actual / official coverage, fresh evidence, sufficient weight | `PASS` |
| stale freshness | `REVIEW` |
| partial / bridge / proxy / mixed coverage | `REVIEW` |
| positive but less than 80% coverage weight | `REVIEW` |
| missing required area | `NEEDS_INPUT` |
| zero required coverage | `NEEDS_INPUT` |
| error / blocked row | `BLOCKED` |

The look-through board now adds a selected monitoring policy row so holdings / exposure coverage cannot look ready when the compact board says otherwise.

## Storage Boundary

This task reads selected component contracts and existing provider DB context through the current runtime path.
It does not collect provider data, write provider rows, append monitoring logs, save user comments, create presets, approve trades, create orders, or rebalance anything.
