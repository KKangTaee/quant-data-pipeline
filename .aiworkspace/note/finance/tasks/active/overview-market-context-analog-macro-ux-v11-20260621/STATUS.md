# Status

Status: Complete

## Progress

- 2026-06-21: User confirmed V11 implementation after guideline review.
- 2026-06-21: Started task record for historical analog and Macro comparison structural UX.
- 2026-06-21: Added RED HTML contract tests for basis bar, method grid, insight split, separate Macro comparison section, and condition-role groups.
- 2026-06-21: Reworked `Overview > Market Context` historical analog UI to use a basis bar, method grid, summary strip, insight split, and sibling Macro comparison section.
- 2026-06-21: Browser QA confirmed latest / selected 기준 시점 and 20D / monthly pattern changes rerender the analog section.

## Result

- Historical analog no longer renders its basis as the old `ov-analog-basis-ledger`; it now shows requested date, actual calculation date, sector, proxy, pattern, sample, and data window in a wide basis bar.
- The old explanation blob is replaced with `현재 기준`, `유사 사례 조건`, and `표본 품질`.
- Macro conditioned comparison now renders as a separate `ov-macro-compare-section` after the broad analog section, with funnel, broad-vs-conditioned lanes, condition-role groups, and dimension audit details.
- Boundaries stayed unchanged: DB-backed read model only, no render-time provider fetch, no schema / registry / saved write, no validation / monitoring / trading semantics, and no FRED / events / sentiment hard conditioning.

## Next

- Future polish can further reduce Macro detail typography density, but the structural split is in place.
