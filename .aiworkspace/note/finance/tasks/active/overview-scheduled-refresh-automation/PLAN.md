# Plan

## 이걸 하는 이유?

Overview Market Intelligence는 Market Movers, Sector / Industry, Events, Data Health 화면을 갖췄지만 수집 실행은 여전히 사용자가 버튼을 눌러야 한다. 자동 수집 운영의 1차 목표는 브라우저를 켜지 않아도 기존 ingestion job wrapper를 주기적으로 실행할 수 있는 안전한 run-once orchestrator를 추가하는 것이다.

## Scope

- 새 provider collector를 만들지 않고 기존 `app.jobs.ingestion_jobs` wrapper를 재사용한다.
- cron / launchd / 외부 runner가 주기적으로 호출할 수 있는 CLI를 추가한다.
- cadence, US market-hours guard, lock, run history metadata를 자동화 계층에서 처리한다.
- 자동 실행 결과는 기존 `WEB_APP_RUN_HISTORY.jsonl` 형식으로 기록해 Data Health가 읽을 수 있게 한다.

## Non-Goals

- macOS launchd job을 사용자 시스템에 즉시 설치하지 않는다.
- provider 유료 API, broker order, live trading, auto rebalance는 범위 밖이다.
- BLS `.ics` 파일처럼 사용자가 직접 내려받아야 하는 source는 자동 다운로드하지 않는다.

## Steps

1. Overview scheduled refresh orchestrator 추가.
2. dry-run / force / profile / job filter CLI 옵션 추가.
3. lock / cadence / scheduled metadata service contract test 추가.
4. Overview runbook과 automation script guide 갱신.
5. focused QA와 full service contract test 실행.
