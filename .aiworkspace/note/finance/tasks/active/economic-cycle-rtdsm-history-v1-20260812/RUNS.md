# Runs

## 2026-08-12 Official Source Exploration

- `EMPLOY`: 1,051 rows × 741 columns, vintages 1964:M12 through 2026:M7
- `H`: 955 rows × 660 columns, vintages 1971:M9 through 2026:M7
- `IPT`: 1,291 rows × 766 columns, vintages 1962:M11 through 2026:M7
- `RUC`: 953 rows × 244 columns, vintages 1965:Q4 through 2026:Q2
- throwaway 4-indicator audit: usable phase months 589, confirmed transitions 117,
  holdout events 30, sample decision `GO_EXPERIMENT`

## 2026-08-12 Actual Ingestion And Gate

- initial actual DB ingest: 1,334,818 rows; EMPLOY 442,176 / H 276,257 /
  IPT 476,181 / RUC 140,204; missing/failed 0; elapsed 48.7s
- incremental overlap run: 3,597 UPSERT rows; missing/failed 0; elapsed 12.2s
- post-run uniqueness: all four series row counts equal distinct business-key counts
- DB-only signal load: 24,156 rows; 659 monthly origins from 1971-09 through 2026-07
- sample: 589 usable origins, 117 events, destination recovery 25 / expansion 33 /
  slowdown 20 / contraction 39; holdout 30 with 6 / 9 / 5 / 10; `GO_EXPERIMENT`
- parity: 142 overlapping months (2014-04 through 2026-01), exact 0.542254,
  Cohen's kappa 0.368198, level-side 0.830986; `NO_GO_PARITY`
- focused new tests: 22 passed
- full focused economic-cycle + RTDSM + ingestion-job regression: 248 passed,
  3 third-party EDGAR deprecation warnings
