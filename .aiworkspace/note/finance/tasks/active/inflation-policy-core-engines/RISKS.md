# Inflation Policy Core Engines Risks

- 짧은 FOMC decision history는 policy probability를 `READY`로 공개하기에 부족할 수 있다.
- SEP marginal distribution을 joint path처럼 취급하면 존재하지 않는 participant mapping이 생긴다.
- revised/current ACM workbook을 과거 origin에 사용하면 term-premium look-ahead가 생긴다.
- fixed state/zone threshold를 current 2026 사례에 과적합할 수 있다.
- simulation path 수가 적은 reverse target은 조건부분포가 불안정하다.
- 사용자 소유 registry, research, run history와 generated QA artifact는 stage하지 않는다.
- 1개월 Core PCE nowcast의 검증을 연말 Q4/Q4 path 검증으로 오해하지 않는다. path는
  자체 multi-horizon rolling-origin gate 전까지 `LIMITED`다.
- versioned state-to-policy reaction matrix는 아직 calibrated policy model이 아니다.
  정책 결과는 decision history와 통계 component가 충분해질 때까지 `LIMITED`다.
- 저항대는 point-in-time으로 계산되지만 breakout/hold event 표본 calibration 전에는
  zone 위치·상태만 사용하고 확률은 `null`로 둔다.
- 2026-07-29 저장 snapshot은 workbench 연결용 historical replay evidence다. 투자
  확정값이나 자동 금리·주식 판단으로 사용하지 않는다.
