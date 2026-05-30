# Plan

## 이걸 하는 이유?

Overview Market Intelligence 자동 수집은 OS scheduler까지 붙이기 전에, 사용자가 Overview를 열어둔 동안만 가볍게 작동하는 1차 운영 모드가 필요하다. 이 task는 provider 부담을 줄이면서 S&P 500 daily snapshot을 주기적으로 최신화할 수 있는 browser-session gated refresh 흐름을 만든다.

## Scope

- 1차 기본 자동 수집 대상은 S&P 500 daily snapshot만 둔다.
- 기존 `app.jobs.overview_automation` cadence, market-hours guard, lock, run history를 재사용한다.
- Streamlit UI는 이후 단계에서 toggle / status panel / fragment heartbeat로 연결한다.
- OS launchd / cron 등록은 범위 밖이다.

## Steps

1. `browser_safe` automation profile을 추가해 S&P 500 intraday snapshot만 선택하게 한다.
2. Overview UI에 browser-open auto refresh toggle과 상태 패널을 추가한다.
3. Streamlit fragment heartbeat에서 `browser_safe` profile을 호출한다.
4. Data Health / runbook 문구를 browser-session auto refresh 기준으로 정렬한다.
5. focused tests, dry-run, browser smoke로 검증한다.
