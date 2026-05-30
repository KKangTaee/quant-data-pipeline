# Risks

- Existing DBs need `sync_market_intelligence_tables` or any event collector run to add new lifecycle columns before direct SQL reads can rely on them.
- Superseded rows remain in DB for auditability; Overview hides them by default.
