# Institutional Portfolios Workspace V1 Design

Status: Active

## IA Decision

Primary location is `Workspace > Institutional Portfolios`.

- `Workspace`: 탐색과 research workflow에 맞다.
- `Operations`: 내 포트폴리오 운영 / 모니터링 의미가 강해 분기 지연 13F 탐색 기능을 두면 actionability가 과장된다.
- `Reference`: caveat와 guide 보조 위치로는 적합하지만 실제 탐색 화면으로는 약하다.
- `Institutional Interest`: page title보다 reverse lookup sub-mode 이름으로 쓴다.

## Data Flow

```text
SEC Form 13F official data set zip or local uploaded/downloaded zip
  -> finance/data/institutional_13f.py
  -> finance_meta.institutional_13f_manager
  -> finance_meta.institutional_13f_filing
  -> finance_meta.institutional_13f_holding
  -> finance_meta.institutional_13f_cusip_symbol_map
  -> finance/loaders/institutional_13f.py
  -> app/services/institutional_portfolios.py
  -> app/web/institutional_portfolios.py
```

## Source Contract

- Official source: SEC Form 13F Data Sets and EDGAR filing URLs.
- EDGAR API is used as filing metadata/source-link support, not as a complete holdings endpoint.
- Third-party pages remain benchmark/link-out references only.
- Filing period and filing date are both visible because 13F is delayed and filing timing matters.

## Change Model

Holdings are compared by CUSIP, optional FIGI, optional mapped symbol, and put/call class.

- `reported_new`: present in latest filing, absent in previous comparable filing.
- `increased`: latest shares or value is greater than previous.
- `reduced`: latest shares or value is lower than previous.
- `unchanged`: latest and previous quantities are effectively equal.
- `no_longer_reported`: present previously, absent in latest.

These labels describe reported 13F rows and must not be worded as current buy / sell signals.

## CUSIP / Symbol Boundary

13F official info table contains CUSIP and FIGI but not a reliable ticker. The MVP stores optional symbol mappings separately and keeps unmapped holdings visible by issuer / CUSIP. Reverse lookup accepts ticker, CUSIP, or issuer text and reports mapping caveats.

## UI Shape

- Top caveat band.
- Manager search/select.
- Latest filing summary and data freshness.
- Holdings table with weights.
- Change view.
- Sector / industry exposure with unmapped weight.
- Institutional Interest reverse lookup.
- Source links to SEC filing or dataset.

The page is read-only and creates no registry / saved portfolio rows.
