# Inflation Policy Equity Stress Design

- 계산 identity는 `index = next-year forward EPS × forward multiple`이다.
- origin마다 당시 공개된 공식 EPS workbook vintage, 직전 시장 가격과 금리만 선택한다.
- historical label은 같은 해 마지막 거래일이고 `months_to_year_end`를 feature로 보존한다.
- 측정된 EPS revision과 사용자 AI EPS uplift를 별도 필드·별도 문구로 표시한다.
- 모델은 rolling-origin과 baseline 비교를 통과해야 확률을 공개한다.
- 공식 EPS·공동 macro path·검증 중 하나라도 부족하면 equity만 `NOT_AVAILABLE` 또는
  `LIMITED`이며 물가·정책·금리·침체 상태는 바꾸지 않는다.
