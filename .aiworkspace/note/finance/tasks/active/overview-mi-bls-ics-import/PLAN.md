# Plan

## 이걸 하는 이유?

BLS release schedule HTML / ICS 자동 요청이 현재 실행 환경에서 HTTP 403으로 막힌다.
Macro Calendar를 실사용하려면 CPI, PPI, Employment Situation 일정을 공식 출처 기반으로 DB에 넣을 수 있는 fallback이 필요하다.

## Scope

- BLS `.ics` 파일 내용을 파싱해 `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT` event row로 정규화한다.
- 정규화된 row를 기존 `market_event_calendar` UPSERT 경로로 저장한다.
- Ingestion > Overview Market Event Calendar > Macro 화면에서 `.ics` 파일 업로드/import 버튼을 제공한다.
- Overview Events와 Data Health는 기존 DB read path를 그대로 사용한다.

## Non-goals

- BLS 차단을 우회하기 위한 비공식 scraping이나 browser automation은 추가하지 않는다.
- Macro source 범위를 CPI/PPI/Employment/GDP 밖으로 확장하지 않는다.
- 자동 refresh schedule은 이번 task에서 다루지 않는다.
