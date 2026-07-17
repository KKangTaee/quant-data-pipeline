# Notes

- 주식 대표값은 S&P 500 단일 지수다.
- 채권은 가격이 아니라 2년·10년·10년-2년 금리 구조로 읽는다.
- 원자재는 WTI·구리·금만 사용한다.
- EIA weekly XLS는 별도 API key 없이 내려받을 수 있고 기존 macro observation table에 저장할 수 있다.
- S&P EPS는 actual/as-reported 완료 분기만 사용하며 Shiller proxy는 이 경로에서 사용하지 않는다.
- 기간 표시는 daily 가격·금리 `1주(5거래일) / 1개월(21거래일) / 3개월(63거래일)`, EIA weekly `최근 4주 / 전년 대비`, actual EPS `완료 분기 TTM 전년 대비`로 분리한다.
- `PATHWAYS_NOT_CONNECTED` fallback은 실제 production read model에서 제거했다. 자료가 없는 개별 경로만 `UNAVAILABLE`로 격리한다.
- 서술은 함께 관찰된 측정값을 나열하며 가격 원인, 확률, 향후 가격 방향으로 확대하지 않는다.
- UI 블록은 왼쪽 강조선 없이 저채도 배경을 사용하고, desktop 자산 카드 안의 현재 움직임은 긴 단위가 깨지지 않도록 1열로 표시한다.
