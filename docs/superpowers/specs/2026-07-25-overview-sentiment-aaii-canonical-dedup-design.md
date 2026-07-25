# Overview Sentiment AAII Canonical Dedup Design

Date: 2026-07-25
Status: Approved

## 이걸 하는 이유?

Overview > Sentiment의 AAII 그래프에 `2026-06-17/18`, `2026-07-08/09`처럼 하루 간격의 점이 함께 보인다. 실제 DB 확인 결과 앞 날짜는 과거 HTML 수집본, 뒤 날짜는 공식 XLS workbook 수집본이며 값은 반올림 차이만 있는 동일 주차 설문이다. 주간 설문을 서로 다른 두 관측으로 표시하면 변화 속도와 표본 수를 왜곡한다.

## Approved Scope

사용자는 2026-07-25 진단 결과에서 제안한 아래 범위의 개선을 승인했다.

- 기존 canonical AAII HTML/XLS 동일 주차 중복 정리
- 공식 XLS 날짜를 canonical observation date로 사용
- 동일 문제가 다시 발생하지 않도록 수집 경로에 회귀 방지
- immutable `market_sentiment_observation_snapshot`과 collection batch는 보존
- 차트 표현, AAII 방향 판정, CNN 데이터는 변경하지 않음

## Design

### Source of truth

AAII 공식 XLS workbook의 `Reported Date`를 canonical 주차 날짜로 사용한다. 정상 workbook은 한 주에 한 날짜를 제공하고 최근 관측은 7일 간격이다.

### Preventive reconciliation

`persist_market_sentiment_source_capture()`가 `aaii_sentiment_survey`의 완전한 XLS capture를 저장할 때, 같은 트랜잭션 안에서 incoming workbook 날짜 범위를 authoritative canonical window로 정리한다.

- 대상: `finance_meta.macro_series_observation`
- 범위: incoming XLS의 최소~최대 `observation_date`
- 보존: incoming XLS에 포함된 날짜
- 제거: 같은 AAII source와 네 canonical series 중 보존 날짜에 없는 canonical 행
- 후속: incoming normalized rows UPSERT
- 비대상: HTML fallback, CNN, immutable snapshot, collection batch

XLS capture가 네 AAII series의 정렬된 날짜 집합을 제공하지 않으면 canonical window 정리를 수행하지 않고 기존 coverage/저장 검증에 맡긴다. HTML fallback은 현재 parser가 workbook 날짜로 하루 보정하지만, authoritative window 삭제 권한은 갖지 않는다.

### Existing data cleanup

기존 DB는 `backfill_aaii_sentiment_history()`를 한 번 실행해 공식 workbook 전체를 먼저 가져온 뒤, 트랜잭션으로 기존 AAII canonical history를 삭제·재삽입한다. 이 경로는 immutable snapshot을 만들거나 변경하지 않는다.

## Failure Handling

- workbook fetch 실패 시 DB cleanup을 시작하지 않는다.
- canonical window cleanup 또는 UPSERT 실패 시 source capture 전체 트랜잭션을 rollback한다.
- 전체 backfill 실패 시 기존 canonical history를 rollback해 유지한다.

## Verification

- 회귀 테스트에서 XLS capture가 authoritative date window를 정리한 뒤 UPSERT하는지 확인
- HTML capture는 window cleanup을 실행하지 않는지 확인
- cleanup 실패가 batch/snapshot/canonical write 전체를 rollback하는지 확인
- 실제 공식 workbook 최근 날짜 간격이 모두 7일인지 확인
- 실제 DB와 React payload에서 6/17·18, 7/8·9 중복이 제거됐는지 확인

## Out of Scope

- AAII historical methodology 변경 검증
- 1W/1M 전망 공개
- chart interpolation, scale, tooltip 변경
- immutable PIT snapshot 재작성
