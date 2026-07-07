# Backtest Coverage Provider Gap Refresh V1

Status: Completed
Started: 2026-07-07
Completed: 2026-07-07

## Purpose

Quality / Value strict factor backtest에서 Coverage 최신화가 provider no-data 심볼을 계속 해결 가능한 action으로 보여주는 문제를 고친다.

## Scope

- Backtest Data Trust price refresh plan에서 provider/source gap 성격의 심볼을 refresh 가능 대상과 구분한다.
- refresh 실행 후 rows가 0이고 unresolved 심볼이 남으면 같은 화면에서 재클릭 버튼을 다시 노출하지 않는다.
- OHLCV collector 자체, provider 교체, universe 선정 정책은 이번 작업 범위가 아니다.

## Result

- 원인 조사 완료: `refresh_symbols_all`이 전부 refresh 가능 대상으로 들어가고, post-refresh unresolved 결과가 렌더링 순서상 버튼을 막지 못했다.
- `classification_rows`가 명백한 persistent provider/source gap을 가리키면 refresh plan에서 제외한다.
- rows_written=0이고 `post_refresh_unresolved_symbols`가 남은 실행 결과는 같은 화면에서 재클릭 버튼을 다시 렌더링하지 않는다.
- 검증: price refresh focused service contract 11개, py_compile, git diff --check, Browser smoke QA 통과.
