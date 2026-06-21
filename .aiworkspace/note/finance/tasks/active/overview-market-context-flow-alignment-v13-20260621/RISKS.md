# Overview Market Context Flow Alignment V13 Risks

- Historical analog still uses current universe / sector metadata for selected as-of replay. Full point-in-time sector membership remains out of scope.
- Canonical sector normalization can change displayed labels slightly when the stored metadata uses provider-specific names.
- If the latest leadership sector ETF has insufficient local daily price history, the analog remains an actionable coverage-gap state until the existing bounded OHLCV refresh path fills those rows.
- The compact macro comparison intentionally does not render when broad analog rows are unavailable; this avoids a misleading conditioned sample comparison but means users first need to repair the broad ETF price coverage.
