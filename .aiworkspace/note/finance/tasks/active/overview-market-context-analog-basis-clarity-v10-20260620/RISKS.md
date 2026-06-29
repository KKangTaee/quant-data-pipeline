# Risks

- Current service uses current universe / sector metadata for selected-as-of replay. Full PIT sector membership remains out of scope.
- If comparison asset daily prices are stale, selected recent dates may still be bounded to an older common matrix date until data is refreshed.
- UI must avoid implying prediction guarantee, recommendation, or trading signal.
- The current date picker still lets users choose dates beyond usable common price coverage; the new warning explains the fallback instead of disabling those dates.
