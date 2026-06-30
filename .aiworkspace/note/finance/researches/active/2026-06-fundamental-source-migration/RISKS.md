# Risks

## Data correctness risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| 10-K FY values enter quarterly shadow as if they were Q4 | Quarterly factors and backtests become materially wrong | Block quarterly promotion until Q4/FY policy is fixed |
| EDGAR concept mapping misses company-specific taxonomy concepts | Missing or wrong normalized fields | Keep raw ledger, add concept fallback audit, sample top sectors |
| Shares outstanding fallback still uses broad yfinance | EPS/PER can remain partly non-canonical | Replace with SEC `dei` / statement concepts or explicit profile fallback label |
| Amendments/restatements are not fully modeled | Backtest may use later corrected data incorrectly | Decide first-available vs latest-amended policy per read model |
| available_at fallback uses end of filing date when accepted timestamp missing | Slight timing approximation | Prefer accepted timestamp; mark fallback basis |

## Migration risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Removing yfinance loaders before consumers migrate | Backtest/UI regression | Deprecate first, then hide, then delete |
| Broad coverage shrinks from 5,500 symbols to EDGAR current 989 symbols | Some screens lose broad symbol coverage | Expand EDGAR universe collection before removal |
| Old saved backtests expect `quality_snapshot` | History replay or comparison confusion | Keep legacy path with explicit label |
| Ingestion Console becomes too operational again | User sees jobs, rows, failures instead of source trust | Keep status compact; raw diagnostics in expander |

## Operational risks

- SEC fair-access policy requires responsible request pacing and identity.
- `edgartools` wrapper behavior can change across versions.
- Direct SEC API migration would require adapter work but can preserve current DB schema.
- Paid provider adoption requires license and cost decision before DB canonical use.

## Current blockers before full EDGAR migration

1. Quarterly shadow 10-K/FY policy.
2. Market Movers detail loader still defaults to broad yfinance.
3. Legacy `quality_snapshot` still uses `nyse_factors`.
4. Source/freshness contract not uniformly exposed in UI/read models.
5. `nyse_fundamentals_statement` coverage should be expanded if Top2000/Nasdaq workflows need fundamentals.
