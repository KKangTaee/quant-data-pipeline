# Risks

## Closed

- NYSE API 응답 크기가 갑자기 급감하면 current master를 파괴하지 않도록 guard가 필요하다.
- `MySQLClient`가 기본 `autocommit=True`이므로 transaction 구간에서 명시적으로 autocommit을
  제어하거나 atomic writer 전용 연결 동작을 검증해야 한다.
- normalized ticker에는 provider가 바로 받지 못하는 preferred/unit 등 non-plain symbol이
  포함된다. 이번 action은 listing truth를 보존하고, 가격 수집의 기존 non-plain filter를 유지한다.

## Validation

- source empty/급감 guard는 DB transaction 시작 전에 실패한다.
- stock/ETF 중 하나의 fetch가 실패하면 writer를 호출하지 않는다.
- DB write 중 예외가 발생하면 두 master와 lifecycle 변경을 rollback한다.
- actual refresh 전후 price-history row count가 동일함을 확인했다.

## Closed By Design

- 주식만 성공하고 ETF가 실패하는 split snapshot은 허용하지 않는다.
- current master에서 빠진 ticker의 과거 가격을 삭제하지 않는다.
- lifecycle snapshot은 historical survivorship PASS를 의미하지 않는다.

## Follow-up

- 정기 자동화가 필요하면 scheduler/cron 주기와 실패 알림을 별도 task로 승인한다.
- listing current master는 최신화됐지만 신규 ticker의 가격은 후속 가격 수집 action을 실행해야 채워진다.
