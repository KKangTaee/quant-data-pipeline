# Institutional Portfolios Watchlist / Mapping V1 Status

- 2026-07-12: User approved 1차~4차 development sequence after source / DB audit.
- 2026-07-12: RED tests added for expanded guru alias rail, alias manager search, ambiguous mapping block, and separated price action states.
- 2026-07-12: 1차 completed. Expanded seed watchlist now includes Duquesne / Stanley Druckenmiller, Bridgewater / Ray Dalio, Third Point / Daniel Loeb, Icahn, Tiger Global, Lone Pine, Soros, and Akre. `institutional_13f_manager_watchlist` has a read-only loader boundary.
- 2026-07-12: 2차 completed. Manager choices merge SEC manager search, DB/seed watchlist CIKs, and alias metadata. Alias-matched CIKs sort before generic seed managers.
- 2026-07-12: 3차 completed. Service read model treats explicit / source-marked ambiguous CUSIP-symbol mappings as unresolved for chart/performance ticker use.
- 2026-07-12: 4차 completed. Selected-security price action payload separates `symbol_missing`, `mapping_ambiguous`, `price_missing`, and `ready`; React renders reason copy without making mapping issues look like refreshable price gaps.
- 2026-07-12: Browser QA found that search-active manager rail rendering still prepended the full seed list. Added a follow-up regression and changed the payload path so search-active rails preserve manager result order and prefer the query-matched selection.
