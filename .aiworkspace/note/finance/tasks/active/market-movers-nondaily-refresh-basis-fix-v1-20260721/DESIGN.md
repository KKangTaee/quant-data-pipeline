# Design

## Date Semantics

- `refresh_target_date`: `latest_completed_nyse_session()`이 반환하는 최신 완료 NYSE 거래일
- `ranking_data_as_of`: Market Movers coverage가 임계치를 충족한 `effective_end_date` 또는 snapshot timestamp

두 날짜는 같을 수도 있지만 최신 가격의 universe coverage가 부족하면 달라질 수 있다. 이 차이는 오류를 숨기는 대상이 아니라 사용자에게 보여줄 데이터 신뢰 맥락이다.

## Flow

1. 비-Daily 화면은 최신 완료 NYSE 거래일로 EOD preflight를 계산한다.
2. preflight는 각 symbol의 저장 최신일과 목표일을 비교해 보강 대상을 만든다.
3. 수동 갱신은 preflight의 동일 목표일을 job에 넘긴다.
4. 갱신 후 snapshot을 다시 읽고 coverage 임계치를 만족하는 가장 최신일을 랭킹 기준일로 선택한다.

## Tradeoff

가격 갱신 버튼을 항상 노출하면 이미 최신일 때 no-op 실행이 가능하다. 대신 사용자가 필요한 복구 수단을 잃지 않으며, preflight 설명으로 실제 대상 수를 안내한다.
