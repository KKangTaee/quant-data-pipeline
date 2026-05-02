# Phase 4 - Annual Statement Coverage Stage 1 Top-100 Run

## 목적

wider-universe annual coverage를 바로 `Profile Filtered Stocks` 전체에 실행하기 전에,
실제로 의미 있는 staged run이 어떻게 나오는지 확인한다.

이번 stage 1은 다음 기준을 사용했다.

- universe: `Profile Filtered Stocks`
- selection rule: `market_cap DESC`
- size: `100`
- freq: `annual`
- periods: `12`

즉, `Profile Filtered Stocks` 중 시가총액 상위 100개를 annual statement coverage seed universe로 사용했다.

## 실행

실행 순서:
1. annual financial statement refresh
2. annual statement fundamentals shadow rebuild
3. annual statement factors shadow rebuild
4. strict coverage summary audit

## 결과 요약

statement refresh:
- `status = success`
- `rows_written = 188709`
- `upserted_labels = 85164`
- `upserted_filings = 8575`
- `failed_symbols = 0`

shadow rebuild:
- `shadow_fund_rows = 2376`
- `shadow_factor_rows = 2376`

coverage summary:
- stage 1 input symbols: `100`
- symbols with strict annual coverage: `80`
- symbols missing strict annual coverage: `20`
- global min covered period: `2008-12-31`
- global max covered period: `2026-02-01`
- median distinct annual accessions: `12`
- symbols with `12+` accessions: `68`
- symbols with `8+` accessions: `74`
- symbols with `5+` accessions: `77`

shadow factor usable fields:
- `market_cap` non-null rows: `340`
- `roe` non-null rows: `887`

## 중요한 해석

### 1. stage 1 자체는 성공

annual statement coverage를 sample universe 밖으로 넓히는 첫 staged run으로는 충분히 성공적이다.

- 100개 input 중 80개에서 strict annual coverage 확보
- 많은 대형주가 `12` annual accessions까지 채워짐
- shadow fundamentals/factors도 같은 universe로 실제 rebuilt 됨

### 2. coverage가 없는 20개는 대부분 foreign issuer

missing preview:
- `TSM`
- `AZN`
- `ASML`
- `BABA`
- `TM`
- `HSBC`
- `NVS`
- `RY`
- `SAP`
- `SHEL`
- `MUFG`
- `NVO`
- `RIO`
- `BHP`
- `SAN`
- `HDB`
- `TD`
- `TTE`
- `UL`
- `BBVA`

즉 현재 top-market-cap seed는 시가총액 기준으로는 유용하지만,
EDGAR strict statement coverage 관점에서는 foreign issuer가 섞여 비효율이 생긴다.

### 3. 다음 wider run은 scope refinement가 필요

현재 결과는
`Profile Filtered Stocks` 전체를 바로 넓히기보다,
다음 stage에서 아래 중 하나를 고려해야 함을 보여준다.

1. `United States` issuer 중심 annual run
2. EDGAR coverage가 이미 확인된 stock universe 중심 run
3. 현재 top-market-cap seed 유지 + foreign issuer 제외 규칙 추가

## 결론

stage 1 top-100 annual coverage run은 성공했고,
strict annual path를 wider universe로 넓힐 수 있다는 점은 확인됐다.

다만 다음 stage에서는 단순 market-cap top N보다
`EDGAR coverage 친화적인 stock universe`
로 범위를 다듬는 쪽이 더 효율적이다.
