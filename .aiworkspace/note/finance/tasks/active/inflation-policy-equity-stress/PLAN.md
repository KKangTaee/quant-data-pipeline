# Inflation Policy Equity Stress Plan

## 이걸 하는 이유?

사용자가 물가·정책·10년물 경로가 S&P 500에 미치는 부담을 고정 목표가가 아니라
EPS와 valuation multiple의 조건부 범위로 판단할 수 있게 한다.

## Scope

- 공식 S&P 500 EPS release vintage와 저장 가격·금리만 사용하는 PIT panel
- 차년도 EPS 수정과 multiple 변화의 시간순 검증
- 사용자 AI EPS 가정과 사용자 지수 수준의 조건부 시나리오
- 독립 `equity_json` 저장·서비스·워크벤치 패널
- actual DB, desktop·mobile QA

## Out Of Scope

- 매수·매도·목표가·포트폴리오 지시
- 기존 경제 사이클 또는 침체 확률 재사용
- 공식 EPS 빈티지 부재를 Shiller proxy로 대체
- 5차 독립 침체 모델
