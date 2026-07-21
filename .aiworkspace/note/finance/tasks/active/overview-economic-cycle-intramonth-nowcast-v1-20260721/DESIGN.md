# Overview Economic Cycle Intramonth Nowcast V1 Design Record

Status: Approved
Last Updated: 2026-07-21

- 기존 `current`와 `historical_replay` 월말 row를 수정하지 않는다.
- 월중 결과는 날짜별 `intramonth_nowcast`로 분리하고 latest valid row만 화면에 쓴다.
- 계산 기준일, 실제 수집시각, 원천별 최신 관측일을 서로 다른 필드로 보존한다.
- 매 평일 backend `safe/standard/broad` profile에서 증분 수집 후 계산한다.
- 새 달 첫 평일에는 누락된 직전 월말 canonical row만 append하고 이를 새 현월 baseline으로 사용한다.
- `browser_safe`와 화면 render는 provider/fit/write를 호출하지 않는다.
- 실패 시 새 row를 쓰지 않고 마지막 정상 월중 결과와 모든 월말 결과를 유지한다.
- UI는 월말 h0에서 월중 h0까지 한 개의 점선 bridge와 compact 변화 block을 표시한다.

상세 설계는 `docs/superpowers/specs/2026-07-21-economic-cycle-intramonth-nowcast-design.md`를 따른다.
