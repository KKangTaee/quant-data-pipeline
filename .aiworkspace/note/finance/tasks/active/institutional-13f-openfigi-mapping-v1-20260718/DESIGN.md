# Institutional 13F OpenFIGI Mapping V1 Design

Status: Approved For Implementation
Last Updated: 2026-07-18

## Agreed Goal

`Workspace > Institutional Portfolios`의 SEC 13F CUSIP/CINS를 거래 ticker로 안전하게 보강한다. 성공 기준은 연결률만 높이는 것이 아니라 오연결을 막으면서 issuer/CUSIP row가 ticker 기반 chart, price collection, sector metadata로 이어지는 것이다.

SEC holding/value/share data는 그대로 source-of-truth로 유지한다. OpenFIGI는 ticker identity enrichment만 담당하며 portfolio holding 사실이나 매매 의도를 만들지 않는다.

## Evidence Behind The Design

- OpenFIGI 공식 API는 무료이며 API key 없이도 사용할 수 있다.
- key 없음: mapping API 분당 25회, 요청당 10 jobs.
- 무료 key 있음: 6초당 25회, 요청당 100 jobs.
- 현재 날짜 기준 v3를 사용한다. v2는 2026-07-01 sunset 이후 대상이 아니다.
- 공식 mapping 입력은 `ID_CUSIP`과 `ID_CINS`를 지원한다.
- Duquesne latest DB evidence:
  - 70 logical holding rows.
  - 68 distinct CUSIP/CINS values.
  - current exact-name map 5 rows.
  - existing-map CUSIP unique candidate/name mismatch 10 rows.
  - existing-map multi-candidate 1 row.
  - existing-map candidate 없음 54 rows.
- anonymous OpenFIGI v3 actual probe with `exchCode=US`, `marketSecDes=Equity` returned one distinct ticker for all 68 Duquesne identifiers.

Official references:

- <https://www.openfigi.com/api>
- <https://www.openfigi.com/api/documentation>
- <https://www.openfigi.com/docs/terms-of-service>
- <https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data>

## Approaches Considered

### A. Anonymous-First OpenFIGI With Optional Free Key — Chosen

- no-key path is always functional.
- `OPENFIGI_API_KEY`가 있으면 official authenticated request/job limits를 사용한다.
- US Equity 단일 후보만 canonical mapping으로 승격한다.
- 장점: 무료, current Duquesne 표본 coverage가 높고 key가 구현 blocker가 아니다.
- tradeoff: no-key full-universe backfill은 느리므로 첫 실행 범위를 curated managers로 제한한다.

### B. Free-Key-Required Bulk Mapping — Rejected As Default

- full latest universe를 빠르게 처리할 수 있다.
- 단점: 계정 생성과 secret 설정이 없으면 제품 개발/QA가 막힌다.
- 결정: key는 optional acceleration으로만 지원한다.

### C. SEC/Internal Name Matching Only — Rejected As Primary

- 외부 provider 호출이 없다.
- SEC `company_tickers.json`은 ticker/CIK/name을 제공하지만 CUSIP을 제공하지 않는다.
- current exact-name heuristic은 Duquesne 5/70에 그치고 stale/wrong legacy 후보도 확인됐다.
- 결정: SEC/internal data는 output validation과 sector enrichment의 보조 근거로만 사용한다.

## Target Data Flow

```text
latest 13F holding CUSIP/CINS
  -> normalize identifier
  -> numeric first character: ID_CUSIP
     alphabetic first character: ID_CINS
  -> OpenFIGI v3 mapping batch
       exchCode=US
       marketSecDes=Equity
  -> normalize distinct ticker + compositeFIGI candidates
       1 candidate  -> mapped
       0 candidates -> unmapped
       2+ candidates -> ambiguous
       transport/schema failure -> error
  -> upsert current provider resolution + last-attempt evidence
  -> loader source precedence
       OpenFIGI accepted mapping
       legacy exact issuer-name mapping
       curated in-service seed
       unresolved
  -> existing service/read model
  -> Institutional Portfolios UI
```

## Provider Adapter Contract

새 provider boundary는 `finance/data/institutional_13f_mapping.py`가 소유한다.

### Input

- normalized 9-character identifier.
- optional SEC issuer name for audit/evidence only.
- optional `OPENFIGI_API_KEY` from environment or explicit injected argument.

### Request

- endpoint: `https://api.openfigi.com/v3/mapping`.
- numeric-leading identifier: `ID_CUSIP`.
- alphabetic-leading identifier: `ID_CINS`.
- filters: `exchCode=US`, `marketSecDes=Equity`.
- Content-Type JSON.
- no hardcoded key or credential persistence.

### Batch And Retry

- no key: maximum 10 jobs/request.
- key: maximum 100 jobs/request.
- read `ratelimit-limit`, `ratelimit-remaining`, and `ratelimit-reset` when present.
- 429, 500, 503만 bounded retry 대상이다.
- server reset/retry hint가 있으면 따르고, 없으면 bounded exponential backoff를 사용한다.
- invalid request, 401, schema mismatch는 재시도하지 않고 error audit을 남긴다.

### Response Normalization

- result order가 request order와 일치한다는 provider contract를 사용하되 길이 불일치는 전체 batch schema error로 처리한다.
- `warning`은 v3 no-match 정상 상태로 읽는다.
- ticker가 없는 row는 candidate에서 제외한다.
- venue-level 중복은 normalized ticker/composite FIGI 기준으로 dedupe한다.
- 서로 다른 ticker 또는 composite FIGI가 남으면 ambiguous다.
- 첫 번째 결과를 임의 선택하지 않는다.

## Persistence Contract

### Existing Legacy Map

기존 `institutional_13f_cusip_symbol_map`은 `asset_profile_name_match` legacy 결과와 기존 reverse lookup 호환을 위해 보존한다. OpenFIGI 결과를 이 테이블에 섞지 않는다. 현재 unique key는 같은 CUSIP/source에 여러 symbol을 허용하므로 provider의 현재 canonical resolution을 표현하기에 적합하지 않다.

### Canonical Provider Resolution

OpenFIGI의 현재 accepted identity와 성공 외 상태를 함께 보존하는 source별 identifier resolution table을 추가한다.

- identifier value/type.
- source.
- resolution status: `mapped`, `ambiguous`, `unmapped`.
- accepted symbol/provider name/composite FIGI when mapped.
- candidate count와 compact candidate JSON.
- last attempt status: `success`, `error`.
- warning/error text와 attempted/resolved timestamps.
- stable unique key: identifier + source.

정상 HTTP 응답의 `mapped`, `ambiguous`, `unmapped`는 current resolution을 교체한다. transport/provider/schema `error`는 last-attempt evidence만 갱신하고 마지막 정상 resolution과 accepted symbol을 지우지 않는다. 이 규칙으로 일시 장애가 이미 검증된 연결을 파괴하지 않는다.

full provider response는 저장하지 않는다. UI에 run/job/row diagnostic panel을 추가하지 않는다.

## Loader Resolution Contract

현재 loader의 `CUSIP + exact issuer_name` join만으로는 SEC 축약명과 provider canonical name이 달라 OpenFIGI 결과를 사용할 수 없다.

reader는 다음 규칙을 사용한다.

1. 같은 identifier의 current `openfigi_v3` resolution이 `mapped`이고 accepted symbol/composite FIGI가 있으면 issuer spelling과 무관하게 사용한다.
2. current OpenFIGI resolution이 `ambiguous`이면 legacy 후보를 승격하지 않고 ambiguous로 반환한다.
3. current OpenFIGI resolution이 `unmapped`, error-only, 또는 없을 때만 legacy `asset_profile_name_match` exact issuer-name 결과를 사용한다.
4. legacy source가 CUSIP-only로 여러 symbol을 갖더라도 issuer exact match가 아니면 사용하지 않는다.
5. service curated seed는 기존 마지막 안전 fallback으로 유지한다.

symbol/CUSIP reverse lookup도 provider resolution의 current `mapped` row를 먼저 읽고, 그 다음 legacy table을 사용한다.

현재 DB에서 확인된 stale/wrong legacy rows는 삭제하지 않는다. source precedence와 exact-name gate로 제품 사용에서 격리한다.

## Sector And Price Handoff

- OpenFIGI는 identity source이며 sector source가 아니다.
- accepted ticker를 local `nyse_asset_profile`과 연결해 sector/industry를 보강한다.
- local profile metadata가 없으면 ticker는 mapped로 유지하되 sector는 `Unmapped`일 수 있다.
- price collection은 existing selected-symbol OHLCV action을 그대로 사용한다.
- ticker mapping 성공과 price-history ready를 같은 상태로 취급하지 않는다.

## Backfill Scope

### V1 Initial Run

- code/DB curated manager set의 latest accession holdings.
- current evidence: 12 managers, 약 1,244 distinct identifiers.
- identifier dedupe 후 unresolved/stale 대상만 요청한다.
- no-key execution remains supported; free key가 있으면 larger official batch limit을 자동 사용한다.

### Follow-up Expansion

- all latest manager holdings: current DB 약 31,215 distinct identifiers.
- all stored dataset holdings: current DB 약 33,654 distinct identifiers.
- full-universe run은 V1 adapter와 persistence를 재사용하지만 initial done condition은 아니다.

## Error And Safety States

- `mapped`: one accepted US Equity ticker/composite FIGI.
- `ambiguous`: more than one distinct accepted identity; no chart/price action.
- `unmapped`: provider warning/no result; issuer/CUSIP holding remains visible.
- `error`: provider/transport/schema failure; existing valid mapping is not overwritten.
- one batch failure must not corrupt successful earlier batches.
- rejected/ambiguous candidates never populate `holding_symbol` or canonical accepted map.

## File Ownership

- `finance/data/institutional_13f_mapping.py`
  - OpenFIGI request/response normalization, batching, retry, resolution persistence orchestration.
- `finance/data/db/schema.py`
  - per-identifier canonical provider resolution + attempt evidence schema.
- `finance/data/institutional_13f.py`
  - SEC ingestion handoff and mapping backfill entry point only.
- `finance/loaders/institutional_13f.py`
  - accepted-source precedence and safe reader joins.
- `app/jobs/ingestion_jobs.py`
  - explicit backend job boundary if existing registry action requires it.
- `app/web/ingestion/*`
  - only existing action metadata needed to invoke mapping; no new diagnostic product panel.
- `tests/test_institutional_13f_mapping.py`
  - provider/parser/batch/persistence behavior.
- `tests/test_institutional_portfolios.py`
  - loader/service mapped/ambiguous/unmapped regression.

## Testing Contract

### Unit / TDD

- numeric CUSIP uses `ID_CUSIP`.
- alphabetic CINS uses `ID_CINS`.
- key/no-key batch sizes are 100/10.
- request contains US Equity filters.
- v3 `warning` becomes unmapped, not transport error.
- repeated venue rows for one identity dedupe to mapped.
- multiple ticker/composite identities become ambiguous.
- 429/500/503 retry is bounded; 401/400 is not retried.
- persistence is idempotent; normal no-match/ambiguity replaces current resolution while transport/provider error preserves the last normal resolution.
- loader chooses OpenFIGI source before legacy exact-name and blocks multi-source ambiguity.

### Integration / Actual DB

- schema sync.
- curated manager distinct identifier backfill.
- before/after manager mapping count and mapped reported-value weight.
- Duquesne top holdings resolve to expected symbols from actual provider response.
- unresolved/ambiguous fixture still exposes issuer/CUSIP and no price action.

### UI QA

- Institutional Portfolios desktop actual DB.
- Duquesne entire holdings mapping badges and coverage metrics.
- mapped row opens security detail and existing price action.
- any remaining unresolved/ambiguous row stays blocked.
- one screenshot is kept as generated QA artifact and not committed unless requested.

## Important Trade-offs

- identity correctness is prioritized over 100% mapping coverage.
- free anonymous mode avoids a credential blocker but is slower for broad backfills.
- source precedence isolates legacy bad candidates without destructive cleanup.
- V1 improves curated-manager real use first; full 31k latest-universe processing is a follow-up run, not a different architecture.
