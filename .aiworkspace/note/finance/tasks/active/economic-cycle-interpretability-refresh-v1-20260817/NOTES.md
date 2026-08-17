# Notes

## 2026-08-17 진단 기준값

- official observed state: recovery, as_of 2026-07-31, duration 7 months.
- level -0.32564, 3-month momentum +0.07483.
- recent composite: 1m -0.02438 with 0/4 improving; 3m +0.07483 with 2/4; 6m +0.27454 with 3/4.
- transition pressure: 63.59% in next 3 usable releases.
- conditional destination: contraction 69.72%, expansion 23.93%, slowdown 6.36%.
- confirmed ribbon: 2025-08~2025-12 contraction, 2026-01~2026-07 recovery.

## 핵심 원인

- freshness owner mismatch: official RTDSM current snapshot vs legacy intramonth weekday comparison.
- React collecting state reset omission.
- production current evidence vs preserved legacy asset evidence mismatch.
- missing RTDSM quality metadata and hard-coded UI denominator 8.
- quarterly RUC threshold 120 days makes a 121-day normal cadence look stale.

## 구현 결정

- 공식 freshness 기준은 현재 날짜가 아니라 직전 완결 월말의 `current` snapshot이다.
- 수동 경기 갱신은 RTDSM 4개만 수집하고 confirmed monthly publisher를 강제 재발행한다.
- 기존 intramonth 함수와 자동화 등록은 호환용으로 남지만 Overview 수동 액션에서는 호출하지 않는다.
- 품질 필드가 없는 기존 RTDSM current row는 날짜가 최신이어도 한 번 재발행 대상으로 본다.
- 현재 국면 evidence는 RTDSM observed state에서 직접 만들고 기존 8지표 evidence는 자산 pathway 계산에만 유지한다.
- 자산 카드의 내용·계산·하위 구획은 보존하고 공통 경제 배경만 섹션 상단에 한 번 렌더링한다.
- 표시 수치의 부호는 화면 정밀도로 반올림한 뒤 판정해 `-0.0`을 회색 중립으로 처리한다.

## 실제 UI 확인값

- Data Freshness 갱신 전: 2026-07-31 공식 월은 최신이나 legacy quality contract 재발행 필요.
- 수동 갱신: RTDSM 4개 수집과 2026-07-31 강제 재발행이 약 45초 안에 종료.
- 갱신 후: `경제사이클 계산 최신 · 자산 경로 최신`, RTDSM 4/4.
- 양수 `rgb(29, 122, 97)`, 음수 `rgb(186, 87, 76)`, 0 `rgb(104, 121, 133)`을 브라우저 computed style로 확인.
