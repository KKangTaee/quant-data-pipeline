# Overview Market Context Historical Analog V1 Risks

## Open Risks

- Local DB may not have enough sector ETF or comparison ETF price coverage for every sector.
- Current leadership sector labels may not map cleanly to GICS sector names; alias handling must be conservative.
- Sector ETF proxy analog is not the same as historical constituent-level sector leadership and carries PIT/survivorship limitations.
- Forward-return samples can overlap or be too sparse; the MVP needs dedup/minimum sample handling and honest `REVIEW`/`INSUFFICIENT_DATA` status.
- `pytest` may still be unavailable in the local environment; if so, focused `unittest` must be used and documented.

## Closeout Risks

- Current local leadership is `Industrials`, but `XLI` coverage is only 63 rows. The MVP is implemented, but the live UI correctly shows `자료 부족` until sector ETF price coverage is expanded.
- `XLB`, `XLC`, `XLF`, `XLI`, `XLK`, `XLY`, and `UUP` currently have short local histories, so many sector states will produce coverage-limited output.
- The analog threshold is deliberately simple 5D sector ETF relative strength versus SPY. Macro/futures/event conditioning is deferred.
- The feature is Overview context-only and must remain disconnected from strategy signals, validation gate policy, Final Review decisions, and Operations monitoring.
