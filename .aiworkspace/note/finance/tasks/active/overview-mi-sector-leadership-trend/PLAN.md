# Overview MI Sector Leadership Trend

Status: Active

## 이걸 하는 이유?

Sector / Industry Leadership 화면을 월간 단면 히트맵에서 벗어나, S&P 500 / Top 1000 / Top 2000 커버리지별로 최근 일간, 주간, 월간 주도 섹터와 산업 흐름을 쉽게 읽는 화면으로 개선한다.

## Scope

- Sector / Industry Leadership coverage에 S&P 500 추가.
- Group control을 드롭다운 형태로 변경.
- Period control을 Daily / Weekly / Monthly로 추가.
- 최신 기간 Top N ranking과 최근 기간 trend chart를 함께 제공.
- 기존 DB-backed price / profile / universe 데이터를 사용하고 새 외부 수집은 추가하지 않는다.

## Verification

- Service contract tests.
- `py_compile` for touched modules.
- Browser smoke for Overview Sector / Industry tab.
