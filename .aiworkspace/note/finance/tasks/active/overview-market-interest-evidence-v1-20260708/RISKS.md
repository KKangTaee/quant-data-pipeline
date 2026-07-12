# Overview Market Interest Evidence V1 Risks

## 13F Caveats

- 13F is delayed quarterly data and can be submitted up to 45 days after quarter-end.
- 13F does not reveal short positions, derivatives, hedges, complete fund-level allocation, or real-time trading intent.
- 13F data can contain filer-provided or extraction errors; users should review original SEC filings.
- CUSIP-symbol mapping is required before reliable selected-symbol durable lookup.

## Source / Legal Risks

- Analyst ratings and target changes are usually aggregator-owned and licensing-sensitive.
- Public web pages are not automatically safe DB ingestion sources.
- MarketWatch / FactSet-sourced pages should remain outbound-only unless licensed.
- FMP / Finnhub free API-key sources require quota, attribution, redistribution, and storage review before use.

## Product Risks

- Users may infer recommendations from analyst upgrades or 13F increases. UI copy must use `조사 근거` or `관심 근거`, not `매수 근거`.
- Source diagnostics should not become the main UI. Raw provider status belongs in collapsed detail only if needed.

## Deferred Follow-ups

- Durable 13F ingestion needs official SEC data-set ingestion design, CUSIP-symbol mapping, quarter-over-quarter comparison policy, and DB schema approval.
- API-key providers such as FMP / Finnhub need quota, attribution, redistribution, and storage review before implementation.
- A later summary model may group evidence states, but should stay limited to conservative labels such as `관심 근거 있음`, `원문 확인 필요`, `지연 자료`, and `데이터 없음`.
