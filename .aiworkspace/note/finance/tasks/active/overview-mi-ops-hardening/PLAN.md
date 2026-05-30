# Plan

## 이걸 하는 이유?

Overview Market Intelligence는 4차까지 production baseline을 완료했다. 5차는 새 기능을 늘리기보다, 매일 운영할 때 데이터가 언제 갱신됐고 어떤 수집이 실패했는지 바로 판단할 수 있게 만드는 보강 단계다.

## Scope

- Overview에 `Data Health` 또는 동등한 collection ops 상태 화면을 추가한다.
- 기존 DB table과 `WEB_APP_RUN_HISTORY.jsonl`을 읽어 마지막 성공/실패, 처리량, 실패 수, duration, freshness, next action을 보여준다.
- Overview refresh button이 실행한 market intelligence job도 run history에 남긴다.
- 새 원격 수집 source와 새 DB schema는 추가하지 않는다.

## Done Criteria

- Market Snapshot, FOMC, Earnings, S&P 500 Universe 상태를 한 화면에서 볼 수 있다.
- 상태 row는 `OK / Due / Stale / Missing / Failed / Partial` 계열로 읽힌다.
- Overview render path는 외부 provider를 fetch하지 않는다.
- service contract tests, UI boundary check, Browser smoke가 통과한다.
