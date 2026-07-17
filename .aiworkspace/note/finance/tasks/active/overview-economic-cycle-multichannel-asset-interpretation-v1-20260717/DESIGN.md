# Design Handoff

## Boundaries

- FRED ingestion persists `DGS2`, `DGS10`, `DFII10` in the existing macro table.
- DB-only loaders own reference-date filtering.
- `finance/economic_cycle_asset_pathways.py` owns pure changes, materiality, freshness, and pathway status.
- `finance/economic_cycle_interpretation.py` owns economic-state normalization and deterministic user copy.
- Overview service assembles `economic_cycle_v2`; React only renders the read model.

## UI Contract

White pathway cards, no left color accent, no colored group background, and essential 21/63-day values visible without hover.
