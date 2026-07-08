# Plan

## Purpose

Market Movers Polish V3 4차는 상승/하락/거래량 상위종목 board를 메인 분석 표면으로 만들고, 중복 차트와 개별 상세표를 첫 화면에서 제거한다.

## Scope

- Market Movers snapshot panel을 풀폭 ranking board 중심으로 재배치한다.
- board row에 직전 수익률 preview를 추가한다.
- board list는 내부 스크롤로 제한해 첫 화면이 과도하게 늘어나지 않게 한다.
- 모드별 전체 상세 표 expander는 유지한다.
- 기존 chart workspace helper는 호환용으로 남기되 main flow에서는 호출하지 않는다.

## Completion Criteria

- SP500 Daily 첫 화면에서 board가 중심이고 상승 수익률 차트가 보이지 않는다.
- `상세 표로 보기` 개별 expander가 사라지고, `모드별 상세 표 전체 높이로 보기`는 유지된다.
- Weekly/NASDAQ/mobile QA가 깨지지 않는다.
