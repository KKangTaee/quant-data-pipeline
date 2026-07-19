# Design

Canonical design: `docs/superpowers/specs/2026-07-17-economic-cycle-rates-equities-commodities-pathways-design.md`

Implementation plan: `docs/superpowers/plans/2026-07-17-economic-cycle-rates-equities-commodities-pathways.md`

Data stays inside `source -> ingestion -> DB -> loader -> pathway engine -> Overview service -> React`. Existing tables are reused; EIA weekly XLS rows are stored as official observations in `finance_meta.macro_series_observation`.
