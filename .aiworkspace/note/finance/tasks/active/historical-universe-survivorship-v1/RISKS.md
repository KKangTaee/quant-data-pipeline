# Risks

- V1은 lifecycle table / loader / audit 경로를 만든다. 과거 delisting source backfill은 별도 collector task가 필요하다.
- Current NYSE snapshot만 반복 수집하면 미래 구간의 관찰 history는 쌓이지만 과거 전체 backtest 기간을 자동으로 PASS 처리할 수는 없다.
- 실제 historical source backfill 전까지 많은 과거 backtest는 survivorship `REVIEW`로 남는 것이 정상이다.
