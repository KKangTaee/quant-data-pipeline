# Overview Market Interest Evidence V2 Notes

## 2026-07-08 Intake

- User testing found V1 reads like a URL opening feature, because `애널리스트 관심`, `뉴스/공시 촉매`, and `원문 확인` all collapse to similar `원문 확인` states.
- `뉴스/공시 촉매` should include the existing US news, Korean news, and SEC metadata directly in the `시장 관심` panel.
- `기관 보유 배경` must explain that 13F is manager holdings reporting, not the same as issuer SEC filings.
- `원문 확인` should be a supporting source disclosure, not a primary tab or card.

## Source Decisions

- Existing Google/Korean news and SEC metadata fetchers can be reused for selected-symbol session evidence.
- Naver News API requires Client ID/Secret; no credential integration in this pass.
- FMP/Finnhub structured analyst APIs require key/quota/terms approval; no integration in this pass.
- 13F durable lookup requires CUSIP-symbol mapping and DB design; no ingestion in this pass.

## 2026-07-08 Implementation Notes

- `market_interest.py` now returns `market_interest_evidence_v2` with conservative summary states and evidence sections.
- `시장 관심 근거 확인` now fetches existing news, Korean news, and SEC metadata before building the market-interest model.
- Selected-symbol clue tabs are consolidated to `기본 지표` and `시장 관심`.
- `원문 확인` is no longer a primary tab/section; source links live under `출처/원문 링크`.
- `기관 보유 배경 · 13F 지연 자료` is separated from issuer SEC filing metadata.
