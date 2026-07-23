# NYSE Listing Universe Refresh V1 Design

Status: Approved in conversation
Date: 2026-07-23

## Problem

`app/jobs/symbol_sources.py`와 `finance/loaders/_common.py`는 전체 주식·ETF universe를
`finance_meta.nyse_stock`과 `finance_meta.nyse_etf`에서 읽는다. 기존
`finance/data/nyse.py`는 NYSE 공식 listings API를 수집하고, `finance/data/nyse_db.py`는
CSV를 master와 lifecycle에 적재할 수 있지만, 이 흐름은 현재 Ingestion job과 사용자 화면에
연결되어 있지 않다.

2026-07-23 read-only 비교 결과는 다음과 같다.

| 종류 | DB snapshot | DB current rows | NYSE current rows | DB에 없는 current | NYSE current에서 빠진 DB row |
|---|---:|---:|---:|---:|---:|
| stock | 2026-05-31 | 6,738 | 6,770 | 158 | 126 |
| ETF | 2026-05-31 | 5,232 | 5,537 | 372 | 67 |

따라서 신규 ticker는 전체 가격·프로필 수집 입력에 들어오지 않는다.

## Chosen Approach

Ingestion `일상 운영 / 검증 데이터`의 첫 위치에 독립된
`주식·ETF 종목 목록 최신화` action을 둔다.

일별 가격 업데이트의 자동 pre-step으로 결합하지 않는다. universe provider 장애가 가격
수집을 막지 않아야 하고, 대규모 가격 수집 직전에 대상이 암묵적으로 바뀌지 않아야 하기 때문이다.
scheduler 자동화도 이번 범위에 넣지 않는다. 사용자가 필요할 때 현재 universe를 명시적으로
갱신할 수 있는 제품 행동이 우선이다.

## Architecture

### Source

- 주식: NYSE listings directory API `instrumentType=EQUITY`
- ETF: NYSE listings directory API `instrumentType=EXCHANGE_TRADED_FUND`
- collector는 현재의 symbol/name/url 정규화와 case-insensitive symbol dedupe를 재사용한다.

### Validation

DB write 전에 주식과 ETF를 모두 fetch한다.

- 두 frame 모두 비어 있지 않아야 한다.
- API가 보고한 total과 usable/deduped rows를 결과에 남긴다.
- 각 종류의 새 snapshot이 기존 current master 대비 비정상적으로 작은 경우 refresh를 중단한다.
- 실패 시 기존 `nyse_stock`·`nyse_etf`를 변경하지 않는다.

급감 guard는 정상적인 상장폐지와 source 장애를 구분하기 위한 안전장치다. 정상적인 증감은
추가·제외 diff로 처리하고, 임계값을 넘는 급감은 명시적 실패로 반환한다.

### Persistence

CSV 파일을 필수 중간 단계로 사용하지 않고 정규화된 DataFrame을 writer에 전달한다.
기존 CSV 적재 entry는 호환을 위해 같은 writer를 재사용한다.

한 DB transaction에서 다음 순서를 수행한다.

1. stock/ETF current master와 새 snapshot diff 계산
2. 새 row UPSERT
3. 새 snapshot에 없는 master row 삭제
4. current listing row를 `nyse_symbol_lifecycle`에 UPSERT
5. transaction commit

어느 write라도 실패하면 rollback한다.

`nyse_stock`과 `nyse_etf`는 current listing master이므로 canonical replace한다.
삭제는 이 두 master의 stale row에만 한정한다.

- `finance_price.nyse_price_history`는 삭제하지 않는다.
- `nyse_symbol_lifecycle`의 과거 evidence는 삭제하지 않는다.
- 사용자 registry/saved data는 건드리지 않는다.

### Job Contract

새 ingestion job은 하나의 `JobResult`를 반환한다.

- status: `success` 또는 `failed`
- rows/symbols: stock+ETF 전체 반영 수
- details:
  - snapshot date
  - stock/ETF별 before/current/added/removed count
  - API total/usable/deduped count
  - target tables
- source/validation/persistence 실패는 기존 master 보존 여부를 message와 details에 명시한다.

부분 성공은 허용하지 않는다. 주식과 ETF를 하나의 사용자 action으로 승인했으므로 둘 중 하나만
새 snapshot이 되는 상태를 만들지 않는다.

## User Experience

배치는 Ingestion의 `일상 운영 / 검증 데이터` 안내문 바로 아래, `일별 가격 업데이트` 앞이다.
새 대형 진단 패널은 만들지 않는다.

compact action은 다음을 제공한다.

- 제목: `주식·ETF 종목 목록 최신화`
- 설명: 전체 가격·프로필 수집이 이 목록을 기준으로 한다는 점
- 현재 기준: lifecycle의 stock/ETF 최근 snapshot date와 current row count
- action: `주식·ETF 종목 목록 최신화`
- 완료 요약: stock/ETF별 현재·추가·제외 건수
- 다음 행동: 필요하면 아래 `일별 가격 업데이트`에서 최신 universe를 사용

stale 여부는 사용자의 판단을 돕는 보조 근거다. 화면의 주인공은 “전체 수집 대상을 최신화한다”는
행동이며 job/row/raw status는 별도 주 화면으로 만들지 않는다.

## Error Handling

- NYSE HTTP/JSON 오류: write 전 실패, 기존 master 유지
- 빈/비정상 급감 snapshot: write 전 실패, 기존 master 유지
- DB write 오류: transaction rollback
- 성공 후 후속 가격 수집은 자동 실행하지 않음
- 화면은 실패 원인과 기존 목록 보존 여부를 간결하게 표시

## Testing

TDD로 다음 순서를 검증한다.

1. 정상 주식·ETF snapshot이 추가/제외 diff와 함께 atomic refresh된다.
2. ETF fetch 실패 또는 급감 guard 실패 시 writer가 호출되지 않는다.
3. DB write 실패 시 rollback되고 commit되지 않는다.
4. ingestion job이 stable `JobResult`를 반환한다.
5. registry/dispatcher/action guide가 새 action을 노출한다.
6. operational section에서 universe refresh가 daily price update 앞에 배치된다.
7. 실제 Ingestion Browser QA에서 current basis와 action을 확인한다.

## Documentation

동작이 확정되면 다음 durable docs만 최소 수정한다.

- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- `.aiworkspace/note/finance/docs/data/README.md`
- `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- root handoff logs
