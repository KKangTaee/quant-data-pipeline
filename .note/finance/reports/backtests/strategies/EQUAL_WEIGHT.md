# Equal Weight

## 목적

Equal Weight는 선택한 ETF 묶음을 동일 비중으로 보유하고, 지정한 주기마다 리밸런싱하는 단순 포트폴리오 전략이다.

쉽게 말하면:

- 어떤 ETF를 함께 들고 갈지 정한다.
- 각 ETF를 같은 비중으로 맞춘다.
- 6개월 또는 12개월처럼 정해진 주기마다 다시 같은 비중으로 맞춘다.

## 왜 필요한가

GTAA처럼 동적으로 자산을 갈아타는 전략만 쓰면, 특정 스타일이나 섹터 노출이 부족할 수 있다.
Equal Weight는 특정 ETF basket을 장기 보유하는 보완 sleeve로 사용해 전체 포트폴리오의 성격을 조정할 수 있다.

예를 들어:

- 성장주 / 반도체 / 에너지 / 방어 섹터 / 금을 섞어 GTAA와 다른 노출을 만든다.
- 배당 ETF를 섞어 소득형 성격을 추가한다.
- 리밸런싱 주기를 길게 둬 거래 빈도를 낮춘다.

## 현재 다시 볼 문서

- `EQUAL_WEIGHT_BACKTEST_LOG.md`
  - Equal Weight 후보 탐색과 GTAA mix 검토 결과를 누적 기록한다.

## 현재 판단 요약

- 단독 Equal Weight가 `MDD <= 15%`와 `SPY benchmark 10단계 통과`를 동시에 만족하기는 어렵다.
- 방어형 basket은 MDD가 낮지만 SPY 상대 rolling validation에서 `hold / blocked`가 되기 쉽다.
- 성장 노출을 넣으면 Real-Money gate는 통과하지만 단독 MDD가 대략 18~19%까지 올라간다.
- 따라서 GTAA와 함께 쓰는 경우에는 단독 Equal Weight MDD보다 `GTAA + Equal Weight mix`의 CAGR, MDD, Sharpe를 함께 봐야 한다.
