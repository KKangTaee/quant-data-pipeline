# Risks

- yfinance calendar structure can vary by ticker. Diagnostics should not assume a single field shape.
- Missing earnings date may mean provider gap, no upcoming date in the selected window, or a ticker mapping issue; labels should preserve that distinction.
- `symbol_diagnostics` is job-result / artifact metadata, not a persisted DB table. Historical missing reasons are retained only in run artifacts / run history, while stored event rows remain successful calendar events.
