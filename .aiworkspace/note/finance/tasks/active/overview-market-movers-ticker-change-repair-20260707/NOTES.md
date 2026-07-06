# Notes

- Trigger example: `SATS` and `VSCO` were present in Top1000 / Top2000 liquidity universes but Yahoo quote returned no row for old tickers.
- External check showed official ticker changes: `SATS -> ECHO` effective 2026-06-24 and `VSCO -> VSXY` effective 2026-06-02.
- Product policy: detect automatically, apply only through explicit user action first; after alias is stored, future quote snapshot collection should use the alias automatically.
- Implementation shape: `market_symbol_alias.status=candidate` is surfaced in coverage trust; `status=active` is used only after the user runs `티커 변경 복구 적용`.
- Active alias changes provider quote lookup only. `market_intraday_snapshot.symbol` remains the universe symbol and `quote_symbol` records the actual replacement ticker.
- User workflow: `티커 변경 복구 적용` first, then `일중 스냅샷 갱신` to rewrite the latest snapshot rows.
