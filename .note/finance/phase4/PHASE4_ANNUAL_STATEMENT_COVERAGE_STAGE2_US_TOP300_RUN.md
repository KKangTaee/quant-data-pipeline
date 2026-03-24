# Phase 4 - Annual Statement Coverage Stage 2 US Top-300 Run

## 목적

stage 1 top-100 run 이후,
foreign issuer 혼입을 줄인 `US / EDGAR-friendly` annual coverage stage를 실제로 검증한다.

이번 stage 2는 다음 기준을 사용했다.

- universe: `Profile Filtered Stocks`
- country: `United States`
- selection rule: `market_cap DESC`
- size: `300`
- freq: `annual`
- periods: `12`

## 실행 순서

1. annual statement refresh
2. annual statement fundamentals shadow rebuild
3. annual statement factors shadow rebuild
4. strict coverage summary audit

## 결과 요약

statement refresh:
- `status = success`
- `rows_written = 701189`
- `upserted_labels = 316761`
- `upserted_filings = 30170`
- `failed_symbols = 0`

shadow rebuild:
- `shadow_fund_rows = 9385`
- `shadow_factor_rows = 9385`

coverage summary:
- stage 2 input symbols: `300`
- symbols with strict annual coverage: `297`
- missing symbols: `3`
- global min covered period: `1989-12-31`
- global max covered period: `2026-02-01`
- median distinct annual accessions: `12`
- max distinct annual accessions: `14`
- symbols with `12+` accessions: `251`
- symbols with `8+` accessions: `266`
- symbols with `5+` accessions: `286`

shadow factor usable fields:
- `market_cap` non-null rows: `1244`
- `roe` non-null rows: `3413`

missing symbols:
- `MRSH`
- `AU`
- `CUK`

## stage 1 대비 의미

stage 1 (`top 100 by market cap`)에서는:
- `80 / 100` coverage
- missing 대부분 foreign issuer

stage 2 (`US top 300`)에서는:
- `297 / 300` coverage
- missing `3`

즉, annual strict statement coverage를 넓히려면
단순 top-market-cap보다
`US / EDGAR-friendly` scope refinement가 훨씬 효과적이라는 점이 실제로 확인되었다.

## 결론

`Quality Snapshot (Strict Annual)`을 신뢰 가능한 public candidate로 보려면
annual statement coverage가 sample universe 밖에서도 충분히 열려 있어야 하는데,
이번 stage 2 결과는 그 방향이 실질적으로 가능하다는 강한 근거가 된다.

현재 판단:
- annual strict path는 더 이상 sample-only proof of concept 수준에 머물지 않는다
- 다음 단계는
  - 이 annual US-heavy coverage를 더 넓힐지
  - strict annual quality strategy의 public 설명/기본 universe를 재정의할지
  - strict annual path를 broad path 대비 더 공식적으로 승격할지
  쪽으로 넘어갈 수 있다
