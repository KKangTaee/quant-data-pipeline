# Plan

## 이걸 하는 이유?

Overview Events 탭이 실제 시장 일정 데이터를 보여주려면 무료/공식 소스에서 수집한 이벤트를 DB에 먼저 저장해야 한다. Task 4에서 만든 `finance_meta.market_event_calendar`를 첫 번째 실사용 collector로 검증하고, 이후 earnings collector가 같은 구조를 재사용할 수 있게 한다.

## Scope

- Fed 공식 FOMC calendar 페이지를 파싱한다.
- FOMC meeting date를 `market_event_calendar`에 idempotent UPSERT한다.
- Ingestion 화면에서 `Collect FOMC Calendar` job으로 실행한다.
- Overview Events 탭은 DB에 저장된 FOMC event를 읽어 표시하고, 버튼은 ingestion job wrapper를 호출한다.
- Earnings collector는 이번 task 범위 밖이다.

## Done Criteria

- Network parser 단위 테스트와 DB writer contract test가 있다.
- Overview event read model contract test가 있다.
- 관련 Python 파일 compile, service contract tests, diff check가 통과한다.
- 가능하면 실제 Fed 공식 페이지 수집 smoke를 실행해 DB 저장까지 확인한다.
