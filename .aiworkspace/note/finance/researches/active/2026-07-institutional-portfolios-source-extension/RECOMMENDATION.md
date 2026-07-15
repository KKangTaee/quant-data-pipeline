# Institutional Portfolios Source Extension Recommendation

Status: Active
Last checked: 2026-07-12

## Recommended Direction

1. Keep SEC official 13F as the primary source for holdings.
2. Treat "guru" as a curated manager watchlist and alias layer, not a separate data source.
3. Populate or implement `institutional_13f_manager_watchlist` for manager aliases:
   - Stanley Druckenmiller -> Duquesne Family Office LLC / CIK `0001536411`
   - Ray Dalio -> Bridgewater Associates, LP / CIK `0001350694`
   - Daniel Loeb -> Third Point LLC / CIK `0001040273`
   - David Einhorn -> Greenlight-related filer mapping needs review.
   - Carl Icahn -> Icahn Capital LP / CIK `0001412093` and related CIKs need review.
4. Update manager search to include alias/watchlist labels, so users can search investor names rather than exact SEC filer names.
5. Harden CUSIP-symbol mapping before expanding performance/chart features:
   - avoid joining on CUSIP alone when multiple symbols exist;
   - prefer exact verified rows where `issuer_name` matches the holding issuer;
   - mark ambiguous mappings as unresolved instead of showing the wrong ticker;
   - consider OpenFIGI or a licensed mapping provider as a separate ingestion step.
6. Keep Dataroma / WhaleWisdom / Fintel as reference links and UX benchmarks unless a permitted API/license path is available.

## Suggested Development Sequence

1. Alias/watchlist V1: add DB-backed curated manager watchlist + alias search.
2. CUSIP mapping audit: surface unmapped/ambiguous holdings and prevent wrong chart links.
3. Mapping enrichment adapter: evaluate OpenFIGI or licensed provider behind `finance/data/* -> DB -> loader`.
4. Guru seed expansion: add a reviewed seed list for prominent managers using SEC CIKs, external reference links, and caveats.
5. UI copy: make it clear when a manager exists in 13F DB but is not in the curated rail.
