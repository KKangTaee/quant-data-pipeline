# Methodology Benchmarks

Date: 2026-08-03
Scope: official / primary methodology only

## NBER Business Cycle Dating

- recession은 경제활동의 유의미한 감소가 경제 전반에 퍼지고 수개월 이상 지속되는
  개념으로 depth, diffusion, duration을 함께 본다.
- turning point 판정은 retrospective이며 자료 수정과 모호성 해소를 기다린다.
- 2020년 4월 trough는 2021년 7월에 발표됐다.

Implication: USREC를 실시간 current-state label override로 쓰지 않고, ex-post reference
overlay와 validation benchmark로 분리해야 한다.

## Chicago Fed CFNAI

- 현재 활동은 3개월 이동평균과 diffusion index를 함께 해석한다.
- 단일 0 crossing이 아니라 이전 상태와 지속성에 따라 -0.7, +0.2 등 서로 다른
  threshold를 쓴다.

Implication: 현재 composite에도 level, breadth, duration과 state-dependent hysteresis가
필요하다.

## OECD Composite Leading Indicator

- 목표는 특정 월의 국면 확률보다 경제활동 turning point의 조기 신호다.
- detrending, smoothing, turning-point detection과 minimum phase / cycle length를
  명시한다.
- component는 reference series 대비 lead 길이, lead 일관성, extra / missing cycle로
  평가한다.

Implication: 미래 평가는 1·2개월 class probability보다 turning-point lead, false alarm,
miss, persistence와 revision stability를 중심으로 바꾸는 편이 목적에 맞다.

## ADS / WEI

- Philadelphia Fed ADS는 mixed-frequency 실물지표로 현재 business conditions를
  real time에 추적하고 vintage를 제공한다.
- New York Fed / Dallas Fed WEI는 소비, 노동, 생산의 공통 성분을 고빈도로 추적한다.

Implication: current-state의 freshness를 개선하려면 금융가격을 current state에 섞기보다
고빈도 실물 nowcast를 별도 coincident evidence로 검토할 수 있다.
