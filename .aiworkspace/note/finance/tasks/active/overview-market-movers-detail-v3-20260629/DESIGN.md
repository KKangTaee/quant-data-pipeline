# Overview Market Movers Detail V3 Design

## Ownership

- Market Movers UI: `app/web/overview/market_movers_helpers.py`
- Why It Moved read model / metadata helpers: `app/services/overview/why_it_moved.py`
- Contract tests: `tests/test_service_contracts.py`

## UI Flow

1. User selects Coverage / Period / Sector / Top N / exploration mode.
2. Main panel renders the selected mode rows and chart.
3. `선택 종목 조사` selectbox is sourced from the current symbol-level mode rows. If the selected exploration mode is sector-level, it falls back to Top Gainers symbol rows.
4. Detail area shows:
   - `종목`: symbol, name, sector, industry, market cap.
   - `랭킹 맥락`: selected mode / rank / period / coverage.
   - `가격 / 거래량`: return, previous return, momentum delta, relative volume when available, current volume, 10D baseline, volume basis, dollar volume.
   - `같은 섹터 맥락`: visible same-sector position and average return within the displayed rows.
5. Metadata state strip shows lookup status, News, Korean News, SEC, fetched-at, and session-only storage boundary.
6. `조사 단서` tabs show compact metadata tables when present and outbound search links otherwise.

## Boundary

The UI does not infer why a stock moved. It only selects a mover row and renders the existing Why It Moved service read model. Metadata lookup is button-only, selected-symbol-only, compact, and session-only. It does not store article body, filing body, AI summary, registry rows, or DB rows.
