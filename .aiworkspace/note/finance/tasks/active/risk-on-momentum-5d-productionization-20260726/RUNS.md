# Risk-On Momentum 5D Productionization Runs

## 2026-07-26 Baseline

### Actual Top1000 Two-Year Timing

Range: `2024-07-26` through `2026-07-24`

| Stage | Result |
|---|---|
| universe | 0.034s, 1,000 symbols |
| prices | 3.006s, 610,253 rows, 1,002 symbols |
| statements | 0.250s, 9,930 rows, 953 symbols |
| macro | 0.055s, 7,583 source rows, 632 score rows |
| features | 3.008s, 609,005 rows, 31 columns |
| primary | 18.616s, 500 days, 340 trades, 6,130 scanner rows |
| three random variants | 55.631s |
| total diagnostic | 80.621s |

The diagnostic called domain/loaders directly and did not write a backtest artifact.

### Profile

- approximately 318.9 million profiled calls in the measured process
- approximately 15.7 million `Series.__getitem__` calls
- approximately 496,000 `DataFrame.iterrows` rows
- `_rank_candidates` itself was not the dominant single-run Python cost

### Baseline Tests

Command:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.RiskOnMomentumSwingContractTests \
  tests.test_backtest_risk_on_governance
```

Result: PASS, 13 tests.

Broader evidence-inventory command: 21 tests run, one pre-existing literal-source drift failure.

## Pending

- RED/GREEN TDD commands
- focused regression suite
- actual optimized two-year timing
- Browser QA
- compile/diff/hygiene checks
